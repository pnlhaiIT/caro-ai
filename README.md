# Caro AI 10x10

A web-based Gomoku (Caro) game where a player competes against an AI opponent.  
The AI is implemented using the **Minimax algorithm with Alpha-Beta Pruning** and heuristic board evaluation.

---

# Features

- Play Gomoku (Caro) on a 10x10 board
- AI opponent using classical game-search algorithms
- Minimax search with Alpha-Beta pruning
- Heuristic board evaluation based on pattern recognition
- Web interface using HTML, CSS, and JavaScript
- REST API built with Flask
- Containerized deployment using Docker 

---

# Project Structure
```
CARO-AI
│
├── engine/
│   ├── ai.py               # Core AI engine 
│   ├── config_para.json    # Parameters 
│   ├── board.py            # Board representation and game rules 
│   ├── app.py              # Flask API server for moves
│   ├── requirements.txt    # Dependencies
│   ├── templates/
│   │   └── index.html      # Main game page
│   └── static/
│       ├── script.js       # Frontend game logic and API calls
│       └── style.css       # UI styling
│
├── Dockerfile              # Container
├── docker-compose.yaml     # Orchestration
├── .gitignore              # Files ignored by Git
└── README.md               # Project documentation
```

---

# AI Core Flow
```
The AI determines the best move using a sequence of steps:
Player move
     │
     ▼
Receive board state
     │
     ▼
Generate candidate moves
(get_moves)
     │
     ▼
Prioritize promising moves
(move_score)
     │
     ▼
Limit search space
(top N moves)
     │
     ▼
Run minimax search
     │
     ▼
Apply alpha-beta pruning
(remove unnecessary branches)
     │
     ▼
Evaluate board states
(evaluate)
     │
     ▼
Return best move
```

---

# Technologies Used

- Python
- Flask
- JavaScript
- HTML / CSS
- Docker
  
---

# Quick Start

```bash
git clone https://github.com/pnlhaiIT/caro-ai.git
cd caro-ai/engine
pip install -r requirements.txt
python app.py
```

Then open:

```text
http://localhost:5100
```
---

# Author

Student project demonstrating classical Artificial Intelligence techniques in board game search.<br>
Phạm Nguyễn Long Hải 
