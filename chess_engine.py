#!/usr/bin/env python3
import sys
import time
from locale_config import get_text

try:
    import chess
except ImportError:
    pass

# Captura de forma segura o idioma enviado pelo orquestrador principal do P.A.L.A.
ACTIVE_LANG = sys.argv[1] if len(sys.argv) > 1 else "pt"

def render_actual_board_state(board):
    """Varre as casas reais da memória e força o terminal a desenhar as posições corretas."""
    piece_symbols = {
        'P': '♟', 'N': '♞', 'B': '♝', 'R': '♜', 'Q': '♛', 'K': '♚',  # Brancas
        'p': '♙', 'n': '♘', 'b': '♗', 'r': '♖', 'q': '♕', 'k': '♔'   # Pretas
    }
    header = "   +-----------------+"
    print(header)
    for rank in range(8, 0, -1):
        row_string = f" {rank} | "
        for file in range(1, 9):
            square = chess.square(file - 1, rank - 1)
            piece = board.piece_at(square)
            if piece:
                symbol = piece_symbols.get(piece.symbol(), '⭘')
                row_string += symbol + " "
            else:
                row_string += "⭘ "
        row_string += "|"
        print(row_string)
    print(header)
    print("     a b c d e f g h\n")

def evaluate_board_balance(board):
    """Mecanismo heurístico que analisa o equilíbrio material de peças na mesa."""
    piece_values = {1: 1, 2: 3, 3: 3, 4: 5, 5: 9, 6: 0}
    score = 0
    for square in range(64):
        piece = board.piece_at(square)
        if piece:
            val = piece_values.get(piece.piece_type, 0)
            if piece.color == chess.WHITE:
                score -= val
            else:
                score += val
    return score

def run_pala_chess_match():
    if 'chess' not in globals():
        print("[Chess Error] Dependências lógicas ausentes no wrapper local!")
        return

    import random
    board = chess.Board()
    print(get_text("chess_rules", ACTIVE_LANG))
    print(get_text("chess_exit", ACTIVE_LANG))

    while not board.is_game_over():
        render_actual_board_state(board)
        
        if board.turn == chess.WHITE:
            try:
                user_move_str = input(get_text("your_move", ACTIVE_LANG)).strip()
                if user_move_str.lower() in ["exit", "quit"]:
                    print(get_text("match_abort", ACTIVE_LANG))
                    break
                
                move = chess.Move.from_uci(user_move_str)
                if move in board.legal_moves:
                    board.push(move)
                else:
                    print(get_text("invalid_move", ACTIVE_LANG))
                    continue
            except Exception:
                print(get_text("syntax_error", ACTIVE_LANG))
                continue
        else:
            print(get_text("pala_thinking", ACTIVE_LANG))
            time.sleep(0.4)
            
            legal_moves = list(board.legal_moves)
            best_moves = []
            best_score = -9999
            
            captures = [m for m in legal_moves if board.is_capture(m)]
            if captures:
                chosen_move = random.choice(captures)
            else:
                for move in legal_moves:
                    board.push(move)
                    score = evaluate_board_balance(board)
                    board.pop()
                    if score > best_score:
                        best_score = score
                        best_moves = [move]
                    elif score == best_score:
                        best_moves.append(move)
                chosen_move = random.choice(best_moves) if best_moves else random.choice(legal_moves)
                    
            if chosen_move:
                board.push(chosen_move)
                print(get_text("pala_moved", ACTIVE_LANG).format(chosen_move))
            else:
                break

    if board.is_game_over():
        render_actual_board_state(board)
        print(get_text("game_over", ACTIVE_LANG).format(board.result()))

if __name__ == '__main__':
    run_pala_chess_match()
