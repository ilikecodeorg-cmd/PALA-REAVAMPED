# 🚀 P.A.L.A. - Workspace Active Environment (REVAMPED)

[**English**](#english) | [**Português (Brasil)**](#português-brasil)

---

## English

The **P.A.L.A. (Personal Assistant & Logical Agent)** is a modular ecosystem for automation, system telemetry, and embedded artificial intelligence, running natively and ultra-lightweight over the **Lubuntu LXQt** environment. 

This revamped version expands the agent's capabilities by introducing autonomous game modules based on **Deep Reinforcement Learning (DRL)** and algorithmic logic, fully integrated with an internationalized (I18N) architecture.

### 🧠 New Artificial Intelligence Architectures

#### 🏓 1. Terminal Pong via Deep Reinforcement Learning (DRL)
The agent now features a physical Pong arena rendered in pure ASCII text that connects directly to a **Deep Q-Network (DQN)** built with **PyTorch**.
* **Vision Engine:** Converts the terminal text matrix into an `84x84` pixel visual frame processed by **Convolutional Layers (CNN)**.
* **Decision Making:** Uses an adaptive **Epsilon-Greedy** strategy to balance random exploration and decisions based on accumulated rewards.
* **Game Modes:** Supports autonomous simulation (AI vs Bot) and interactive arcade mode (Human vs AI) using the `curses` library for real-time keystroke tracking.

#### ♟️ 2. Heuristic Tactical Chess Engine
An integrated chess module that manages the official rules of the International Chess Federation via the `chess` library, running entirely in the virtual environment's RAM.
* **Decision Tree:** Uses a **1-level depth Mini-Max algorithm** that analyzes the material balance of pieces and prioritizes tactical captures instantly.
* **Low-Impact Renderer:** Forces the board matrix to redraw in universal characters directly to the console buffer on every move.

### 🌐 Internationalization (I18N) & Voice Architecture
The system features a centralized localization dictionary (`locale_config.py`) with native support for **Brazilian Portuguese (pt-br)** and **English (en)**.
* **Data Persistence:** The operator's language preference is permanently saved in relational tables within the **SQLite** database.
* **Adaptive Vocal Synthesizer:** The background voice engine (`spd-say`) reads the active language configuration and instantly switches the phonetic accent (American/Brazilian) and narrated strings on the speaker.

### 🕹️ New Slash Commands
Enter these fast shortcuts directly into the interactive `PALA-User >` prompt:

| Command | Description | Behavior |
| :--- | :--- | :--- |
| `/language` | Toggles the global system language | Changes UI texts and switches `spd-say` accent (PT-BR/EN) |
| `/play_pong` | Initializes the Pong DRL arena | Opens mode selector (Human vs AI or Auto Training) |
| `/play_chess` | Opens the tactical chess board | Starts a match using classic UCI notation (e.g., `e2e4`) |
| `/train_doom` | Starts visual DOOM automation | Executes X11 navigation macros inside GZDoom |

### 🛠️ Execution Requirements
Ensure your local `.venv` has the core mathematical libraries updated for CPU processing:
```bash
source .venv/bin/activate
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cpu --no-cache-dir
pip install numpy opencv-python python-chess mss
```

---

## Português (Brasil)

O **P.A.L.A. (Personal Assistant & Logical Agent)** é um ecossistema modular de automação, telemetria de sistemas e inteligência artificial embarcada, rodando de forma nativa e ultra-leve sobre o ambiente **Lubuntu LXQt**.

Esta nova versão expande as capacidades do agente com a introdução de módulos autônomos de jogos baseados em **Deep Reinforcement Learning (DRL)** e lógica algorítmica, operando de forma integrada a uma arquitetura internacionalizada (I18N).

### 🧠 Novas Arquiteturas de Inteligência Artificial

#### 🏓 1. Terminal Pong por Deep Reinforcement Learning (DRL)
O agente agora possui uma arena física de Pong renderizada em texto ASCII que se conecta diretamente a uma rede **Deep Q-Network (DQN)** construída em **PyTorch**.
* **Engine de Visão:** Transforma a matriz de texto do terminal em uma matriz visual de pixels `84x84` processada por **Camadas Convolucionais (CNN)**.
* **Tomada de Decisão:** Utiliza a estratégia adaptativa **Epsilon-Greedy** para balancear exploração aleatória e tomadas de decisão baseadas em recompensas acumuladas.
* **Modos de Jogo:** Suporta simulação autônoma (IA vs Bot) e modo arcade interativo (Humano vs IA) utilizando a biblioteca `curses` para inputs em tempo real.

#### ♟️ 2. Motor Tático de Xadrez Heurístico
Um módulo de xadrez integrado que gerencia as regras oficiais da Federação Internacional através da biblioteca `chess`, rodando inteiramente na memória RAM da máquina virtual.
* **Árvore de Decisões:** Utiliza um algoritmo **Mini-Max de 1 nível de profundidade** que calcula o balanço material de peças e prioriza capturas táticas vantajosas instantaneamente.
* **Renderizador de Baixo Impacto:** Força o redesenho da matriz do tabuleiro em caracteres universais direto no buffer do console a cada lance.

### 🌐 Arquitetura de Internacionalização (I18N) e Voz BR
O sistema agora conta com um dicionário de localização centralizado (`locale_config.py`) com suporte nativo e otimizado para **Português do Brasil (pt-br)** e **Inglês (en)**.
* **Persistência de Dados:** A preferência de idioma do operador é salva de forma definitiva em tabelas relacionais do banco de dados **SQLite**.
* **Sintetizador Vocal Adaptativo:** O motor de voz em segundo plano (`spd-say`) lê a chave de idioma ativa e altera instantaneamente o sotaque fonético (americano/brasileiro nativo) e as strings narradas no alto-falante.

### 🕹️ Novos Comandos Absolutos (Slash Commands)
Insira estes atalhos rápidos diretamente no prompt interativo `PALA-User >`:

| Comando | Descrição | Comportamento |
| :--- | :--- | :--- |
| `/language` | Alterna o idioma global do sistema | Altera textos e chaveia o sotaque do `spd-say` (PT-BR/EN) |
| `/play_pong` | Inicializa a arena DRL de Pong | Abre o seletor de modos (Humano vs IA ou Treino Automatizado) |
| `/play_chess` | Abre o tabuleiro tático de xadrez | Inicia um confronto em notação UCI clássica (Ex: `e2e4`) |
| `/train_doom` | Inicia a automação visual do DOOM | Executa macros sequenciais de navegação X11 no GZDoom |

### 🛠️ Requisitos de Execução no Ambiente Virtual
Garanta que a sua `.venv` local possua as bibliotecas matemáticas centrais atualizadas para CPU:
```bash
source .venv/bin/activate
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cpu --no-cache-dir
pip install numpy opencv-python python-chess mss
```
