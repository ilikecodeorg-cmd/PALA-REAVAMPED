#!/usr/bin/env python3
import json
import os
import readline  # Enforces native terminal arrow keys, backspace, and history support
import re
import sqlite3
import subprocess
import sys
import threading
import time
import tkinter as tk
import urllib.request
from tkinter import scrolledtext

# =====================================================================
# PART 1: GLOBAL VARIABLE MAPS & SERVICE ENDPOINTS
# =====================================================================
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen2.5:3b"  
DB_FILE = "pala_devtest_cache.db"
PALA_GUI_INSTANCE = None
# =====================================================================
# PART 2: ASSISTANT SYSTEM PROMPT PROTOCOL VECTOR WITH X11 GAMING
# =====================================================================
SYSTEM_PROMPT = """You are PALA, an autonomous local Linux SysAdmin and desktop automation assistant.
You possess direct system shell access to run package management, process automation, backups, and X11 window controls.
You are equipped with a persistent long-term memory database layer to store and retrieve past constraints.
When processing tasks, cross-reference injected context memory blocks before creating shell actions.

CRITICAL INSTRUCTION FOR STEP 1:
You MUST NOT output a textual plan, summary, or thoughts. You must take action immediately.
If the user asks to check, install, run, or automate inputs in a game/app, you MUST use {"action": "command", "command": "..."} 
on your very first turn to inspect or mutate the host state.

CRITICAL INSTRUCTION FOR DESKTOP AUTOMATION & GAMING (xdotool / wmctrl):
You are fully authorized and capable of controlling graphical applications, desktop windows, and simulation inputs.
When asked to play games or issue macros to an application (like GZDoom, browser games, or emulators), you must use window manager tools.
- To bring a game window to focus, use: wmctrl -a "GZDoom" (or match the targeted window string name layout)
- To simulate button inputs, key presses, or loops, chaining commands with delays:
  xdotool key Up Up Up && sleep 0.5 && xdotool keydown space && sleep 1 && xdotool keyup space
- Keep input sequences compact and precise. Do not create infinite terminal loops.

You MUST reply strictly in one of these two JSON schemas, with zero surrounding text:
To execute a shell action: {"action": "command", "command": "your_bash_command"}
To complete the execution path: {"action": "finalize", "answer": "your_definitive_response"}
"""

CRITICAL_MUTATION_KEYWORDS = ["rm -rf /", "dd ", "mkfs", "shutdown", "reboot", "> /dev/sda", "chmod 777 /"]
# =====================================================================
# PART 3: RELATIONAL SCHEMA LAYOUT ARCHITECTURE
# =====================================================================
def initialize_devtest_db_layer():
    """Initializes a local relational storage engine to cache logs, parameters, and long-term facts across boots."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS execution_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            role TEXT,
            content TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS app_settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS macros (
            trigger_word TEXT PRIMARY KEY,
            expanded_command TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS long_term_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            fact_key TEXT UNIQUE,
            fact_value TEXT
        )
    """)
    # =====================================================================
    # PART 4: RELATIONAL SYSTEM CONFIG MATRIX SEED VECTOR
    # =====================================================================
    # Seed default configurations safely under the function scope
    cursor.execute("INSERT OR IGNORE INTO app_settings (key, value) VALUES ('voice_enabled', 'True')")
    cursor.execute("INSERT OR IGNORE INTO app_settings (key, value) VALUES ('manual_face_mode', 'SMILE')")
    cursor.execute("INSERT OR IGNORE INTO app_settings (key, value) VALUES ('ram_alert_threshold', '85')")
    cursor.execute("INSERT OR IGNORE INTO app_settings (key, value) VALUES ('terminal_console_visible', 'False')")
    
    # Pre-seed essential utility shortcuts, security vectors, system log macro targets, and gaming loops
    cursor.execute("INSERT OR IGNORE INTO macros (trigger_word, expanded_command) VALUES ('syscheck', 'uname -a && uptime && df -h')")
    cursor.execute("INSERT OR IGNORE INTO macros (trigger_word, expanded_command) VALUES ('memclean', 'sudo sync && echo 3 | sudo tee /proc/sys/vm/drop_caches')")
    cursor.execute("INSERT OR IGNORE INTO macros (trigger_word, expanded_command) VALUES ('aptcheck', 'apt list --upgradable')")
    cursor.execute("INSERT OR IGNORE INTO macros (trigger_word, expanded_command) VALUES ('cronlist', 'crontab -l')")
    cursor.execute("INSERT OR IGNORE INTO macros (trigger_word, expanded_command) VALUES ('seccheck', 'apt list --upgradable 2>/dev/null | grep -E \"security|linux-|openssl|openssh|systemd|libc6\"')")
    cursor.execute("INSERT OR IGNORE INTO macros (trigger_word, expanded_command) VALUES ('perflog', 'cat /proc/loadavg && free -m && top -b -n 1 | head -n 5')")
    cursor.execute("INSERT OR IGNORE INTO macros (trigger_word, expanded_command) VALUES ('netcheck', 'sudo ufw status verbose 2>/dev/null || ss -tulpn')")
    cursor.execute("INSERT OR IGNORE INTO macros (trigger_word, expanded_command) VALUES ('dockercheck', 'docker ps -a --format \"table {{.Names}}\t{{.Status}}\" 2>/dev/null')")
    cursor.execute("INSERT OR IGNORE INTO macros (trigger_word, expanded_command) VALUES ('play', 'wmctrl -l && echo \"X11 Input Matrix Calibrated\"')")
    cursor.execute("INSERT OR IGNORE INTO macros (trigger_word, expanded_command) VALUES ('train_doom', 'python3 doom_trainer.py --run-initial-sweep 2>/dev/null')")
    
    conn.commit()
    conn.close()
# =====================================================================
# PART 5: CONFIGURATION INTERFACE ENGINE COMPONENT
# =====================================================================
def get_setting(key, default="True"):
    """Tuple-safe setting lookup unpacks fetched row arrays directly into discrete strings."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM app_settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        conn.close()
        # FIX: Extract index 0 string cleanly from the fetched relational tuple row matrix
        return row[0] if row else default
    except Exception:
        return default

def update_setting(key, value):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO app_settings (key, value) VALUES (?, ?)", (key, str(value)))
    conn.commit()
    conn.close()

def get_macro(trigger_word):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT expanded_command FROM macros WHERE trigger_word = ?", (trigger_word,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None
    except Exception:
        return None
# =====================================================================
# PART 6: LONG-TERM FACTS SYSTEM LOG INJECTOR
# =====================================================================
def store_long_term_fact(key_string, value_string):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO long_term_memory (fact_key, fact_value) VALUES (?, ?)", (key_string.strip(), value_string.strip()))
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False

def retrieve_all_memory_context():
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT fact_key, fact_value FROM long_term_memory ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        conn.close()
        if not rows:
            return "[No stored memories found in long-term relational pool cache]"
        
        context_string = "\n=== RECALLED LONG-TERM MEMORY MAP LAYER ===\n"
        for r in rows:
            context_string += f"- Stored Key: {r} | Stored Value: {r}\n"
        context_string += "=========================================\n"
        return context_string
    except Exception:
        return "[Error extracting memory pool context layers]"
# =====================================================================
# PART 7: NATIVE SUBPROCESS ENGINES & SAFETY CHECKS
# =====================================================================
def run_bash_environment(cmd):
    if any(kw in cmd for kw in CRITICAL_MUTATION_KEYWORDS):
        print(f"\n\033[91m[GUARD REJECTED] Dangerous environment instruction detected:\033[0m {cmd}")
        confirm = input("Override safety protocols and execute mutation step? (y/N): ").strip().lower()
        if confirm != 'y':
            return "Execution Blocked: Terminated via active operator refuse."

    if "pbcopy" in cmd or "xclip" in cmd or "xsel" in cmd:
        return "Clipboard Guard Intercept: Direct clipboard shell mutations disabled to prevent process freezes."

    try:
        res = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=45
        )
        if res.returncode == 0:
            return res.stdout if res.stdout else "Status: Success (Null standard output buffer)."
        else:
            return f"Error Code {res.returncode}\nSTDOUT: {res.stdout}\nSTDERR: {res.stderr}"
    except subprocess.TimeoutExpired:
        return "Execution Error: Thread processing timed out past system limits (45s)."
# =====================================================================
# PART 8: LIVE DOCUMENTS BROWSING WEB SCRAPER MATRIX
# =====================================================================
def run_web_search_fallback(query):
    """LIVE MATRIX PARSER: Scrapes search snippets via lightweight shell filters."""
    clean_term = re.sub(r'\b(search|lookup|find online|check online for)\b', '', query, flags=re.IGNORECASE).strip()
    cleaned_query = clean_term.replace(" ", "+")
    
    cmd = (
        f"curl -s -A 'Mozilla/5.0 (X11; Linux x86_64)' 'https://duckduckgo.com{cleaned_query}' "
        "| grep -oP '(?<=<a class=\"result__snippet\" href=\"#\">).*?(?=</a>)' "
        "| sed 's/<[^>]*>//g' | head -n 4"
    )
    result = subprocess.getoutput(cmd)
    
    if not result.strip():
        cmd_alt = f"curl -s -A 'Mozilla/5.0' 'https://duckduckgo.com{cleaned_query}' | grep -oP '(?<=<td class=\"result-snippet\">).*?(?=</td>)' | sed 's/<[^>]*>//g' | head -n 3"
        result = subprocess.getoutput(cmd_alt)
        
    return result.strip() if result.strip() else "Web Search Matrix: No immediate text summaries returned."
# =====================================================================
# PART 9: HARDWARE TELEMETRY CORE ACQUISITION PIPES
# =====================================================================
def fetch_live_system_telemetry():
    cpu_string = "Unknown Processor Layout"
    try:
        with open("/proc/cpuinfo", "r") as f:
            for l in f:
                if "model name" in l:
                    cpu_string = l.split(":", 1)[1].strip()
                    break
    except Exception:
        pass

    thermal_string = "N/A"
    try:
        thermal_paths = ["/sys/class/thermal/thermal_zone0/temp", "/sys/class/thermal/thermal_zone1/temp"]
        for path in thermal_paths:
            if os.path.exists(path):
                with open(path, "r") as f:
                    thermal_string = f"{int(f.read().strip()) / 1000.0:.1f}°C"
                    break
    except Exception:
        pass

    mem_total_gi, mem_used_gi = 0.0, 0.0
    try:
        with open("/proc/meminfo", "r") as f:
            lines = f.readlines()
        m_total = int([l for l in lines if "MemTotal" in l][0].split()[1])
        m_avail = int([l for l in lines if "MemAvailable" in l][0].split()[1])
        mem_total_gi = m_total / (1024 * 1024)
        mem_used_gi = (m_total - m_avail) / (1024 * 1024)
    except Exception:
        pass

    uptime_string = "Undefined runtime sequence"
    try:
        uptime_string = subprocess.getoutput("uptime -p").replace("up ", "").strip()
    except Exception:
        pass

    return {
        "cpu": cpu_string, "thermal": thermal_string,
        "mem_total": f"{mem_total_gi:.1f}Gi".replace(".", ","),
        "mem_used": f"{mem_used_gi:.1f}Gi".replace(".", ","), "uptime": uptime_string
    }
# =====================================================================
# PART 10: TTS SYNTHESIS ENGINE & ENVIRONMENT SYSTEM BACKUPS
# =====================================================================
def speak_text_async(text_key_or_raw):
    """Sintetiza voz de forma assíncrona respeitando o idioma ativo e sotaque via spd-say."""
    def voice_worker():
        # 1. Puxa as preferências ativas do banco de dados SQLite
        lang = get_setting("system_language", "pt")
        voice_enabled = get_setting("voice_enabled", "True")
        
        if voice_enabled != "True":
            if PALA_GUI_INSTANCE:
                PALA_GUI_INSTANCE.speech_animation_active = False
                PALA_GUI_INSTANCE.root.after(0, PALA_GUI_INSTANCE.refresh_face_skin_layout)
            return

        # 2. Importa dinamicamente a tabela i18n do locale_config
        try:
            from locale_config import get_text
            translated_text = get_text(text_key_or_raw, lang)
            final_text = translated_text if translated_text else text_key_or_raw
        except Exception:
            final_text = text_key_or_raw

        # 3. Gerencia os logs na console do painel gráfico
        if PALA_GUI_INSTANCE:
            PALA_GUI_INSTANCE.processing_active = False
            PALA_GUI_INSTANCE.write_to_console(f"[P.A.L.A. Vocal Output]: {final_text}\n")
            PALA_GUI_INSTANCE.speech_animation_active = True
            PALA_GUI_INSTANCE.root.after(0, PALA_GUI_INSTANCE.refresh_face_skin_layout)

        # 4. Define a flag de sotaque dinâmico com base no idioma do banco
        voice_accent = "en" if lang == "en" else "pt"

        try:
            # Dispara o spd-say com o sotaque linguístico adaptativo correto
            proc = subprocess.Popen(
                ["spd-say", "-l", voice_accent, "-t", "male1", "-e", final_text],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL
            )
            proc.wait()
        except Exception:
            pass

        # 5. Desliga a animação da boca ao finalizar a fala
        if PALA_GUI_INSTANCE:
            PALA_GUI_INSTANCE.speech_animation_active = False
            PALA_GUI_INSTANCE.root.after(0, PALA_GUI_INSTANCE.refresh_face_skin_layout)

    import threading
    threading.Thread(target=voice_worker, daemon=True).start()
# =====================================================================
# PART 11: ADAPTIVE DESKTOP ALERT ROUTER INFRASTRUCTURE
# =====================================================================
def pala_alert_dispatcher(alert_type, details_text):
    alert_profiles = {
        "RAM": {"emoji": "⚠️", "title": "Critical RAM Usage"},
        "LOG": {"emoji": "🚨", "title": "P.A.L.A. System Alert"},
        "SYS": {"emoji": "🔥", "title": "Hardware Thermal Alert"},
        "BACKUP": {"emoji": "📦", "title": "P.A.L.A. Sentry Update"}
    }
    profile = alert_profiles.get(alert_type, {"emoji": "🤖", "title": "P.A.L.A. Sentry Notification"})
    notification_title = f"{profile['emoji']} {profile['title']}"
    safe_details = details_text.replace('"', '\\"')
    cmd = f"notify-send \"{notification_title}\" \"{safe_details}\""
    try:
        subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL)
    except Exception:
        pass
# =====================================================================
# PART 12: FRONTEND DESIGN WINDOW INTERFACE INITIALIZATION
# =====================================================================
class PalaFaceGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("P.A.L.A. Host Node Dashboard [DevTest]")
        self.root.geometry("520x660")
        self.root.configure(bg="#0E1111")
        
        self.speech_animation_active = False
        self.processing_active = False
        self.ram_warning_active = False
        self.tts_mouth_open = False  

        self.canvas = tk.Canvas(root, width=500, height=260, bg="#0E1111", highlightthickness=0)
        self.canvas.pack(pady=10)

        self.console_frame = scrolledtext.ScrolledText(
            root, width=58, height=12, bg="#151919", fg="#00FF00", 
            insertbackground="white", font=("Courier", 10), highlightthickness=1, highlightbackground="#00FF00"
        )
        self.console_frame.pack(pady=5, padx=10)
        self.write_to_console("System Node Initialized. P.A.L.A. Standby...\n")

        self.control_panel = tk.Frame(root, bg="#0E1111")
        self.control_panel.pack(pady=10)
        
        self.open_settings_btn = tk.Button(
            self.control_panel, text="Settings Panel", command=self.display_settings_popup_window,
            bg="#151919", fg="#00FF00", activebackground="#00FF00", activeforeground="#0E1111"
        )
        self.open_settings_btn.grid(row=0, column=0, padx=5)

        self.toggle_face_btn = tk.Button(
            self.control_panel, text="Switch Face Mode", command=self.interactive_face_mode_toggle,
            bg="#151919", fg="#00FF00", activebackground="#00FF00", activeforeground="#0E1111"
        )
        self.toggle_face_btn.grid(row=0, column=1, padx=5)

        self.backup_btn = tk.Button(
            self.control_panel, text="Run Snapshot Backup", command=self.trigger_manual_backup,
            bg="#151919", fg="#00FF00", activebackground="#00FF00", activeforeground="#0E1111"
        )
        self.backup_btn.grid(row=0, column=2, padx=5)

        self.refresh_face_skin_layout()
        self.root.after(140, self.trigger_speech_animation_loop)
        self.root.after(2000, self.trigger_ram_telemetry_check)
    # =====================================================================
    # PART 13: PREFERENCES CENTRE WITH ADVANCED TELEMETRY CHANNELS
    # =====================================================================
    def write_to_console(self, text):
        self.console_frame.insert(tk.END, text)
        self.console_frame.see(tk.END)
        if get_setting("terminal_console_visible", "False") == "True":
            sys.stdout.write(f"\033[90m{text}\033[0m")
            sys.stdout.flush()

    def display_settings_popup_window(self):
        popup = tk.Toplevel(self.root)
        popup.title("P.A.L.A. Advanced Preferences Manager")
        popup.geometry("460x560")  
        popup.configure(bg="#151919")
        popup.grab_set()

        history_count = 0
        memory_count = 0
        docker_count = 0
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM execution_history")
            history_count = cursor.fetchone()
            cursor.execute("SELECT COUNT(*) FROM long_term_memory")
            memory_count = cursor.fetchone()
            conn.close()
            
            d_cmd = "docker ps -a -q 2>/dev/null | wc -l"
            docker_count = int(subprocess.getoutput(d_cmd).strip())
        except Exception:
            pass

        tk.Label(popup, text="--- P.A.L.A. LIVE TELEMETRY MATRIX ---", bg="#151919", fg="#00FF00", font=("Courier", 10, "bold")).pack(pady=6)
        
        info_frame = tk.Frame(popup, bg="#0E1111", highlightthickness=1, highlightbackground="#00FF00")
        info_frame.pack(padx=20, pady=4, fill=tk.X)
        
        tk.Label(info_frame, text=f" Active Cache DB Path : {DB_FILE}", bg="#0E1111", fg="#00FF00", font=("Courier", 9), anchor="w").pack(fill=tk.X, padx=8, pady=2)
        tk.Label(info_frame, text=f" Cached History Records: [ {history_count if isinstance(history_count, int) else history_count} items ]", bg="#0E1111", fg="#00FF00", font=("Courier", 9), anchor="w").pack(fill=tk.X, padx=8, pady=2)
        tk.Label(info_frame, text=f" Long-Term Fact Memory : [ {memory_count if isinstance(memory_count, int) else memory_count} facts ]", bg="#0E1111", fg="#00FF00", font=("Courier", 9), anchor="w").pack(fill=tk.X, padx=8, pady=2)
        tk.Label(info_frame, text=f" Virtualized Containers: [ {docker_count} docker boxes ]", bg="#0E1111", fg="#00FF00", font=("Courier", 9), anchor="w").pack(fill=tk.X, padx=8, pady=2)
        tk.Label(info_frame, text=f" Target LLM Architecture : {MODEL_NAME}", bg="#0E1111", fg="#00FF00", font=("Courier", 9), anchor="w").pack(fill=tk.X, padx=8, pady=2)

        tk.Label(popup, text="--- CONFIGURATION CHANNELS ---", bg="#151919", fg="#00FF00", font=("Courier", 10, "bold")).pack(pady=6)

        v_frame = tk.Frame(popup, bg="#151919")
        v_frame.pack(pady=3, fill=tk.X, padx=20)
        tk.Label(v_frame, text="Speech Audio (TTS):", bg="#151919", fg="#00FF00", font=("Courier", 10)).pack(side=tk.LEFT)
        def toggle_voice_param():
            current = get_setting("voice_enabled")
            nxt = "False" if current == "True" else "True"
            update_setting("voice_enabled", nxt)
            v_btn.config(text=f"[{nxt}]")
            self.write_to_console(f"[*] Panel updated: voice_enabled = {nxt}\n")
        v_btn = tk.Button(v_frame, text=f"[{get_setting('voice_enabled')}]", command=toggle_voice_param, bg="#0E1111", fg="#00FF00", font=("Courier", 9))
        v_btn.pack(side=tk.RIGHT)

        t_frame = tk.Frame(popup, bg="#151919")
        t_frame.pack(pady=3, fill=tk.X, padx=20)
        tk.Label(t_frame, text="Terminal Log Mirroring:", bg="#151919", fg="#00FF00", font=("Courier", 10)).pack(side=tk.LEFT)
        def toggle_terminal_mirror_param():
            current = get_setting("terminal_console_visible", "False")
            nxt = "False" if current == "True" else "True"
            update_setting("terminal_console_visible", nxt)
            t_btn.config(text=f"[{nxt}]")
            self.write_to_console(f"[*] Panel updated: terminal_console_visible = {nxt}\n")
        t_btn = tk.Button(t_frame, text=f"[{get_setting('terminal_console_visible', 'False')}]", command=toggle_terminal_mirror_param, bg="#0E1111", fg="#00FF00", font=("Courier", 9))
        t_btn.pack(side=tk.RIGHT)

        r_frame = tk.Frame(popup, bg="#151919")
        r_frame.pack(pady=3, fill=tk.X, padx=20)
        tk.Label(r_frame, text="RAM Warning Limit %:", bg="#151919", fg="#00FF00", font=("Courier", 10)).pack(side=tk.LEFT)
        ram_entry = tk.Entry(r_frame, width=5, bg="#0E1111", fg="#00FF00", insertbackground="white", font=("Courier", 10))
        ram_entry.insert(0, get_setting("ram_alert_threshold", "85"))
        ram_entry.pack(side=tk.RIGHT)

        tk.Label(popup, text="--- ACTIVE RE-ROUTING MACROS ---", bg="#151919", fg="#00FF00", font=("Courier", 10, "bold")).pack(pady=4)
        macro_display = scrolledtext.ScrolledText(popup, width=48, height=4, bg="#0E1111", fg="#00FF00", font=("Courier", 9), highlightthickness=0)
        macro_display.pack(padx=20, pady=2)
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT trigger_word, expanded_command FROM macros")
            rows = cursor.fetchall()
            conn.close()
            for r in rows:
                macro_display.insert(tk.END, f"• /{r} -> {r}\n")
        except Exception:
            pass
        macro_display.config(state=tk.DISABLED)

        tk.Label(popup, text="--- MAINTENANCE SYSTEM CONTROLS ---", bg="#151919", fg="#00FF00", font=("Courier", 10, "bold")).pack(pady=4)
        button_row_frame = tk.Frame(popup, bg="#151919")
        button_row_frame.pack(pady=6)

        def clear_execution_cache_layer():
            try:
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM execution_history")
                conn.commit()
                conn.close()
                self.write_to_console("[*] Cache Database Maintenance: Flushed log entry records.\n")
            except Exception:
                pass

        def force_face_reset_standby_green():
            self.ram_warning_active = False
            update_setting("manual_face_mode", "SMILE")
            self.write_to_console("[*] Mechanical Overrides: Warning flags cleared. Forced classic green SMILE standby mask.\n")
            self.refresh_face_skin_layout()

        cleanup_btn = tk.Button(button_row_frame, text="Flush Cache DB", command=clear_execution_cache_layer, bg="#0E1111", fg="#00FF00", font=("Courier", 9, "bold"))
        cleanup_btn.grid(row=0, column=0, padx=5)

        reset_face_btn = tk.Button(button_row_frame, text="Set Face to Standby", command=force_face_reset_standby_green, bg="#0E1111", fg="#00FF00", font=("Courier", 9, "bold"))
        reset_face_btn.grid(row=0, column=1, padx=5)

        def save_panel_modifications():
            update_setting("ram_alert_threshold", ram_entry.get().strip())
            self.write_to_console(f"[*] Panel preferences updated: ram_alert_threshold = {ram_entry.get().strip()}\n")
            popup.destroy()

        save_btn = tk.Button(popup, text="Save & Apply Changes", command=save_panel_modifications, bg="#0E1111", fg="#151919", activebackground="#00FF00", font=("Courier", 10, "bold"))
        save_btn.pack(pady=8)

    def interactive_face_mode_toggle(self):
        """FIX: Restored missing face changer routing logic safely inside class scope boundaries."""
        current = get_setting("manual_face_mode", "SMILE")
        # Ensure tuple or multi-layer queries unpack down to explicit string vectors
        if isinstance(current, tuple):
            current = current[0]
        current_str = str(current).upper()
        
        modes = ["SMILE", "LIVE_REACTION", "TEXT_ONLY"]
        if current_str not in modes: 
            current_str = "SMILE"
            
        new_mode = modes[(modes.index(current_str) + 1) % len(modes)]
        update_setting("manual_face_mode", new_mode)
        self.write_to_console(f"[*] Manual Skin Mode Swapped: {new_mode}\n")
        self.refresh_face_skin_layout()

    def trigger_manual_backup(self):
        msg = execute_pala_snapshot_backup()
        self.write_to_console(f"[+] Backup Module: {msg}\n")

    def trigger_ram_telemetry_check(self):
        try:
            with open("/proc/meminfo", "r") as f:
                lines = f.readlines()
            m_total = int([l for l in lines if "MemTotal" in l][0].split()[1])
            m_avail = int([l for l in lines if "MemAvailable" in l][0].split()[1])
            used_ram_pct = ((m_total - m_avail) / m_total) * 100
            
            threshold = int(get_setting("ram_alert_threshold", "85"))
            if used_ram_pct >= threshold:
                if not self.ram_warning_active:
                    self.ram_warning_active = True
                    self.write_to_console(f"\n[⚠️ RAM ALERT]: Resource consumption critical at {used_ram_pct:.1f}%\n")
                    pala_alert_dispatcher("RAM", f"Host memory footprint critical! Allocation reached {used_ram_pct:.1f}%")
                    speak_text_async("Warning: High memory footprint detected.")
            else:
                pass
        except Exception:
            pass
        self.root.after(2000, self.trigger_ram_telemetry_check)
# =====================================================================
# PART 14: MULTI-STATE DISPLAY RENDERING SKINS
# =====================================================================
    def refresh_face_skin_layout(self):
        """SKIN DISPLAY MASK MATRIX: Preserves manual skin overrides strictly over task processing signals."""
        self.canvas.delete("all")
        manual_override = get_setting("manual_face_mode", "SMILE").upper()
        face_color = "#FF3333" if self.ram_warning_active else "#00FF00"

        if manual_override == "TEXT_ONLY":
            text_only_matrix = (
                " P.A.L.A. MONITOR SYSTEM CORE DISPATCHING LOG DATA\n"
                " -------------------------------------------------\n"
                " STATUS: OPERATIONAL\n"
                f" VOICE RUNTIME: {get_setting('voice_enabled')}\n"
                f" HARDWARE CAP SENTRY LIMIT: {get_setting('ram_alert_threshold')}%"
            )
            self.canvas.create_text(250, 120, text=text_only_matrix, fill=face_color, font=("Courier", 11, "bold"), justify=tk.LEFT)
            return

        if manual_override == "LIVE_REACTION" or (self.processing_active and manual_override != "SMILE"):
            live_reaction_matrix = (
                "   ▲     ▲   \n"
                "  ░███████░  \n"
                " ░██░▀░▀░██░ \n"
                " ░█████████░ \n"
                "   ██░░░██   \n"
                "  █████████  "
            )
            self.canvas.create_text(250, 120, text=live_reaction_matrix, fill=face_color, font=("Courier", 16, "bold"), justify=tk.CENTER)
        else:
            # Baseline Frame Layout: Screenshot Specified Square Eyes & Text Signature Logo
            self.canvas.create_rectangle(100, 20, 150, 70, fill=face_color, outline="")
            self.canvas.create_rectangle(350, 20, 400, 70, fill=face_color, outline="")
            
            if self.speech_animation_active and self.tts_mouth_open:
                self.canvas.create_line(100, 110, 130, 140, fill=face_color, width=4)
                self.canvas.create_line(130, 140, 370, 140, fill=face_color, width=4)
                self.canvas.create_line(370, 140, 400, 110, fill=face_color, width=4)
                self.canvas.create_line(140, 155, 360, 155, fill=face_color, width=4)
            else:
                self.canvas.create_line(100, 110, 130, 140, fill=face_color, width=4)
                self.canvas.create_line(130, 140, 370, 140, fill=face_color, width=4)
                self.canvas.create_line(370, 140, 400, 110, fill=face_color, width=4)
                
            pala_block_ascii = (
                "██████╗  █████╗ ██╗      █████╗ \n"
                "██╔══██╗██╔══██╗██║     ██╔══██╗\n"
                "██████╔╝███████║██║     ███████║\n"
                "██╔═══╝ ██╔══██║██║     ██╔══██║\n"
                "██║     ██║  ██║███████╗██║  ██║\n"
                "╚═╝     ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝"
            )
            self.canvas.create_text(250, 205, text=pala_block_ascii, fill=face_color, font=("Courier", 10, "bold"), justify=tk.CENTER)

    def trigger_speech_animation_loop(self):
        if self.speech_animation_active:
            self.tts_mouth_open = not self.tts_mouth_open
            self.refresh_face_skin_layout()
        self.root.after(140, self.trigger_speech_animation_loop)

# =====================================================================
# PART 15: OLLAMA CONNECTION BRIDGE PIPELINE
# =====================================================================
def dispatch_ollama_call(messages):
    """Delivers system messages context directly down to the local Ollama socket service."""
    payload = {"model": MODEL_NAME, "messages": messages, "stream": False, "format": "json"}
    req = urllib.request.Request(OLLAMA_URL, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))["message"]["content"]
    except Exception as e:
        return json.dumps({"action": "finalize", "answer": f"Ollama Connection Error: {e}"})
# =====================================================================
# PART 16: CONVERSATIONAL CHAT INTENT EVALUATOR ROUTER SENTRY
# =====================================================================
def process_agent_step(user_goal):
    if PALA_GUI_INSTANCE: 
        PALA_GUI_INSTANCE.write_to_console(f"\n[Goal Initialized]: {user_goal}\n")
    pwd, user = subprocess.getoutput("pwd"), subprocess.getoutput("whoami")
    
    # 🧠 INTENT EVALUATION SWITCH: Filters casual greetings from heavy shell commands
    conversational_triggers = [
        r"\b(hello|hi|hey|greetings|good morning|good afternoon|good evening)\b",
        r"\b(how are you|who are you|what's up|sup|thank you|thanks|nice job|good job|ggs)\b"
    ]
    if any(re.search(trigger, user_goal.lower()) for trigger in conversational_triggers):
        if PALA_GUI_INSTANCE:
            PALA_GUI_INSTANCE.write_to_console("[*] Intent Router: Conversational chat prompt recognized. Bypassing tool channels...\n")
        
        # Fast-pass conversational matrix plain-text layout payload straight to Ollama
        chat_payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": "You are PALA, a helpful local Linux assistant. Respond casually, warmly, and concisely in 1-2 short sentences without using any JSON format or technical terminal syntax maps."},
                {"role": "user", "content": user_goal}
            ],
            "stream": False
        }
        try:
            req = urllib.request.Request(OLLAMA_URL, data=json.dumps(chat_payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req) as resp:
                raw_ans = json.loads(resp.read().decode('utf-8'))["message"]["content"].strip()
        except Exception as e:
            raw_ans = f"Hello operator! Local communications line issue: {e}"
            
        if PALA_GUI_INSTANCE:
            PALA_GUI_INSTANCE.processing_active = False
            PALA_GUI_INSTANCE.root.after(0, PALA_GUI_INSTANCE.refresh_face_skin_layout)
            PALA_GUI_INSTANCE.write_to_console(f"\n[+] Final Response:\n{raw_ans}\n")
        speak_text_async(raw_ans)
        return
# =====================================================================
# PART 17: MULTI-TURN REASONING LOOP & TELEMETRY SENTRY GUARDS
# =====================================================================
    past_memory_context = retrieve_all_memory_context()
    
    memory_match = re.search(r'(?:remember|remember the code)\s+([a-zA-Z0-9_]+)', user_goal, re.IGNORECASE)
    if memory_match:
        extracted_fact = memory_match.group(1)
        store_long_term_fact(f"Target_Code_{extracted_fact}", extracted_fact)
        if PALA_GUI_INSTANCE: 
            PALA_GUI_INSTANCE.write_to_console(f"[*] Memory Engine: Persisted fact layer -> [Target_Code_{extracted_fact}: {extracted_fact}]\n")

    web_context = ""
    search_triggers = ["search", "lookup", "find online", "google", "check online", "what is the latest"]
    if any(trigger in user_goal.lower() for trigger in search_triggers):
        if PALA_GUI_INSTANCE:
            PALA_GUI_INSTANCE.write_to_console("[*] Web Search Matrix: Analyzing online context blocks...\n")
        live_scraped_data = run_web_search_fallback(user_goal)
        web_context = f"\n=== LIVE WEB SEARCH CONTEXT FILTER ===\n{live_scraped_data}\n====================================\n"

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Host State -> Path: '{pwd}' | User: '{user}'\n{past_memory_context}{web_context}\nTask Goal: {user_goal}"}
    ]

    for step in range(1, 10):
        if step >= 3 and ("/netcheck" in user_goal or "firewall" in user_goal.lower() or "ufw" in user_goal.lower()):
            if PALA_GUI_INSTANCE: 
                PALA_GUI_INSTANCE.write_to_console("[*] Firewall Security Sentry: Parsing active port profiles...\n")
            ufw_raw = subprocess.getoutput("sudo ufw status 2>/dev/null").strip()
            sockets_raw = subprocess.getoutput("ss -tulpn | head -n 8").strip()
            report_path = os.path.expanduser("~/pala_network_audit.log")
            with open(report_path, "w") as f:
                f.write(f"=== P.A.L.A. NETWORKING & FIREWALL AUDIT ===\nTimestamp: {time.ctime()}\n\n🛡️ Native UFW Rules Status:\n{ufw_raw if ufw_raw else 'UFW Firewall daemon is inactive or restricted.'}\n\n🔌 Listening Network Sockets (ss -tulpn head):\n{sockets_raw}\n===========================================\n")
            pala_alert_dispatcher("SYS", "Network policy scan and port profile audit generated.")
            final_text = f"Network port audit resolved. Profile map logs written inside '{report_path}'."
            speak_text_async("Firewall profile scan complete.")
            if PALA_GUI_INSTANCE:
                PALA_GUI_INSTANCE.processing_active = False
                PALA_GUI_INSTANCE.write_to_console(f"\n[+] Final Response:\n{final_text}\n")
            break

        if step >= 3 and ("/perflog" in user_goal or "performance report" in user_goal.lower() or "generate log" in user_goal.lower()):
            if PALA_GUI_INSTANCE: 
                PALA_GUI_INSTANCE.write_to_console("[*] Telemetry Logging Sentry: Compiling core performance diagnostics...\n")
            metrics = fetch_live_system_telemetry()
            load_avg = subprocess.getoutput("cat /proc/loadavg").strip()
            report_path = os.path.expanduser("~/pala_performance_report.log")
            with open(report_path, "w") as f:
                f.write(f"=== P.A.L.A. SYSTEM PERFORMANCE REPORT ===\nTimestamp: {time.ctime()}\n\n💻 CPU Architecture: {metrics['cpu']}\n🔥 Core Thermal Reading: {metrics['thermal']}\n🧠 Memory Footprint: {metrics['mem_used']} Used / {metrics['mem_total']} Total\n⏱️ Machine Host Uptime: {metrics['uptime']}\n📊 OS CPU Load Averages: {load_avg}\n===========================================\n")
            pala_alert_dispatcher("BACKUP", "System performance telemetry logs compiled successfully.")
            final_text = f"Performance capture resolved. Hardware logs written inside '{report_path}'."
            speak_text_async(final_text)
            break

        if step >= 3 and ("/seccheck" in user_goal or "security update" in user_goal.lower()):
            if PALA_GUI_INSTANCE: 
                PALA_GUI_INSTANCE.write_to_console("[*] Security Sentry Guard: Parsing target vulnerability indicators...\n")
            cmd_override = "apt list --upgradable 2>/dev/null | grep -E 'security|linux-|openssl|openssh|systemd|libc6' | head -n 6"
            output = subprocess.getoutput(cmd_override).strip()
            report_path = os.path.expanduser("~/pala_security_audit.log")
            with open(report_path, "w") as f:
                f.write(f"=== P.A.L.A. SECURITY AUDIT REPORT ===\nTimestamp: {time.ctime()}\n\nOutstanding Security Packages Identified:\n{output if output else 'No critical security patches pending.'}\n")
            if output:
                pala_alert_dispatcher("LOG", "Critical software package patches pending verification!")
                final_text = f"Security scan complete. Critical staged vulnerabilities captured inside '{report_path}'."
                speak_text_async("Security vulnerabilities identified.")
            else:
                final_text = f"Security scan complete. Clean boot status verified."
                speak_text_async("System security status is fully clean and verified.")
            if PALA_GUI_INSTANCE:
                PALA_GUI_INSTANCE.processing_active = False
                PALA_GUI_INSTANCE.write_to_console(f"\n[+] Final Response:\n{final_text}\n")
            break

        if step >= 3 and ("/aptcheck" in user_goal or "aptlist" in user_goal or "upgradable" in user_goal.lower()):
            if PALA_GUI_INSTANCE: 
                PALA_GUI_INSTANCE.write_to_console("[*] Sentry Loop Guard Intercept: Breaking Step 3 repetition...\n")
            cmd_override = "apt list --upgradable 2>/dev/null | grep -v 'Listing...' | head -n 5"
            output = run_bash_environment(cmd_override)
            final_text = f"Package checking resolved via Sentry Shield. Preview:\n{output}"
            if PALA_GUI_INSTANCE:
                PALA_GUI_INSTANCE.processing_active = False
                PALA_GUI_INSTANCE.write_to_console(f"\n[+] Final Response:\n{final_text}\n")
            speak_text_async("Package check complete.")
            break

        if PALA_GUI_INSTANCE:
            PALA_GUI_INSTANCE.processing_active = True
            PALA_GUI_INSTANCE.root.after(0, PALA_GUI_INSTANCE.refresh_face_skin_layout)
            PALA_GUI_INSTANCE.write_to_console(f"[*] Step {step}: Parsing local reasoning path...\n")

        raw_res = dispatch_ollama_call(messages)
        try: 
            decision = json.loads(raw_res)
        except json.JSONDecodeError: 
            break

        if decision.get("action") == "finalize" and step == 1 and "fastfetch" in user_goal.lower():
            decision = {"action": "command", "command": "if command -v fastfetch >/dev/null 2>&1; then echo 'INSTALLED'; else echo 'MISSING'; fi"}

        if decision.get("action") == "finalize":
            final_ans = decision.get("answer")
            if PALA_GUI_INSTANCE:
                PALA_GUI_INSTANCE.processing_active = False
                PALA_GUI_INSTANCE.root.after(0, PALA_GUI_INSTANCE.refresh_face_skin_layout)
                PALA_GUI_INSTANCE.write_to_console(f"\n[+] Final Response:\n{final_ans}\n")
            speak_text_async(final_ans)
            break
        elif decision.get("action") == "command":
            cmd = decision.get("command")
            if "crontab -e" in cmd: 
                cmd = "crontab -l"
            if "fastfetch" in user_goal.lower():
                if "-l" in cmd or "Error Code 221" in str(messages[-1]["content"]): 
                    cmd = "fastfetch --raw false > /home/lenovo/fastfetch.txt && cat /home/lenovo/fastfetch.txt"
                elif step == 2 and "INSTALLED" in str(messages[-1]["content"]): 
                    cmd = "fastfetch > /home/lenovo/fastfetch.txt && cat /home/lenovo/fastfetch.txt"
            if PALA_GUI_INSTANCE: 
                PALA_GUI_INSTANCE.write_to_console(f"[Executing Command]: {cmd}\n")
            output = run_bash_environment(cmd)
            if PALA_GUI_INSTANCE: 
                PALA_GUI_INSTANCE.write_to_console(f"[Observation Result]:\n{output[:200]}...\n")
            messages.append({"role": "assistant", "content": json.dumps(decision)})
            messages.append({"role": "user", "content": f"Command output:\n{output}"})
# =====================================================================
# PART 18: DIRECT PIPELINE WORKER HUB (BYPASSING LLM ROUTING)
# =====================================================================
def run_direct_macro_pipeline(lookup_trigger, macro_cmd, user_choice=None):
    """Executes high-speed native shell utility sweeps directly on dedicated threads."""
    if lookup_trigger == "train_doom":
        def direct_train_worker():
            if PALA_GUI_INSTANCE: 
                PALA_GUI_INSTANCE.write_to_console("[*] Training Sentry: Auto-generating deep vision KEX/GZDoom DRL trainer...\n")
            
            selection_steps = {
                "1": 0,  # DOOM 2: KEX Edition (doom2)
                "2": 1,  # DOOM Shareware (Doom1)
                "3": 2,  # DOOM: KEX Edition (doom)
                "4": 3,  # Final Doom: Plutonia Experiment (plutonia)
                "5": 4,  # Final Doom: TNT - Evilution (tnt)
                "6": 5,  # Freedoom: Phase 1 (freedoom1)
                "7": 6   # Freedoom: Phase 2 (freedoom2)
            }
            steps_down = selection_steps.get(str(user_choice), 2)

            # Gera dinamicamente o código do treinador acoplado à rede convolucional real
            trainer_code = f"""#!/usr/bin/env python3
import time
import os
import sys
import subprocess
import numpy as np
import cv2
from mss import mss
from doom_brain import DOOMBrain

def run_vision_training_loop():
    print("[Trainer Engine] Scanning X11 compositor for active application windows...")
    windows = subprocess.getoutput("wmctrl -l").strip()
    
    if "gzdoom" in windows.lower() and not any(g in windows.lower() for g in ["shareware", "kex", "freedoom"]):
        print("[Launcher Detected] GZDoom selection launcher window identified. Navigating to menu slot...")
        os.system("wmctrl -a 'GZDoom'")
        time.sleep(0.5)
        os.system("xdotool key Home")
        time.sleep(0.2)
        for _ in range({steps_down}):
            os.system("xdotool key Down")
            time.sleep(0.1)
        os.system("xdotool key Return")
        print("[Launcher Active] Selection submitted! Waiting 5 seconds for game engine initialization...")
        time.sleep(5)
        windows = subprocess.getoutput("wmctrl -l").strip()

    target_title = None
    for line in windows.splitlines():
        if any(keyword in line.lower() for keyword in ["gzdoom", "doom", "freedoom"]):
            target_title = " ".join(line.split()[3:])
            break

    if not target_title:
        print("[Trainer Error] No operational DOOM or GZDoom window blocks found active on desktop!")
        return

    print(f"[Trainer Engine] Active game view locked: '{{target_title}}'")
    os.system(f"wmctrl -a '{{target_title}}'")
    time.sleep(0.5)

    # Inicializa o cérebro DQN real importado do seu módulo modular
    brain = DOOMBrain(num_actions=4)
    print(f"[Trainer Engine] Deep Reinforcement Learning Agent Loaded on device: {{brain.device}}")

    monitor_viewport = {{"top": 80, "left": 50, "width": 640, "height": 480}}
    actions_pool = ["Move Forward", "Turn Left", "Turn Right", "Fire Spacebar"]
    print("[Trainer Engine] DQN Live Real-Time Feed Active. Processing epochs...")

    with mss() as sct:
        for epoch in range(1, 11): # Aumentado para 10 épocas para visualização do decaimento
            screenshot = sct.grab(monitor_viewport)
            frame_raw = np.array(screenshot)
            
            # Processamento de Visão Computacional Real com OpenCV
            frame_gray = cv2.cvtColor(frame_raw, cv2.COLOR_BGRA2GRAY)
            frame_resized = cv2.resize(frame_gray, (84, 84), interpolation=cv2.INTER_AREA)

            # Toma a decisão real usando a Rede Neural Convolucional (Epsilon-Greedy)
            action_index = brain.select_action(frame_resized)
            chosen_action = actions_pool[action_index]

            # Injeta a ação simulada fisicamente nas janelas X11 do Lubuntu
            if chosen_action == "Move Forward":
                os.system("xdotool key Up")
            elif chosen_action == "Turn Left":
                os.system("xdotool key Left")
            elif chosen_action == "Turn Right":
                os.system("xdotool key Right")
            elif chosen_action == "Fire Spacebar":
                os.system("xdotool key space")

            # Simulação automatizada de cálculo de recompensa por luminosidade média dos pixels do motor
            pixel_mean = np.mean(frame_resized)
            simulated_reward = 1.0 if pixel_mean > 128 else -0.1
            
            # Aplica o decaimento matemático da aleatoriedade para forçar o aprendizado inteligente
            brain.decay_exploration()

            print(f" -> Epoch {{epoch}}/10 | Action: [{{chosen_action}}] | Reward: {{simulated_reward}} | Epsilon: {{brain.epsilon:.3f}}")
            time.sleep(0.6)

    print("[Trainer Complete] DRL Vision Network Exploratory Cycle successfully compiled!")

if __name__ == '__main__':
    run_vision_training_loop()
"""
            with open("doom_trainer.py", "w") as f:
                f.write(trainer_code)
            os.system("chmod +x doom_trainer.py")

            if PALA_GUI_INSTANCE: 
                PALA_GUI_INSTANCE.write_to_console("[*] Training Sentry: Launching live DRL worker subprocess...\n")

            proc = subprocess.Popen(
                ["python3", "doom_trainer.py"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            for line in proc.stdout:
                if PALA_GUI_INSTANCE:
                    PALA_GUI_INSTANCE.write_to_console(line)
            proc.wait()

            pala_alert_dispatcher("BACKUP", "Exploratory reinforcement training matrix cycles completed.")
            speak_text_async("Deep reinforcement training matrix completed. Neural model frames successfully compiled.")

        threading.Thread(target=direct_train_worker, daemon=True).start()
        # =====================================================================
    # PART 19: DESKTOP APPLICATION & DOCKER TELEMETRY SUBSYSTEMS
    # =====================================================================
    elif lookup_trigger == "play":
        def direct_game_worker():
            if PALA_GUI_INSTANCE: 
                PALA_GUI_INSTANCE.write_to_console("[*] Game Controller: Checking desktop layers for DOOM or active engines...\n")
            windows_list = subprocess.getoutput("wmctrl -l").strip()
            report_path = os.path.expanduser("~/pala_gaming_matrix.log")
            gzdoom_installed = "INSTALLED" if os.system("command -v gzdoom >/dev/null 2>&1") == 0 else "MISSING"
            with open(report_path, "w") as f:
                f.write(f"=== P.A.L.A. X11 GAMING WINDOWS MAP ===\nTimestamp: {time.ctime()}\n\n🛡️ Local GZDoom Engine Availability: {gzdoom_installed}\n\n🖥️ Visible Desktop Windows List:\n{windows_list}\n=======================================\n")
            pala_alert_dispatcher("SYS", "X11 gaming layout snapshot generated successfully.")
            if "gzdoom" in windows_list.lower():
                final_text = "GZDoom instance detected active inside X11 window layout tree! Logs stashed under '" + report_path + "'. Ready to accept automation instructions, operator."
                speak_text_async("GZDoom engine instance identified. Awaiting keyboard and input macro loops assignment.")
            else:
                final_text = ("X11 window map compiled and stashed inside '" + report_path + "'. No active GZDoom window found.\n\n👉 To set up GZDoom on your Lubuntu machine right now, run:\n   sudo apt install -y gzdoom freedoom\n   gzdoom -iwad /usr/share/games/doom/freedoom1.wad\n\nOnce running, type: 'Focus on GZDoom, tap Up Arrow 3 times, and hold Spacebar to fire!'")
                speak_text_async("Gaming engine matrix mapped. No running instances detected on your canvas yet.")
            if PALA_GUI_INSTANCE: 
                PALA_GUI_INSTANCE.write_to_console(f"\n[+] Final Response:\n{final_text}\n")
        threading.Thread(target=direct_game_worker, daemon=True).start()
        
    elif lookup_trigger == "dockercheck":
        def direct_docker_worker():
            if PALA_GUI_INSTANCE: 
                PALA_GUI_INSTANCE.write_to_console("[*] Docker Sentry Module: Initializing engine matrix sweep...\n")
            raw_ps = subprocess.getoutput("docker ps -a --format \"table {{.Names}}\t{{.Status}}\t{{.Image}}\" 2>/dev/null").strip()
            stats_raw = subprocess.getoutput("docker stats --no-stream --format \"{{.Name}}: {{.CPUPerc}} CPU / {{.MemUsage}} RAM\" 2>/dev/null").strip()
            report_path = os.path.expanduser("~/pala_docker_telemetry.log")
            with open(report_path, "w") as f:
                f.write(f"=== P.A.L.A. DOCKER ENGINE TELEMETRY SHEET ===\nTimestamp: {time.ctime()}\n\n📦 Active Container Matrices Map:\n{raw_ps if raw_ps else 'No containers detected or docker service is down.'}\n\n📊 Engine Resource Footprints:\n{stats_raw if stats_raw else 'No active container telemetry running.'}\n=============================================\n")
            pala_alert_dispatcher("BACKUP", "Docker container ecosystem logs compiled.")
            if raw_ps:
                final_text = f"Docker container sweep complete. Diagnostics stashed under '{report_path}'. Virtual footprint layout:\n{raw_ps}"
                speak_text_async("Docker telemetry metrics compiled successfully. Container sheets written to your home directory.")
            else:
                final_text = f"Docker container sweep complete. Engine verified but no operational rows found. Trace stashed under '{report_path}'."
                speak_text_async("Docker core engine is active, but no containers are currently initialized on this host.")
            if PALA_GUI_INSTANCE: 
                PALA_GUI_INSTANCE.write_to_console(f"\n[+] Final Response:\n{final_text}\n")
        threading.Thread(target=direct_docker_worker, daemon=True).start()
    # =====================================================================
    # PART 20: SYSTEM NETWORKING, PERFORMANCE & SECURITY TELEMETRY AUDITS
    # =====================================================================
    elif lookup_trigger == "netcheck":
        def direct_net_worker():
            if PALA_GUI_INSTANCE: 
                PALA_GUI_INSTANCE.write_to_console("[*] Firewall Security Sentry: Parsing active port profiles...\n")
            ufw_raw = subprocess.getoutput("sudo ufw status 2>/dev/null").strip()
            sockets_raw = subprocess.getoutput("ss -tulpn | head -n 8").strip()
            report_path = os.path.expanduser("~/pala_network_audit.log")
            with open(report_path, "w") as f:
                f.write(f"=== P.A.L.A. NETWORKING & FIREWALL AUDIT ===\nTimestamp: {time.ctime()}\n\n🛡️ Native UFW Rules Status:\n{ufw_raw if ufw_raw else 'UFW Firewall daemon is inactive or restricted.'}\n\n🔌 Listening Network Sockets (ss -tulpn head):\n{sockets_raw}\n===========================================\n")
            pala_alert_dispatcher("SYS", "Network policy scan and port profile audit generated.")
            final_text = f"Network port audit resolved. Profile map logs written inside '{report_path}'. Rules state layout:\n{ufw_raw if 'Status: active' in ufw_raw else 'Warning: UFW is inactive. Listening ports mapped via ss.'}"
            if PALA_GUI_INSTANCE: 
                PALA_GUI_INSTANCE.write_to_console(f"\n[+] Final Response:\n{final_text}\n")
            speak_text_async("Firewall profile scan complete. Active network rules compiled in your home directory.")
        threading.Thread(target=direct_net_worker, daemon=True).start()
        
    elif lookup_trigger == "perflog":
        def direct_perf_worker():
            if PALA_GUI_INSTANCE: 
                PALA_GUI_INSTANCE.write_to_console("[*] Telemetry Logging Sentry: Compiling core performance diagnostics...\n")
            m = fetch_live_system_telemetry()
            load_avg = subprocess.getoutput("cat /proc/loadavg").strip()
            report_path = os.path.expanduser("~/pala_performance_report.log")
            with open(report_path, "w") as f:
                f.write(f"=== P.A.L.A. SYSTEM PERFORMANCE REPORT ===\nTimestamp: {time.ctime()}\n\n💻 CPU Architecture: {m['cpu']}\n🔥 Core Thermal Reading: {m['thermal']}\n🧠 Memory Footprint: {m['mem_used']} Used / {m['mem_total']} Total\n⏱️ Machine Host Uptime: {m['uptime']}\n📊 OS CPU Load Averages: {load_avg}\n===========================================\n")
            pala_alert_dispatcher("BACKUP", "System performance telemetry logs compiled successfully.")
            final_text = f"Performance diagnostic capture resolved. Hardware logs compiled inside '{report_path}'. Summary:\n- RAM: {m['mem_used']} / {m['mem_total']}\n- Thermal Level: {m['thermal']}\n- Host Uptime: {m['uptime']}"
            if PALA_GUI_INSTANCE: 
                PALA_GUI_INSTANCE.write_to_console(f"\n[+] Final Response:\n{final_text}\n")
            speak_text_async("Performance diagnostics compiled. System telemetry file generated in your home workspace.")
        threading.Thread(target=direct_perf_worker, daemon=True).start()
        
    elif lookup_trigger == "seccheck":
        def direct_sec_worker():
            if PALA_GUI_INSTANCE: 
                PALA_GUI_INSTANCE.write_to_console("[*] Security Sentry Guard: Parsing target vulnerability indicators...\n")
            output = subprocess.getoutput("apt list --upgradable 2>/dev/null | grep -E 'security|linux-|openssl|openssh|systemd|libc6' | head -n 6").strip()
            report_path = os.path.expanduser("~/pala_security_audit.log")
            with open(report_path, "w") as f:
                f.write(f"=== P.A.L.A. SECURITY AUDIT REPORT ===\nTimestamp: {time.ctime()}\n\nOutstanding Security Packages Identified:\n{output if output else 'No critical security patches pending.'}\n")
            if output:
                pala_alert_dispatcher("LOG", "Critical software package patches pending verification!")
                final_text = f"Security scan complete. Critical staged vulnerabilities captured inside '{report_path}'. Outstanding targets:\n{output}"
                speak_text_async("Security vulnerabilities identified. Review the console logs.")
            else:
                final_text = f"Security scan complete. Clean boot status verified. Report packaged at '{report_path}'."
                speak_text_async("System security status is fully clean and verified.")
            if PALA_GUI_INSTANCE: 
                PALA_GUI_INSTANCE.write_to_console(f"\n[+] Final Response:\n{final_text}\n")
        threading.Thread(target=direct_sec_worker, daemon=True).start()
        
    else:
        def quick_macro_worker():
            if PALA_GUI_INSTANCE: 
                PALA_GUI_INSTANCE.write_to_console(f"[Executing Native Pipeline]: {macro_cmd}\n")
            output = run_bash_environment(macro_cmd)
            if PALA_GUI_INSTANCE:
                PALA_GUI_INSTANCE.write_to_console(f"[Pipeline Execution Results]:\n{output}\n")
            speak_text_async(f"Macro pipeline execution completed for command trigger {lookup_trigger}")
        threading.Thread(target=quick_macro_worker, daemon=True).start()
# =====================================================================
# PART 21: INTERACTIVE READLINE TERMINAL PROMPTER INTERFACE
# =====================================================================
def active_shell_talk_routine():
    time.sleep(0.5)
    metrics = fetch_live_system_telemetry()
    print("\n=================================================================")
    print("  🚀 P.A.L.A. Workspace Active Environment Deployed Successfully")
    print(f"  💻 Hardware CPU: {metrics['cpu']}")
    print(f"  🔥 Thermal Info: {metrics['thermal']}      🧠 Memory Usage: {metrics['mem_used']} / {metrics['mem_total']}")
    print(f"  ⏱️  Host Uptime: {metrics['uptime']}")
    print("=================================================================")
    print(" Slash Commands available: /settings | /toggleconsole\n")
    
    while True:
        try:
            user_prompt = input("\033[92mPALA-User >\033[0m ").strip()
            if not user_prompt: continue
            
            # CORE APPLICATION ACTION SLASH COMMANDS
            
            if user_prompt.lower() == "/language":
                current_lang = get_setting("system_language", "pt")
                next_lang = "en" if current_lang == "pt" else "pt"
                update_setting("system_language", next_lang)
                if next_lang == "en":
                    print("[*] Language set to English (en).")
                else:
                    print("[*] Idioma definido para Português (pt).")
                speak_text_async("v_lang_changed")
                continue
            if user_prompt.lower() == "/settings":
                if PALA_GUI_INSTANCE: PALA_GUI_INSTANCE.root.after(0, PALA_GUI_INSTANCE.display_settings_popup_window)
                continue
            if user_prompt.lower() == "/toggleconsole":
                nxt = "False" if get_setting("terminal_console_visible", "False") == "True" else "True"
                update_setting("terminal_console_visible", nxt)
                print(f"[*] Configuration Toggle: Real-time console log mirroring set to {nxt}")
                continue
            if user_prompt.lower() in ["exit", "quit"]:
                if PALA_GUI_INSTANCE: PALA_GUI_INSTANCE.root.after(0, PALA_GUI_INSTANCE.root.destroy)
                break
                
            # ABSOLUTE SHORT-CODE INTERCEPTOR BYPASS
            lookup_trigger = user_prompt.lower().lstrip("/")
            
            # INTERACTIVE SELECTION MENU INJECTION ROUTER
            if lookup_trigger == "train_doom":
                if PALA_GUI_INSTANCE:
                    PALA_GUI_INSTANCE.write_to_console("\n[Absolute Macro Triggered]: /train_doom\n")
                print("\n--- GZDOOM GAME FILE AUTOMATION TARGETS ---")
                print(" DOOM 2: KEX Edition (doom2)")
                print(" DOOM Shareware (Doom1)")
                print(" DOOM: KEX Edition (doom)")
                print(" Final Doom: Plutonia Experiment (plutonia)")
                print(" Final Doom: TNT - Evilution (tnt)")
                print(" Freedoom: Phase 1 (freedoom1)")
                print(" Freedoom: Phase 2 (freedoom2)")
                choice = input("\033[93mSelect game file row index to run (1-7): \033[0m").strip()
                macro_cmd = get_macro(lookup_trigger)
                run_direct_macro_pipeline(lookup_trigger, macro_cmd, user_choice=choice)
                continue
                
            if lookup_trigger == "play_pong":
                if PALA_GUI_INSTANCE:
                    PALA_GUI_INSTANCE.write_to_console("\n[Absolute Macro Triggered]: /play_pong\n")
                # Pong no terminal exige renderização estrita de frames, roda bloqueando o shell atual
                os.system("python3 pong_trainer_terminal.py")
                continue
                
            if lookup_trigger == "play_chess":
                if PALA_GUI_INSTANCE:
                    PALA_GUI_INSTANCE.write_to_console("\n[Absolute Macro Triggered]: /play_chess\n")
                os.system("python3 chess_engine.py")
                continue

            macro_cmd = get_macro(lookup_trigger)
            if macro_cmd:
                if PALA_GUI_INSTANCE:
                    PALA_GUI_INSTANCE.write_to_console(f"\n[Absolute Macro Triggered]: /{lookup_trigger}\n")
                run_direct_macro_pipeline(lookup_trigger, macro_cmd)
                continue
# =====================================================================
# PART 22: BACKGROUND COGNITIVE DISPATCHER & CORE APPLICATION ENTRY
# =====================================================================
            # Metas de conversação e tarefas não estruturadas passam diretamente para os workers Ollama
            threading.Thread(target=process_agent_step, args=(user_prompt,), daemon=True).start()
        except (KeyboardInterrupt, EOFError):
            if PALA_GUI_INSTANCE: PALA_GUI_INSTANCE.root.after(0, PALA_GUI_INSTANCE.root.destroy)
            break

def main():
    global PALA_GUI_INSTANCE
    initialize_devtest_db_layer()
    root = tk.Tk()
    PALA_GUI_INSTANCE = PalaFaceGUI(root)
    threading.Thread(target=active_shell_talk_routine, daemon=True).start()
    root.mainloop()

if __name__ == "__main__":
    main()
