from board import SIZE, check_win
import json
import math
from pathlib import Path
import random

CONFIG_PATH = Path(__file__).with_name("config_para.json")
with CONFIG_PATH.open("r", encoding="utf-8") as f:
    CFG = json.load(f)

DIRECTIONS = [tuple(direction) for direction in CFG["DIRECTIONS"]]
DIFFICULTY_DEPTH = {int(k): v for k, v in CFG["DIFFICULTY_DEPTH"].items()}
THREAT_CHECK_PATTERNS = [(p, w) for p, w in CFG["THREAT_CHECK_PATTERNS"]]
PATTERN_BLOCKS = [(p, idxs, w) for p, idxs, w in CFG["PATTERN_BLOCKS"]]
EVAL_PATTERNS_O = [(p, w) for p, w in CFG["EVAL_PATTERNS_O"]]
EVAL_PATTERNS_X = [(p, w) for p, w in CFG["EVAL_PATTERNS_X"]]

TRANSPOSITION_TABLE = {}
MOVE_SCORE_CACHE = {}
MOVE_GEN_CACHE = {}


def bstate(board):
    return "".join("".join(row) for row in board)

def get_moves(board, radius=2):
    state = bstate(board)
    cache_key = (state, radius)
    cached_moves = MOVE_GEN_CACHE.get(cache_key)
    if cached_moves is not None:
        return list(cached_moves)

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
        generated_moves = [(center, center)]
        MOVE_GEN_CACHE[cache_key] = tuple(generated_moves)
        return generated_moves

    generated_moves = list(moves)
    MOVE_GEN_CACHE[cache_key] = tuple(generated_moves)
    return generated_moves

def urgent_moves(board):
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
    return (bstate(board), depth, maximizing)

def eval_line(s):
    score = 0

    for pattern, value in EVAL_PATTERNS_O:
        score += s.count(pattern) * value

    for pattern, value in EVAL_PATTERNS_X:
        score -= s.count(pattern) * value

    return score

def count_threats(board, r, c, player):
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

def local_score(board, r, c, player):
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

def check_threat(board, r, c):
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

def collect_blocks(line, coords):
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

def threat_block(board):
    candidate_scores = {}

    def add_blocks_from_line(line, coords):
        for pos, w in collect_blocks(line, coords):
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

def win_move(board, player):
    for r, c in get_moves(board):
        board[r][c] = player
        if check_win(board, player):
            board[r][c] = "."
            return (r, c)
        board[r][c] = "."
    return None

def urgent_move(board):
    best = None
    best_score = 0

    for r, c in urgent_moves(board):
        score = check_threat(board, r, c)

        if score >= 100000:
            return (r, c)

        if score > best_score:
            best_score = score
            best = (r, c)

    return best if best_score > 0 else None

def find_open4(board, player):
    best = None
    best_score = -1

    for r, c in get_moves(board):
        if board[r][c] != ".":
            continue

        open4, close4, open3 = count_threats(board, r, c, player)

        if open4 > 0:
            score = open4 * 100 + close4 * 10 + open3
            if score > best_score:
                best_score = score
                best = (r, c)

    return best

def move_score(board, r, c):
    state = bstate(board)
    cache_key = (state, r, c)
    cached_score = MOVE_SCORE_CACHE.get(cache_key)
    if cached_score is not None:
        return cached_score

    if board[r][c] != ".":
        return -10**9

    center = SIZE // 2
    center_bonus = -(abs(r - center) + abs(c - center))
    move_count = state.count("X") + state.count("O")

    board[r][c] = "O"
    attack = local_score(board, r, c, "O")
    o_open4, o_close4, o_open3 = count_threats(board, r, c, "O")
    attack += o_open4 * 50000 + o_close4 * 12000 + o_open3 * 3000
    if o_open3 >= 2:
        attack += 50000
    board[r][c] = "."

    board[r][c] = "X"
    defense = local_score(board, r, c, "X")
    x_open4, x_close4, x_open3 = count_threats(board, r, c, "X")
    defense += x_open4 * 60000 + x_close4 * 15000 + x_open3 * 3500
    if x_open3 >= 2:
        defense += 60000
    board[r][c] = "."

    if move_count < 8:
        defense_weight = 0.75
    elif move_count < 14:
        defense_weight = 0.95
    else:
        defense_weight = 1.15

    score = attack + defense * defense_weight + center_bonus
    MOVE_SCORE_CACHE[cache_key] = score
    return score


def sort_moves(board, moves):
    state = bstate(board)

    def score_for(move):
        r, c = move
        cache_key = (state, r, c)
        cached_score = MOVE_SCORE_CACHE.get(cache_key)
        if cached_score is not None:
            return cached_score
        return move_score(board, r, c)

    moves.sort(key=score_for, reverse=True)

def evaluate(board):
    score = 0

    for line in get_lines(board):
        s = "#" + "".join(line) + "#"
        score += eval_line(s)

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
    sort_moves(board, moves)
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
    MOVE_SCORE_CACHE.clear()
    MOVE_GEN_CACHE.clear()

    win = win_move(board, "O")
    if win:
        return win

    opp_win = win_move(board, "X")
    if opp_win:
        return opp_win

    if difficulty == -1:
        moves = get_moves(board)
        return random.choice(moves) if moves else None

    move_count = sum(row.count("X") + row.count("O") for row in board)

    #ưu tiên tạo open4 trước
    ai_open4 = find_open4(board, "O")
    opp_open4 = find_open4(board, "X")
    if ai_open4 and not opp_open4:
        return ai_open4

    #block đối thủ
    block_existing = threat_block(board)
    if block_existing:
        urgent_block_score = check_threat(board, block_existing[0], block_existing[1])
        should_force_block = move_count >= 10 or urgent_block_score >= 5000
        if should_force_block:
            return block_existing

    #xét urgent
    urgent = urgent_move(board)
    if urgent:
        return urgent

    # nếu đang rất sớm, ưu tiên phát triển thế tấn công hơn block pattern nhẹ
    if block_existing and move_count >= 6:
        return block_existing

    if difficulty == 1:
        opp_open4 = find_open4(board, "X")
        opp_has_close4 = block_existing is not None

        if not opp_open4 and not opp_has_close4:
            ai_open4 = find_open4(board, "O")
            if ai_open4:
                return ai_open4

    moves = get_moves(board)
    if not moves:
        return None
    if len(moves) == 1:
        return moves[0]

    sort_moves(board, moves)

    if difficulty == 0:
        moves = moves[:4]
    else:
        moves = moves[:6]

    if move_count < 10:
        depth = 1
    elif move_count < 20:
        depth = 2
    else:
        depth = 3

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