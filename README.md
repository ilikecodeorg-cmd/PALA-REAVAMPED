# P.A.L.A. REVAMPED (Personal Assistant Linux Automation)

[![License: MIT](https://shields.io)](https://opensource.org)
[![Python: 3.10+](https://shields.io)](https://python.org)
[![Ollama: qwen2.5:3b](https://shields.io)](https://ollama.com)

P.A.L.A. Revamped is a highly optimized, fully autonomous local Linux System Administration assistant framework. Built using a thread-isolated dual-channel system, it merges a plain-text terminal listener routine with an animated Tkinter graphical dashboard interface. 

Equipped with long-term relational memory layers, absolute short-code macro bypass channels, and dynamic loop sentry guards, P.A.L.A. safely automates package management, process scheduling, network firewall tracking, and microservices telemetry analysis without ever risking terminal lockups or frozen interaction tracks.

---

## 🚀 Core Architectural Engine Features

* **🧠 Intent Evaluation Sentry**: Evaluates the linguistic parameters of inputs instantly. Conversational prompts, text greetings, or casual statements (e.g., *"Hello PALA!"*) are automatically redirected away from terminal execution blocks, preventing unnecessary arbitrary filesystem mutations.
* **⚡ Decoupled Direct Pipeline Routing**: Absolute short-code slash macros forcefully bypass the large language model's inference cycles entirely. Commands are passed directly onto high-speed background thread subprocess workers to update logs instantly.
* **💾 Relational Database Memory Core**: Implements a persistent SQLite storage layer (`pala_devtest_cache.db`) that records historical execution counts, parameters, and long-term user constraints that hot-reload smoothly across system reboots.
* **🛡️ Dynamic Sentry Loop Counter Shields**: Monitors sequential tool use interactions. If a local model gets trapped processing messy, infinite stdout buffers past Step 3, the shield forcefully drops the loop thread and returns the UI cleanly to standby configurations.
* **🗣️ Thread-Isolated Text-To-Speech Driver**: Built-in `spd-say` auditory synthesis pipelines function on separate async workers, ensuring speech runtime audio plays smoothly while syncing with face canvas vector mouth movements.
* **⚠️ Adaptive Hardware Resource Sentry**: Continuously monitors host allocation tables (/proc/meminfo, thermal zones). Exceeding defined limits automatically triggers a native desktop overlay alert (`notify-send`) and changes the interface face grid color map to emergency crimson.

---

## 🕹️ Production Short-Code Slash Macros Pool

| Slash Command Macro | Executed Under-the-Hood Shell Action | Output Target & Sentry Routine Impact |
| :--- | :--- | :--- |
| `/syscheck` | `uname -a && uptime && df -h` | Logs system architecture specs, uptime data, and block metrics right to the GUI terminal panel frame. |
| `/memclean` | `sudo sync && echo 3 \| sudo tee /proc/sys/vm/drop_caches` | Drops page caches, dentries, and inodes safely out of the active kernel allocation boundaries. |
| `/aptcheck` | `apt list --upgradable` | Sweeps upstream repository indexes to fetch a list of available host package updates. |
| `/cronlist` | `crontab -l` | Lists running user background timing automation scripts and repetitive tasks non-interactively. |
| `/seccheck` | Isolate high-risk targets via `apt list` | Targets core packages (`openssh`, `openssl`, `systemd`, `linux-image`), compiles an advisory report inside `~/pala_security_audit.log`, and alerts the desktop user. |
| `/perflog` | Pulls loads via `/proc/loadavg` & `free -m` | Captures CPU averages, memory allocation curves, and active machine uptimes to format a snapshot at `~/pala_performance_report.log`. |
| `/netcheck` | `sudo ufw status verbose` \|\| `ss -tulpn` | Maps firewall profiles, tracking active port configurations and communication socket tables into `~/pala_network_audit.log`. |
| `/dockercheck` | `docker ps -a` & `docker stats` | Sweeps background microservice environments, compiling container runtimes and hardware usage matrix graphs inside `~/pala_docker_telemetry.log`. |

---

## 📊 Structural Component Dataflow Map

```text
[Operator Prompt] ──► (Part 17 Readline Terminal Listener Thread)
                            │
            ┌───────────────┴───────────────┐
            ▼                               ▼
    [Slash Macro Trigger]          [Unstructured System Goal]
            │                               │
            ▼                               ▼
 (Part 18 Direct Bypass Workers)    (Part 16 Intent Router Sentry)
            │                               │
            │                       ┌───────┴───────┐
            │                       ▼               ▼
            │               [Conversational]   [Technical SysAdmin Task]
            │                       │               │
            ▼                       ▼               ▼
   {Shell Subprocess}        { Warm Response }   (Part 15 Ollama API Bridge)
            │                       │               │
            └───────────────┬───────┴───────────────┘
                            ▼
     (Part 14 Canvas Multi-Skin Render & UI Component Core Panel)
                            │
            ┌───────────────┴───────────────┐
            ▼                               ▼
 [Part 11 notify-send Alerts]   [Part 10 spd-say Async TTS Core Voice]
```

---

## 🛠️ Machine Workspace Environment Setup

### 📋 Prerequisites
Ensure your local host has the underlying engine capabilities installed:

```bash
# 1. Install local system audio synthesis tools and tkinter graphical rendering engines
sudo apt update && sudo apt install -y speech-dispatcher tk libreadline-dev curl libnotify-bin

# 2. Deploy your Ollama microservice local endpoint model
ollama run qwen2.5:3b
```

### 📦 Installation & Boot Steps
Clone and run P.A.L.A. directly out of your local dev virtual environment:

```bash
# 1. Switch to your project workspace directory
cd ~/ai-agent

# 2. Fire up the master Python orchestrator node file
python3 devtestagent.py
```

### ⚙️ Interactive Slash Commands
While the active terminal loop is waiting, use these built-in management short-codes:
* `/settings`: Opens the TopLevel Tkinter popup configurations manager window to edit RAM boundary limits, flush relational logs, and toggle real-time log mirroring.
* `/toggleconsole`: Instantly changes the mirroring level status to reflect active background data processes straight to stdout.
* `quit` / `exit`: Discharges all active loop threads, cleans up database descriptors, and kills window frames cleanly.

---

## 📄 License
This application is distributed under the open-source **MIT License**. Check the full file tracking boundaries details for parameters.
