#!/usr/bin/env python3
import os
import random
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

# =====================================================================
# DEEP REINFORCEMENT LEARNING DOOM BRAIN ENGINE
# =====================================================================

class DQNDoomNet(nn.Module):
    """Rede Neural Convolucional (CNN) que processa frames 84x84 do DOOM."""
    def __init__(self, num_actions=4):
        super(DQNDoomNet, self).__init__()
        # Camadas convolucionais para capturar formas geométricas e movimento nos pixels
        self.features = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=8, stride=4),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=4, stride=2),
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3, stride=1),
            nn.ReLU()
        )
        # Camadas densas para mapeamento e tomada de decisão de valor Q
        self.fc = nn.Sequential(
            nn.Linear(64 * 7 * 7, 512),
            nn.ReLU(),
            nn.Linear(512, num_actions)
        )

    def forward(self, x):
        # Normalização dos pixels da tela (0-255) para valores flutuantes entre 0 e 1
        x = x / 255.0
        x = self.features(x)
        x = x.view(x.size(0), -1)
        return self.fc(x)

class DOOMBrain:
    """Interface de decisão do agente baseada em Deep Q-Learning (Equação de Bellman)."""
    def __init__(self, num_actions=4):
        self.num_actions = num_actions
        # Força o uso da CPU otimizada para o seu processador Intel Core i3
        self.device = torch.device("cpu")
        self.policy_net = DQNDoomNet(num_actions).to(self.device)
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=0.00025)
        
        self.epsilon = 1.0        # Taxa de exploração inicial (100% ações aleatórias para coletar dados)
        self.epsilon_decay = 0.995 # Redução gradual da aleatoriedade a cada época de treino
        self.epsilon_min = 0.1     # Limite mínimo de exploração randômica preventiva
        
    def select_action(self, state_matrix):
        """Escolhe uma ação usando a estratégia adaptativa Epsilon-Greedy."""
        if random.random() <= self.epsilon:
            return random.randint(0, self.num_actions - 1)
        
        with torch.no_grad():
            # Converte a matriz de imagem do OpenCV em tensores matemáticos do PyTorch
            state_tensor = torch.FloatTensor(state_matrix).unsqueeze(0).unsqueeze(0).to(self.device)
            q_values = self.policy_net(state_tensor)
            return torch.argmax(q_values).item()

    def decay_exploration(self):
        """Aumenta a confiança do modelo reduzindo o fator de exploração randômica."""
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
