from board import SIZE, check_win
import math

ttable = {}

def score_pattern(line, player):
    s = "".join(line)
    score = 0

    if player == "O":
        score += s.count("OOOOO") * 1000000
        score += s.count(".OOOO.") * 500000
        score += s.count("OOOO.") * 250000
        score += s.count(".OOOO") * 250000
        score += s.count(".OOO.") * 50000
        score += s.count("OOO.") * 15000
        score += s.count(".OOO") * 15000
        score += s.count("OO.OO") * 30000
        score += s.count("OO.O") * 5000
        score += s.count("O.OO") * 5000
        score += s.count(".OO.") * 500
    else:  # X (opponent)
        score -= s.count("XXXXX") * 2000000
        score -= s.count(".XXXX.") * 600000
        score -= s.count("XXXX.") * 300000
        score -= s.count(".XXXX") * 300000
        score -= s.count("XX.XX") * 600000
        score -= s.count("XX.X") * 100000
        score -= s.count("X.XX") * 100000
        score -= s.count(".XXX.") * 150000
        score -= s.count("XXX.") * 50000
        score -= s.count(".XXX") * 50000
        score -= s.count(".XX.") * 5000

    return score

def get_lines(board):
    lines = []

    for r in range(SIZE):
        lines.append(board[r])

    for c in range(SIZE):
        lines.append([board[r][c] for r in range(SIZE)])

    for r in range(SIZE):
        diag1, diag2 = [], []
        i,j = r,0
        while i < SIZE and j < SIZE:
            diag1.append(board[i][j])
            diag2.append(board[i][SIZE-1-j])
            i += 1
            j += 1
        lines.append(diag1)
        lines.append(diag2)
    for c in range(1, SIZE):
        diag1, diag2 = [], []
        i,j = 0,c
        while i < SIZE and j < SIZE:
            diag1.append(board[i][j])
            diag2.append(board[i][SIZE-1-j])
            i += 1
            j += 1
        lines.append(diag1)
        lines.append(diag2)

    return lines

def get_forced_moves(board):
    moves_to_block = set()

    def add_blocks(line, r_start, c_start, dr, dc):
        s = "".join(line)
        idx = s.find(".XXX.")
        while idx != -1:
            moves_to_block.add((r_start + idx*dr, c_start + idx*dc))
            moves_to_block.add((r_start + (idx+4)*dr, c_start + (idx+4)*dc))
            idx = s.find(".XXX.", idx+1)

        idx = s.find("XXXX.")
        while idx != -1:
            moves_to_block.add((r_start + (idx+4)*dr, c_start + (idx+4)*dc))
            idx = s.find("XXXX.", idx+1)
        idx = s.find(".XXXX")
        while idx != -1:
            moves_to_block.add((r_start + idx*dr, c_start + idx*dc))
            idx = s.find(".XXXX", idx+1)

        idx = s.find("XX.X")
        while idx != -1:
            moves_to_block.add((r_start + (idx+2)*dr, c_start + (idx+2)*dc))
            idx = s.find("XX.X", idx+1)
        idx = s.find("X.XX")
        while idx != -1:
            moves_to_block.add((r_start + (idx+1)*dr, c_start + (idx+1)*dc))
            idx = s.find("X.XX", idx+1)

    for r in range(SIZE):
        add_blocks(board[r], r, 0, 0, 1)

    for c in range(SIZE):
        col = [board[r][c] for r in range(SIZE)]
        add_blocks(col, 0, c, 1, 0)

    for r in range(SIZE):
        diag = []
        rr, cc = r, 0
        while rr < SIZE and cc < SIZE:
            diag.append(board[rr][cc])
            rr += 1
            cc += 1
        add_blocks(diag, r, 0, 1, 1)
    for c in range(1, SIZE):
        diag = []
        rr, cc = 0, c
        while rr < SIZE and cc < SIZE:
            diag.append(board[rr][cc])
            rr += 1
            cc += 1
        add_blocks(diag, 0, c, 1, 1)

    for r in range(SIZE):
        diag = []
        rr, cc = r, SIZE-1
        while rr < SIZE and cc >= 0:
            diag.append(board[rr][cc])
            rr += 1
            cc -= 1
        add_blocks(diag, r, SIZE-1, 1, -1)
    for c in range(SIZE-2, -1, -1):
        diag = []
        rr, cc = 0, c
        while rr < SIZE and cc >= 0:
            diag.append(board[rr][cc])
            rr += 1
            cc -= 1
        add_blocks(diag, 0, c, 1, -1)

    return list(moves_to_block)

def proximity_score(board, r, c):
    score = 0
    for dr in range(-2,3):
        for dc in range(-2,3):
            nr, nc = r + dr, c + dc
            if 0 <= nr < SIZE and 0 <= nc < SIZE and (nr,nc)!=(r,c):
                if board[nr][nc] == "O":
                    score += 2
                elif board[nr][nc] == "X":
                    score += 1
    return score

def evaluate(board):
    score = 0
    lines = get_lines(board)
    for line in lines:
        if len(line) < 5:
            continue
        score += score_pattern(line, "O")
        score += score_pattern(line, "X")
    occupied = [(r,c) for r in range(SIZE) for c in range(SIZE) if board[r][c] != "."]
    for r, c in occupied:
        if board[r][c] == "O":
            score += 2 + proximity_score(board, r, c)
        else:
            score -= 2 + proximity_score(board, r, c)
    return score

def get_moves(board):
    moves = []
    for r in range(SIZE):
        for c in range(SIZE):
            if board[r][c] != ".":
                continue
            found = False
            for dr in range(-2,3):
                for dc in range(-2,3):
                    if dr==0 and dc==0:
                        continue
                    nr,nc = r+dr,c+dc
                    if 0<=nr<SIZE and 0<=nc<SIZE and board[nr][nc]!=".":
                        moves.append((r,c))
                        found = True
                        break
                if found:
                    break
    if not moves:
        return [(SIZE//2, SIZE//2)]
    if len(moves) > 40:
        return moves[:40]
    return moves

def move_score(board, r, c):
    score = 0
    x_count = 0
    for dr in range(-2,3):
        for dc in range(-2,3):
            if dr==0 and dc==0 or abs(dr)+abs(dc)>2:
                continue
            nr,nc = r+dr,c+dc
            if 0<=nr<SIZE and 0<=nc<SIZE:
                if board[nr][nc]=="O":
                    score += 2
                elif board[nr][nc]=="X":
                    x_count += 1
                    score += 4
    score += x_count*3
    return score

def minimax(board, depth, alpha, beta, maximizing):
    key = (tuple(tuple(row) for row in board), depth, maximizing)
    if key in ttable:
        return ttable[key]

    if check_win(board, "O"):
        return 1000000
    if check_win(board, "X"):
        return -1000000
    if depth == 0:
        return evaluate(board)

    forced = get_forced_moves(board)
    if forced:
        moves = forced
    else:
        moves = get_moves(board)
        moves.sort(key=lambda m: move_score(board, m[0], m[1]), reverse=True)
        moves = moves[:20]

    if maximizing:
        max_eval = -math.inf
        for r,c in moves:
            board[r][c] = "O"
            eval = minimax(board, depth-1, alpha, beta, False)
            board[r][c] = "."
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if alpha >= beta:
                break
        ttable[key] = max_eval
        return max_eval
    else:
        min_eval = math.inf
        for r,c in moves:
            board[r][c] = "X"
            eval = minimax(board, depth-1, alpha, beta, True)
            board[r][c] = "."
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if alpha >= beta:
                break
        ttable[key] = min_eval
        return min_eval

def best_move(board):
    ttable.clear()

    forced = get_forced_moves(board)
    if forced:
        return forced[0]

    moves = get_moves(board)
    moves.sort(key=lambda m: move_score(board, m[0], m[1]), reverse=True)
    moves = moves[:20]

    best_score = -math.inf
    move = None

    for r,c in moves:
        board[r][c] = "O"
        depth = 5 if len(moves)<10 else 4
        score = minimax(board, depth, -math.inf, math.inf, False)
        board[r][c] = "."
        if score > best_score:
            best_score = score
            move = (r,c)
    return move