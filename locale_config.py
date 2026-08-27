#!/usr/bin/env python3

# =====================================================================
# P.A.L.A. INTERNATIONALIZATION (I18N) LOCALIZATION MATRIX
# =====================================================================

TRANSLATIONS = {
    "en": {
        # General Game Hub
        "select_mode": "Select game file row index to run (1-7): ",
        "invalid_move": "[!] Invalid or illegal move! Try again.\n",
        "syntax_error": "[!] Incorrect syntax! Use columns and ranks pattern (ex: e2e4).\n",
        "match_abort": "[Chess Engine] Match aborted by the operator.",
        "game_over": "=== GAME OVER: {} ===",
        
        # Chess Strings
        "chess_rules": "\n⚡ INPUT RULES: Type your moves in classic UCI format (Ex: e2e4, g1f3).",
        "chess_exit": "👉 Type 'exit' or 'quit' at any time to leave the table.\n",
        "your_move": "Your Move (White) ──► ",
        "pala_thinking": "[P.A.L.A.] Analyzing tactical positions in the decision tree...",
        "pala_moved": "[P.A.L.A. Move] Black played ──► {}",
        
        # Pong Strings
        "pong_title": "=== P.A.L.A. TERMINAL PONG | SCORE: PALA [{}] VS YOU [{}] ===",
        "pong_sim_title": "=== P.A.L.A. TERMINAL PONG | SCORE: PALA [{}] VS COMP [{}] ===",
        "pong_controls": "🎮 YOUR CONTROLS: [W/S] or [Arrows] to move | [Q] to Exit",
        "pong_epsilon": "🤖 P.A.L.A. Epsilon (Exploration): {:.3f}",
        "pong_menu_title": "=================================================================",
        "pong_menu_header": "  🏓 COMBAT MODE SELECTOR - PALA TERMINAL PONG  ",
        "pong_menu_opt1": "1. YOU VS P.A.L.A. (Human vs Deep Learning)",
        "pong_menu_opt2": "2. AUTONOMOUS TRAINING (AI vs Computer Bot)",
        "pong_menu_choice": "Choose game mode (1-2): ",
        "pong_activating_curses": "\n[*] Activating Curses interface... Prepare your reflexes!",
        "pong_activating_sim": "\n[*] Activating autonomous simulation loop...",
        "pong_match_ended": "=== MATCH ENDED! FINAL SCORE: PALA [{}] VS YOU [{}] ===",
        "pong_sim_epoch": " -> Simulation Round: {}/{} | Frame: {}/100",

        # Voice Feedback Rows
        "v_welcome": "System environment deployed successfully. Standing by, operator.",
        "v_lang_changed": "System language updated to English.",
        "v_doom_start": "Launching Deep Q-Network. Latching vision grabbers onto Doom game matrix.",
        "v_doom_end": "Exploratory reinforcement training completed. Matrix successfully compiled.",
        "v_chess_start": "Chess tactical module engaged. Stockfish sub-processes online.",
        "v_pong_start": "Terminal Pong arena initialized. Neural decision model active.",
        "v_alert_ram": "Warning. Hardware resource alert. Random access memory usage has exceeded safe threshold.",
        "v_alert_temp": "Alert. Core thermal reading is high. Throttling backup sweeps."
    },
    "pt": {
        # Central de Jogos Geral
        "select_mode": "Select game file row index to run (1-7): ",
        "invalid_move": "\033[91m[!] Movimento inválido ou ilegal! Tente novamente.\033[0m\n",
        "syntax_error": "\033[91m[!] Sintaxe incorreta! Use o padrão de colunas e linhas (ex: e2e4).\033[0m\n",
        "match_abort": "[Chess Engine] Partida abortada pelo operador.",
        "game_over": "=== FIM DE JOGO: {} ===",
        
        # Textos do Xadrez
        "chess_rules": "\n⚡ REGRAS DE INPUT: Digite seus movimentos no formato UCI clássico (Ex: e2e4, g1f3).",
        "chess_exit": "👉 Digite 'exit' ou 'quit' a qualquer momento para abandonar a mesa.\n",
        "your_move": "\033[93mSeu Movimento (Brancas) ──► \033[0m",
        "pala_thinking": "[P.A.L.A.] Analisando posições táticas na árvore de decisões...",
        "pala_moved": "\033[92m[P.A.L.A. Movimento] Pretas jogaram ──► {}\033[0m\n",
        
        # Textos do Pong
        "pong_title": "=== FLIPERAMA P.A.L.A. | PLACAR: PALA [{}] VS VOCÊ [{}] ===",
        "pong_sim_title": "=== P.A.L.A. TERMINAL PONG | PLACAR: PALA [{}] VS COMP [{}] ===",
        "pong_controls": "🎮 SEUS CONTROLES: [W/S] ou [Setas] para mover | [Q] para Sair",
        "pong_epsilon": "🤖 P.A.L.A. Epsilon (Exploração): {:.3f}",
        "pong_menu_title": "=================================================================",
        "pong_menu_header": "  🏓 SELETOR DE MODOS DE COMBATE - PALA TERMINAL PONG  ",
        "pong_menu_opt1": "1. VOCÊ VS P.A.L.A. (Humano vs Deep Learning)",
        "pong_menu_opt2": "2. TREINAMENTO AUTÔNOMO (IA vs Bot do Computador)",
        "pong_menu_choice": "Escolha o modo de jogo (1-2): ",
        "pong_activating_curses": "\n[*] Ativando interface Curses... Prepare seus reflexos!",
        "pong_activating_sim": "\n[*] Ativando loop autônomo de simulação...",
        "pong_match_ended": "=== PARTIDA TERMINADA! PLACAR FINAL: PALA [{}] VS VOCÊ [{}] ===",
        "pong_sim_epoch": " -> Rodada Simulação: {}/{} | Frame: {}/100",

        # Frases de Voz
        "v_welcome": "Ambiente de sistema implantado com sucesso. Em espera, operador.",
        "v_lang_changed": "Idioma do sistema atualizado para português.",
        "v_doom_start": "Iniciando rede profunda. Vinculando capturadores de visão na matriz do Doom.",
        "v_doom_end": "Treinamento exploratório por reforço concluído. Matriz compilada com sucesso.",
        "v_chess_start": "Módulo tático de xadrez acionado. Sub-processos online.",
        "v_pong_start": "Arena de Pong por terminal inicializada. Modelo de decisão neural ativo.",
        "v_alert_ram": "Atenção. Alerta de hardware. O uso da memória RAM ultrapassou o limite seguro.",
        "v_alert_temp": "Alerta. Temperatura do processador está alta. Reduzindo varreduras secundárias."
    }
}

def get_text(text_key, lang="pt"):
    """Retorna a string traduzida baseada na chave e idioma ativo."""
    return TRANSLATIONS.get(lang, TRANSLATIONS["pt"]).get(text_key, "")
