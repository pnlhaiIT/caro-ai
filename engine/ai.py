from board import SIZE, check_win
import math
import random

DIRECTIONS = [(1, 0), (0, 1), (1, 1), (1, -1)]

DIFFICULTY_DEPTH = {
    -1: 0,   # dễ
     0: 1,   # trung bình
     1: 3    # khó
}

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

EVAL_PATTERNS_O = [
    (".OOOO.", 100000),
    ("OOOO.", 25000),
    (".OOOO", 25000),
    ("OOO.O", 18000),
    ("OO.OO", 18000),
    ("O.OOO", 18000),

    (".OOO.", 5000),
    ("OOO..", 1500),
    ("..OOO", 1500),
    (".OOO#", 1000),
    ("#OOO.", 1000),

    (".OO.O.", 3000),
    (".O.OO.", 3000),
    ("OO.O.", 2200),
    (".O.OO", 2200),
    ("O.OO.", 2200),
    (".OO.O", 2200),

    (".OO.", 300),
    (".O.O.", 180),
]

EVAL_PATTERNS_X = [
    (".XXXX.", 120000),
    ("XXXX.", 30000),
    (".XXXX", 30000),
    ("XXX.X", 22000),
    ("XX.XX", 22000),
    ("X.XXX", 22000),

    (".XXX.", 7000),
    ("XXX..", 1800),
    ("..XXX", 1800),
    (".XXX#", 1200),
    ("#XXX.", 1200),

    (".XX.X.", 3500),
    (".X.XX.", 3500),
    ("XX.X.", 2500),
    (".X.XX", 2500),
    ("X.XX.", 2500),
    (".XX.X", 2500),

    (".XX.", 350),
    (".X.X.", 220),
]

TRANSPOSITION_TABLE = {}

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
        center = SIZE // 2
        return [(center, center)]

    return list(moves)

def get_urgent_moves(board):
    return get_moves(board, radius=3)

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

def board_key(board, depth, maximizing):
    return ("".join("".join(row) for row in board), depth, maximizing)

def evaluate_line_string(s):
    score = 0

    for pattern, value in EVAL_PATTERNS_O:
        score += s.count(pattern) * value

    for pattern, value in EVAL_PATTERNS_X:
        score -= s.count(pattern) * value

    return score

def count_threat_types_after_move(board, r, c, player):
    board[r][c] = player
    open4 = 0
    close4 = 0
    open3 = 0

    if player == "O":
        open4_patterns = [".OOOO."]
        close4_patterns = ["OOOO.", ".OOOO", "OOO.O", "OO.OO", "O.OOO"]
        open3_patterns = [".OOO.", ".OO.O.", ".O.OO."]
    else:
        open4_patterns = [".XXXX."]
        close4_patterns = ["XXXX.", ".XXXX", "XXX.X", "XX.XX", "X.XXX"]
        open3_patterns = [".XXX.", ".XX.X.", ".X.XX."]

    for dr, dc in DIRECTIONS:
        s = get_line(board, r, c, dr, dc)

        for p in open4_patterns:
            if p in s:
                open4 += 1

        for p in close4_patterns:
            if p in s:
                close4 += 1
                break

        for p in open3_patterns:
            if p in s:
                open3 += 1
                break

    board[r][c] = "."
    return open4, close4, open3

def local_pattern_score(board, r, c, player):
    score = 0

    if player == "O":
        patterns = EVAL_PATTERNS_O
    else:
        patterns = EVAL_PATTERNS_X

    for dr, dc in DIRECTIONS:
        s = get_line(board, r, c, dr, dc)
        s = "#" + s + "#"
        for p, w in patterns:
            score += s.count(p) * w

    return score

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

def find_open4_creator(board, player):
    best = None
    best_score = -1

    for r, c in get_moves(board):
        if board[r][c] != ".":
            continue

        open4, close4, open3 = count_threat_types_after_move(board, r, c, player)

        if open4 > 0:
            score = open4 * 100 + close4 * 10 + open3
            if score > best_score:
                best_score = score
                best = (r, c)

    return best

def move_score(board, r, c):
    if board[r][c] != ".":
        return -10**9

    center = SIZE // 2
    center_bonus = -(abs(r - center) + abs(c - center))

    board[r][c] = "O"
    attack = local_pattern_score(board, r, c, "O")
    o_open4, o_close4, o_open3 = count_threat_types_after_move(board, r, c, "O")
    attack += o_open4 * 50000 + o_close4 * 12000 + o_open3 * 3000
    board[r][c] = "."

    board[r][c] = "X"
    defense = local_pattern_score(board, r, c, "X")
    x_open4, x_close4, x_open3 = count_threat_types_after_move(board, r, c, "X")
    defense += x_open4 * 60000 + x_close4 * 15000 + x_open3 * 3500
    board[r][c] = "."

    return attack + defense * 1.15 + center_bonus

def evaluate(board):
    score = 0

    for line in get_lines(board):
        s = "#" + "".join(line) + "#"
        score += evaluate_line_string(s)

    return score

def minimax(board, depth, alpha, beta, maximizing):
    key = board_key(board, depth, maximizing)
    if key in TRANSPOSITION_TABLE:
        return TRANSPOSITION_TABLE[key]

    if check_win(board, "O"):
        return 1000000
    if check_win(board, "X"):
        return -1000000
    if depth == 0:
        val = evaluate(board)
        TRANSPOSITION_TABLE[key] = val
        return val

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
        TRANSPOSITION_TABLE[key] = max_eval
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
        TRANSPOSITION_TABLE[key] = min_eval
        return min_eval

def best_move(board, difficulty=0):
    TRANSPOSITION_TABLE.clear()

    win = winning_move(board)
    if win:
        return win

    if difficulty == -1:
        moves = get_moves(board)
        return random.choice(moves) if moves else None

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
    if not moves:
        return None
    if len(moves) == 1:
        return moves[0]

    moves.sort(key=lambda m: move_score(board, m[0], m[1]), reverse=True)

    if difficulty == 0:
        moves = moves[:6]
    else:
        moves = moves[:10]

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