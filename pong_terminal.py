#!/usr/bin/env python3
import os
import sys
import time
import random
import numpy as np
import cv2

# =====================================================================
# PALA TERMINAL PONG PHYSICS & TEXT GRAPHICS MATRIX ENGINE
# =====================================================================

class TerminalPongGame:
    def __init__(self, width=40, height=15):
        self.width = width
        self.height = height
        self.reset_game_arena()
        
    def reset_game_arena(self):
        """Reseta as posições e direções da bolinha e das raquetes."""
        self.ball_x = self.width // 2
        self.ball_y = self.height // 2
        
        # Direção da bola: [-1 ou 1]
        self.ball_dx = random.choice([-1, 1])
        self.ball_dy = random.choice([-1, 1])
        
        # Posição vertical central das raquetes (Garante limite interno inicial)
        self.paddle_left_y = self.height // 2
        self.paddle_right_y = self.height // 2
        self.score_left = 0
        self.score_right = 0

    def move_paddles(self, action_left, action_right):
        """Move as raquetes baseado nos inputs do operador e do P.A.L.A."""
        # Raquete Esquerda (P.A.L.A.): 0=Cima, 1=Baixo (Trava estritamente nas bordas internas)
        if action_left == 0 and self.paddle_left_y > 1:
            self.paddle_left_y -= 1
        elif action_left == 1 and self.paddle_left_y < self.height - 2:
            self.paddle_left_y += 1
            
        # Raquete Direita (Inimigo): Segue a bola de forma fluida e fixa nas bordas
        if self.ball_y < self.paddle_right_y and self.paddle_right_y > 1:
            self.paddle_right_y -= 1
        elif self.ball_y > self.paddle_right_y and self.paddle_right_y < self.height - 2:
            self.paddle_right_y += 1

    def update_physics_frame(self):
        """Calcula o vetor de colisão da bolinha nas paredes e raquetes."""
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy
        
        # Colisão com o teto ou chão (Inverte o vetor Y)
        if self.ball_y <= 0 or self.ball_y >= self.height - 1:
            self.ball_dy *= -1
            
        # Colisão com a Raquete Esquerda (X=1)
        if self.ball_x == 1:
            if abs(self.ball_y - self.paddle_left_y) <= 1:
                self.ball_dx *= -1
                return 10.0  # Defendeu! Recompensa positiva!
                
        # Colisão com a Raquete Direita (X=Width-2)
        if self.ball_x == self.width - 2:
            if abs(self.ball_y - self.paddle_right_y) <= 1:
                self.ball_dx *= -1
                
        # Ponto do Oponente
        if self.ball_x < 0:
            self.score_right += 1
            self.ball_x = self.width // 2
            self.ball_y = self.height // 2
            self.ball_dx = 1
            return -50.0  
            
        # Ponto do Agente
        if self.ball_x >= self.width:
            self.score_left += 1
            self.ball_x = self.width // 2
            self.ball_y = self.height // 2
            self.ball_dx = -1
            return 50.0   
            
        return -0.1  

    def extract_game_state_matrix(self):
        """Gera uma matriz compacta 84x84 para alimentar a rede do doom_brain."""
        matrix = np.zeros((84, 84), dtype=np.uint8)
        bx = int((self.ball_x / self.width) * 83)
        by = int((self.ball_y / self.height) * 83)
        pl = int((self.paddle_left_y / self.height) * 83)
        pr = int((self.paddle_right_y / self.height) * 83)
        
        cv2.circle(matrix, (bx, by), 3, 255, -1)
        cv2.line(matrix, (1, max(0, pl-5)), (1, min(83, pl+5)), 255, 3)
        cv2.line(matrix, (82, max(0, pr-5)), (82, min(83, pr+5)), 255, 3)
        return matrix

    def draw_ascii_frame(self):
        """Imprime a quadra de Pong em caracteres de texto de forma estrita e alinhada."""
        os.system('clear')
        print(f"=== P.A.L.A. TERMINAL PONG | PLACAR: PALA [{self.score_left}] VS COMP [{self.score_right}] ===")
        print("+" + "-" * (self.width) + "+")
        
        for y in range(self.height):
            line_str = "|"
            for x in range(self.width):
                if x == self.ball_x and y == self.ball_y:
                    line_str += "●"  # A bola
                elif x == 0 and abs(y - self.paddle_left_y) <= 1:
                    line_str += "█"  # Raquete Esquerda (P.A.L.A.) fixada na coluna 0!
                elif x == self.width - 1 and abs(y - self.paddle_right_y) <= 1:
                    line_str += "█"  # Raquete Direita fixada na última coluna!
                else:
                    line_str += " "
            line_str += "|"
            print(line_str)
            
        print("+" + "-" * (self.width) + "+")
        print("👉 Controles Manuais do Operador: [W] para Cima | [S] para Baixo")

