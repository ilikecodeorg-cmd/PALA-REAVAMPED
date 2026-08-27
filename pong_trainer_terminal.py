#!/usr/bin/env python3
import time
import sys
import os
import numpy as np
from locale_config import get_text

try:
    import torch
    import cv2
    import curses
    from pong_terminal import TerminalPongGame
    from doom_brain import DOOMBrain
except ImportError as e:
    print(f"[Pong Error] Falta carregar bibliotecas na venv: {e}")
    sys.exit(1)

# Captura de forma segura o idioma enviado pelo orquestrador principal do P.A.L.A.
ACTIVE_LANG = sys.argv[1] if len(sys.argv) > 1 else "pt"

def run_pala_vs_human_curses(stdscr, game, brain):
    """Modo Jogador vs P.A.L.A. usando a biblioteca curses para inputs instantâneos."""
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(50)
    
    while game.score_left < 5 and game.score_right < 5:
        key = stdscr.getch()
        human_action = None
        if key in [ord('w'), ord('W'), curses.KEY_UP]:
            human_action = 0
        elif key in [ord('s'), ord('S'), curses.KEY_DOWN]:
            human_action = 1
        elif key in [ord('q'), ord('Q'), 27]:
            break

        state_matrix = game.extract_game_state_matrix()
        pala_action = brain.select_action(state_matrix)
        
        if pala_action == 0 and game.paddle_left_y > 1:
            game.paddle_left_y -= 1
        elif pala_action == 1 and game.paddle_left_y < game.height - 2:
            game.paddle_left_y += 1
            
        if human_action == 0 and game.paddle_right_y > 1:
            game.paddle_right_y -= 1
        elif human_action == 1 and game.paddle_right_y < game.height - 2:
            game.paddle_right_y += 1

        game.update_physics_frame()
        brain.decay_exploration()
        
        stdscr.clear()
        stdscr.addstr(0, 0, get_text("pong_title", ACTIVE_LANG).format(game.score_left, game.score_right))
        stdscr.addstr(1, 0, "+" + "-" * game.width + "+")
        
        for y in range(game.height):
            line_str = "|"
            for x in range(game.width):
                if x == game.ball_x and y == game.ball_y:
                    line_str += "●"
                elif x == 0 and abs(y - game.paddle_left_y) <= 1:
                    line_str += "█"
                elif x == game.width - 1 and abs(y - game.paddle_right_y) <= 1:
                    line_str += "█"
                else:
                    line_str += " "
            line_str += "|"
            stdscr.addstr(y + 2, 0, line_str)
            
        stdscr.addstr(game.height + 2, 0, "+" + "-" * game.width + "+")
        stdscr.addstr(game.height + 3, 0, get_text("pong_controls", ACTIVE_LANG))
        stdscr.addstr(game.height + 4, 0, get_text("pong_epsilon", ACTIVE_LANG).format(brain.epsilon))
        stdscr.refresh()

def run_ia_vs_bot_simulation(game, brain):
    """Modo Simulação Automatizada padrão (PC vs PC) para treino."""
    total_episodes = 5
    for episode in range(1, total_episodes + 1):
        game.reset_game_arena()
        steps = 0
        while game.score_left < 3 and game.score_right < 3 and steps < 100:
            steps += 1
            state_matrix = game.extract_game_state_matrix()
            pala_action = brain.select_action(state_matrix)
            game.move_paddles(action_left=pala_action, action_right=None)
            game.update_physics_frame()
            game.draw_ascii_frame()
            
            print(get_text("pong_sim_epoch", ACTIVE_LANG).format(episode, total_episodes, steps))
            print(get_text("pong_epsilon", ACTIVE_LANG).format(brain.epsilon))
            brain.decay_exploration()
            time.sleep(0.08)
        time.sleep(1)

def main_menu_launcher():
    os.system('clear')
    print(get_text("pong_menu_title", ACTIVE_LANG))
    print(get_text("pong_menu_header", ACTIVE_LANG))
    print(get_text("pong_menu_title", ACTIVE_LANG))
    print(get_text("pong_menu_opt1", ACTIVE_LANG))
    print(get_text("pong_menu_opt2", ACTIVE_LANG))
    print(get_text("pong_menu_title", ACTIVE_LANG))
    
    choice = input(get_text("pong_menu_choice", ACTIVE_LANG)).strip()
    game = TerminalPongGame(width=40, height=15)
    brain = DOOMBrain(num_actions=2)
    
    if choice == "1":
        print(get_text("pong_activating_curses", ACTIVE_LANG))
        time.sleep(1.5)
        curses.wrapper(run_pala_vs_human_curses, game, brain)
        os.system('clear')
        print(get_text("pong_match_ended", ACTIVE_LANG).format(game.score_left, game.score_right))
    else:
        print(get_text("pong_activating_sim", ACTIVE_LANG))
        time.sleep(1)
        run_ia_vs_bot_simulation(game, brain)

if __name__ == '__main__':
    main_menu_launcher()
