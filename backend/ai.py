from board import SIZE, check_win
import math
import random

DIRECTIONS = [(1,0), (0,1), (1,1), (1,-1)]

def get_moves(board):
    moves = set()
    has_piece = False

    for r in range(SIZE):
        for c in range(SIZE):
            if board[r][c] != ".":
                has_piece = True
                for dr in range(-2, 3):
                    for dc in range(-2, 3):
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < SIZE and 0 <= nc < SIZE:
                            if board[nr][nc] == ".":
                                moves.add((nr, nc))
    if not has_piece:
        return [(random.randint(0, SIZE-1), random.randint(0, SIZE-1))]

    return list(moves)

def move_score(board, r, c):
    score = 0

    for dr, dc in DIRECTIONS:
        s = get_line(board, r, c, dr, dc, "O")

        score += s.count("O") * 2
        score += s.count("X") * 3

    center = SIZE // 2
    score -= abs(r - center) + abs(c - center)

    return score

def get_line(board, r, c, dr, dc, player):
    line = []

    for i in range(-4, 5):
        nr = r + dr*i
        nc = c + dc*i
        if 0 <= nr < SIZE and 0 <= nc < SIZE:
            line.append(board[nr][nc])
        else:
            line.append("#")

    return "".join(line)

def get_lines(board):
    lines = []

    for r in range(SIZE):
        lines.append(board[r])

    for c in range(SIZE):
        lines.append([board[r][c] for r in range(SIZE)])

    for start_r in range(SIZE):
        diag = []
        r, c = start_r, 0
        while r < SIZE and c < SIZE:
            diag.append(board[r][c])
            r += 1
            c += 1
        if len(diag) >= 5:
            lines.append(diag)

    for start_c in range(1, SIZE):
        diag = []
        r, c = 0, start_c
        while r < SIZE and c < SIZE:
            diag.append(board[r][c])
            r += 1
            c += 1
        if len(diag) >= 5:
            lines.append(diag)

    for start_r in range(SIZE):
        diag = []
        r, c = start_r, SIZE - 1
        while r < SIZE and c >= 0:
            diag.append(board[r][c])
            r += 1
            c -= 1
        if len(diag) >= 5:
            lines.append(diag)

    for start_c in range(SIZE - 2, -1, -1):
        diag = []
        r, c = 0, start_c
        while r < SIZE and c >= 0:
            diag.append(board[r][c])
            r += 1
            c -= 1
        if len(diag) >= 5:
            lines.append(diag)

    return lines

def check_threat_at(board, r, c):
    board[r][c] = "X"

    if check_win(board, "X"):
        board[r][c] = "."
        return 100000
    
    score = 0

    for dr, dc in DIRECTIONS:
        s = get_line(board, r, c, dr, dc, "X")

        if ".XXX.X." in s or ".X.XXX." in s or "XX.XX" in s:
            score += 5000

        if (
            ".XXX." in s or
            "..XXX." in s or
            ".XXX.." in s or
            "..XXX.." in s
        ):
            score += 2000

        if ".XX.X." in s or ".X.XX." in s:
            score += 800
    board[r][c] = "."
    return score

def get_urgent_moves(board):
    moves = set()
    has_piece = False

    for r in range(SIZE):
        for c in range(SIZE):
            if board[r][c] != ".":
                has_piece = True
                for dr in range(-3, 4):   
                    for dc in range(-3, 4):
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < SIZE and 0 <= nc < SIZE:
                            if board[nr][nc] == ".":
                                moves.add((nr, nc))
    if not has_piece:
        return [(SIZE // 2, SIZE // 2)]

    return list(moves)

def collect_pattern_blocks(line, coords):
    s = "".join(line)
    blocks = []

    idx = 0
    while True:
        idx = s.find(".XXXX.", idx)
        if idx == -1:
            break
        blocks.append((coords[idx], 100000))
        blocks.append((coords[idx + 5], 100000))
        idx += 1

    idx = 0
    while True:
        idx = s.find("XXXX.", idx)
        if idx == -1:
            break
        blocks.append((coords[idx + 4], 90000))
        idx += 1

    idx = 0
    while True:
        idx = s.find(".XXXX", idx)
        if idx == -1:
            break
        blocks.append((coords[idx], 90000))
        idx += 1

    idx = 0
    while True:
        idx = s.find("XX.XX", idx)
        if idx == -1:
            break
        blocks.append((coords[idx + 2], 5000))
        idx += 1

    idx = 0
    while True:
        idx = s.find("XXX.X", idx)
        if idx == -1:
            break
        blocks.append((coords[idx + 3], 5000))
        idx += 1

    idx = 0
    while True:
        idx = s.find("X.XXX", idx)
        if idx == -1:
            break
        blocks.append((coords[idx + 1], 5000))
        idx += 1

    idx = 0
    while True:
        idx = s.find(".XXX.", idx)
        if idx == -1:
            break
        blocks.append((coords[idx], 2000))
        blocks.append((coords[idx + 4], 2000))
        idx += 1

    idx = 0
    while True:
        idx = s.find(".XX.X.", idx)
        if idx == -1:
            break
        blocks.append((coords[idx + 3], 800))
        idx += 1

    idx = 0
    while True:
        idx = s.find(".X.XX.", idx)
        if idx == -1:
            break
        blocks.append((coords[idx + 2], 800))
        idx += 1

    return blocks

def existing_threat_block(board):
    candidate_scores = {}

    def add_blocks_from_line(line, coords):
        for pos, w in collect_pattern_blocks(line, coords):
            r, c = pos
            if board[r][c] == ".":
                candidate_scores[(r, c)] = candidate_scores.get((r, c), 0) + w

    for r in range(SIZE):
        line = [board[r][c] for c in range(SIZE)]
        coords = [(r, c) for c in range(SIZE)]
        add_blocks_from_line(line, coords)

    for c in range(SIZE):
        line = [board[r][c] for r in range(SIZE)]
        coords = [(r, c) for r in range(SIZE)]
        add_blocks_from_line(line, coords)

    for start_r in range(SIZE):
        line, coords = [], []
        r, c = start_r, 0
        while r < SIZE and c < SIZE:
            line.append(board[r][c])
            coords.append((r, c))
            r += 1
            c += 1
        if len(line) >= 5:
            add_blocks_from_line(line, coords)

    for start_c in range(1, SIZE):
        line, coords = [], []
        r, c = 0, start_c
        while r < SIZE and c < SIZE:
            line.append(board[r][c])
            coords.append((r, c))
            r += 1
            c += 1
        if len(line) >= 5:
            add_blocks_from_line(line, coords)

    for start_r in range(SIZE):
        line, coords = [], []
        r, c = start_r, SIZE - 1
        while r < SIZE and c >= 0:
            line.append(board[r][c])
            coords.append((r, c))
            r += 1
            c -= 1
        if len(line) >= 5:
            add_blocks_from_line(line, coords)

    for start_c in range(SIZE - 2, -1, -1):
        line, coords = [], []
        r, c = 0, start_c
        while r < SIZE and c >= 0:
            line.append(board[r][c])
            coords.append((r, c))
            r += 1
            c -= 1
        if len(line) >= 5:
            add_blocks_from_line(line, coords)

    if not candidate_scores:
        return None

    return max(candidate_scores, key=candidate_scores.get)

def winning_move(board):
    moves = get_moves(board)

    for r, c in moves:
        board[r][c] = "O"
        if check_win(board, "O"):
            board[r][c] = "."
            return (r, c)
        board[r][c] = "."

    return None

def urgent_move(board):
    moves = get_urgent_moves(board)

    best_move = None
    best_score = 0

    for r, c in moves:
        score = check_threat_at(board, r, c)

        if score >= 100000:
            return (r, c)

        if score > best_score:
            best_score = score
            best_move = (r, c)

    return best_move if best_score > 0 else None

def evaluate(board):
    score = 0

    for line in get_lines(board):
        s = "".join(line)
        score += s.count("OOOO") * 10000
        score += s.count("OOO") * 1000
        score -= s.count("XXXX") * 20000
        score -= s.count("XXX") * 2000

    return score

def minimax(board, depth, alpha, beta, maximizing):
    if check_win(board, "O"):
        return 1000000
    if check_win(board, "X"):
        return -1000000
    if depth == 0:
        return evaluate(board)

    moves = get_moves(board)
    moves.sort(key=lambda m: move_score(board, m[0], m[1]), reverse=True)
    moves = moves[:10]  

    if maximizing:
        max_eval = -math.inf
        for r, c in moves:
            board[r][c] = "O"
            val = minimax(board, depth-1, alpha, beta, False)
            board[r][c] = "."
            max_eval = max(max_eval, val)
            alpha = max(alpha, val)
            if alpha >= beta:
                break
        return max_eval
    else:
        min_eval = math.inf
        for r, c in moves:
            board[r][c] = "X"
            val = minimax(board, depth-1, alpha, beta, True)
            board[r][c] = "."
            min_eval = min(min_eval, val)
            beta = min(beta, val)
            if alpha >= beta:
                break
        return min_eval

def best_move(board):

    win = winning_move(board)
    if win:
        return win

    block_existing = existing_threat_block(board)
    if block_existing:
        return block_existing

    urgent = urgent_move(board)
    if urgent:
        return urgent

    moves = get_moves(board)

    if len(moves) == 1:
        return moves[0]

    moves.sort(key=lambda m: move_score(board, m[0], m[1]), reverse=True)

    if len(moves) > 12:       
        limit = 20
        depth = 3
    else:                    
        limit = 10            
        depth = 4     

    limit = 8 if len(moves) > 12 else 10
    moves = moves[:limit]

    best_score = -math.inf
    best = moves[0]

    for r, c in moves:
        board[r][c] = "O"

        score = minimax(board, depth, -math.inf, math.inf, False) 
        board[r][c] = "."

        if score > best_score:
            best_score = score
            best = (r, c)

    return best