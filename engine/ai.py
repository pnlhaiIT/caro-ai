from board import SIZE, check_win
import math
import random

DIRECTIONS = [(1, 0), (0, 1), (1, 1), (1, -1)]

DIFFICULTY_DEPTH = {
    -1: 0,   # dễ
     0: 1,   # trung bình
     1: 3    # khó
}

ATTACK_PATTERNS = [
    ("OOOO", 10000),
    ("OOOO.", 10000),
    (".OOOO", 10000),
    (".OOO.", 3000),
    ("OO.OO", 1500),
    (".OO.O.", 1500),
    ("OO.O.", 1500),
    (".O.OO", 1500),
    (".OO.", 200),
]

DEFENSE_PATTERNS = [
    ("XX.XX", 2000),
    ("X.XX.", 2000),
    (".XX.X", 2000),
    ("XXX..", 2000),
    ("..XXX", 2000),
]

THREAT_CHECK_PATTERNS = [
    (".XXX.X.", 5000),
    (".X.XXX.", 5000),
    ("XX.XX", 5000),
    (".XXX.", 2000),
    ("..XXX.", 2000),
    (".XXX..", 2000),
    ("..XXX..", 2000),
    (".XX.X.", 800),
    (".X.XX.", 800),
]

PATTERN_BLOCKS = [
    (".XXXX.", [0, 5], 100000),
    ("XXXX.", [4], 90000),
    (".XXXX", [0], 90000),
    ("XX.XX", [2], 5000),
    ("XXX.X", [3], 5000),
    ("X.XXX", [1], 5000),
    (".XXX.", [0, 4], 2000),
    (".XX.X.", [3], 800),
    (".X.XX.", [2], 800),
]

def get_moves(board, radius=2):
    moves = set()
    has_piece = False

    for r in range(SIZE):
        for c in range(SIZE):
            if board[r][c] != ".":
                has_piece = True
                for dr in range(-radius, radius + 1):
                    for dc in range(-radius, radius + 1):
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < SIZE and 0 <= nc < SIZE and board[nr][nc] == ".":
                            moves.add((nr, nc))

    if not has_piece:
        return [(random.randint(0, SIZE - 1), random.randint(0, SIZE - 1))]

    return list(moves)

def get_line(board, r, c, dr, dc):
    line = []
    for i in range(-4, 5):
        nr = r + dr * i
        nc = c + dc * i
        if 0 <= nr < SIZE and 0 <= nc < SIZE:
            line.append(board[nr][nc])
        else:
            line.append("#")
    return "".join(line)

def attack_pattern_score(board, r, c):
    score = 0
    for dr, dc in DIRECTIONS:
        s = get_line(board, r, c, dr, dc)
        for p, w in ATTACK_PATTERNS:
            if p in s:
                score += w
    return score

def near_win_score(board, r, c):
    score = 0
    for dr, dc in DIRECTIONS:
        s = get_line(board, r, c, dr, dc)
        if "OOO." in s or ".OOO" in s:
            score += 5000
        if "OO." in s or ".OO" in s:
            score += 500
    return score

def defensive_pattern_score(board, r, c):
    score = 0
    for dr, dc in DIRECTIONS:
        s = get_line(board, r, c, dr, dc)
        for p, w in DEFENSE_PATTERNS:
            if p in s:
                score += w
    return score

def move_score(board, r, c):
    score = 0

    for dr, dc in DIRECTIONS:
        s = get_line(board, r, c, dr, dc)
        score += s.count("X") * 3
        score += s.count("O") * 2

    score += attack_pattern_score(board, r, c)
    score += near_win_score(board, r, c)
    score += defensive_pattern_score(board, r, c)

    center = SIZE // 2
    score -= abs(r - center) + abs(c - center)

    return score

def get_lines(board):
    lines = []

    for r in range(SIZE):
        lines.append([board[r][c] for c in range(SIZE)])

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
        s = get_line(board, r, c, dr, dc)
        for p, w in THREAT_CHECK_PATTERNS:
            if p in s:
                score += w

    board[r][c] = "."
    return score

def get_urgent_moves(board):
    return get_moves(board, radius=3)

def collect_pattern_blocks(line, coords):
    s = "".join(line)
    blocks = []

    for pattern, indexes, weight in PATTERN_BLOCKS:
        idx = 0
        while True:
            idx = s.find(pattern, idx)
            if idx == -1:
                break
            for offset in indexes:
                blocks.append((coords[idx + offset], weight))
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
    for r, c in get_moves(board):
        board[r][c] = "O"
        if check_win(board, "O"):
            board[r][c] = "."
            return (r, c)
        board[r][c] = "."
    return None

def urgent_move(board):
    best = None
    best_score = 0

    for r, c in get_urgent_moves(board):
        score = check_threat_at(board, r, c)

        if score >= 100000:
            return (r, c)

        if score > best_score:
            best_score = score
            best = (r, c)

    return best if best_score > 0 else None

def count_threat_types_after_move(board, r, c, player):
    board[r][c] = player
    open4 = 0
    close4 = 0

    if player == "O":
        open_pattern = ".OOOO."
        close_patterns = ["OOOO.", ".OOOO", "OOO.O", "OO.OO", "O.OOO"]
    else:
        open_pattern = ".XXXX."
        close_patterns = ["XXXX.", ".XXXX", "XXX.X", "XX.XX", "X.XXX"]

    for dr, dc in DIRECTIONS:
        s = get_line(board, r, c, dr, dc)

        if open_pattern in s:
            open4 += 1

        for p in close_patterns:
            if p in s:
                close4 += 1
                break

    board[r][c] = "."
    return open4, close4

def find_open4_creator(board, player):
    best = None
    best_score = -1

    for r, c in get_moves(board):
        if board[r][c] != ".":
            continue

        open4, close4 = count_threat_types_after_move(board, r, c, player)

        if open4 > 0:
            score = open4 * 100 + close4
            if score > best_score:
                best_score = score
                best = (r, c)

    return best

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
            val = minimax(board, depth - 1, alpha, beta, False)
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
            val = minimax(board, depth - 1, alpha, beta, True)
            board[r][c] = "."
            min_eval = min(min_eval, val)
            beta = min(beta, val)
            if alpha >= beta:
                break
        return min_eval

def best_move(board, difficulty=0):
    win = winning_move(board)
    if win:
        return win

    if difficulty == -1:
        return random.choice(get_moves(board))

    block_existing = existing_threat_block(board)
    if block_existing:
        return block_existing

    urgent = urgent_move(board)
    if urgent:
        return urgent

    if difficulty == 1:
        opp_open4 = find_open4_creator(board, "X")
        opp_has_close4 = block_existing is not None

        if not opp_open4 and not opp_has_close4:
            ai_open4 = find_open4_creator(board, "O")
            if ai_open4:
                return ai_open4

    moves = get_moves(board)
    if len(moves) == 1:
        return moves[0]

    if difficulty >= 0:
        moves.sort(key=lambda m: move_score(board, m[0], m[1]), reverse=True)
        if difficulty == 0:
            limit = min(6, max(4, len(moves)))
        else:
            limit = min(10, max(8, len(moves)))
        moves = moves[:limit]

    depth = DIFFICULTY_DEPTH.get(difficulty, 2)

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