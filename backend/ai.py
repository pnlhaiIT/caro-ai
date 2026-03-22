from board import SIZE, check_win
import math

ttable = {}

def score_pattern(line, player):
    s = "".join(line)
    score = 0

    if player == "O":
        score += s.count("OOOOO") * 100000
        score += s.count(".OOOO.") * 30000

        score += s.count("OOOO.") * 15000
        score += s.count(".OOOO") * 15000

        score += s.count(".OOO.") * 8000

        score += s.count("OOO.") * 3000
        score += s.count(".OOO") * 3000

        score += s.count("OO.OO") * 7000

        score += s.count("OO.O") * 2000
        score += s.count("O.OO") * 2000

        score += s.count(".OO.") * 500

    else:
        score -= s.count("XXXXX") * 200000

        score -= s.count(".XXXX.") * 120000

        score -= s.count("XXXX.") * 60000
        score -= s.count(".XXXX") * 60000

        score -= s.count("XX.XX") * 120000

        score -= s.count("XX.X") * 40000
        score -= s.count("X.XX") * 40000

        score -= s.count(".XXX.") * 50000

        score -= s.count("XXX.") * 15000
        score -= s.count(".XXX") * 15000

        score -= s.count(".XX.") * 1000

    return score

def get_lines(board):
    lines = []

    for r in range(SIZE):
        lines.append(board[r])

    for c in range(SIZE):
        col = [board[r][c] for r in range(SIZE)]
        lines.append(col)

    for r in range(SIZE):
        diag = []
        i,j = r,0
        while i < SIZE and j < SIZE:
            diag.append(board[i][j])
            i += 1
            j += 1
        lines.append(diag)

    for c in range(1,SIZE):
        diag = []
        i,j = 0,c
        while i < SIZE and j < SIZE:
            diag.append(board[i][j])
            i += 1
            j += 1
        lines.append(diag)

    for r in range(SIZE):
        diag = []
        i,j = r,SIZE-1
        while i < SIZE and j >= 0:
            diag.append(board[i][j])
            i += 1
            j -= 1
        lines.append(diag)

    for c in range(SIZE-2,-1,-1):
        diag = []
        i,j = 0,c
        while i < SIZE and j >= 0:
            diag.append(board[i][j])
            i += 1
            j -= 1
        lines.append(diag)

    return lines

def get_forced_moves(board):
    moves = get_moves(board)

    for r, c in moves:
        board[r][c] = "O"
        if check_win(board, "O"):
            board[r][c] = "."
            return [(r, c)]
        board[r][c] = "."

    block = []
    for r, c in moves:
        board[r][c] = "X"
        if check_win(board, "X"):
            block.append((r, c))
        board[r][c] = "."

    if block:
        return block
    return []

def proximity_score(board, r, c):
    score = 0
    for dr in range(-2,3):
        for dc in range(-2,3):
            nr = r + dr
            nc = c + dc
            if 0 <= nr < SIZE and 0 <= nc < SIZE:
                if (nr, nc) == (r, c):
                    continue
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

    for r in range(SIZE):
        for c in range(SIZE):
            if board[r][c] == ".":
                continue

            if board[r][c] == "O":
                score += 2
                score += proximity_score(board, r, c)
            else:
                score -= 2
                score -= proximity_score(board, r, c)

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
                    if dr == 0 and dc == 0:
                        continue
                    if abs(dr) + abs(dc) > 1:
                        continue
                    nr = r + dr
                    nc = c + dc
                    if 0 <= nr < SIZE and 0 <= nc < SIZE:
                        if board[nr][nc] != ".":
                            moves.append((r,c))
                            found = True
                            break
                if found:
                    break
    if not moves:
        return [(SIZE//2, SIZE//2)]

    return moves

def move_score(board, r, c):
    board[r][c] = "O"
    if check_win(board, "O"):
        board[r][c] = "."
        return 1000000

    board[r][c] = "X"
    if check_win(board, "X"):
        board[r][c] = "."
        return 900000

    board[r][c] = "."
    score = 0
    x_count = 0

    for dr in range(-2,3):
        for dc in range(-2,3):
            if dr == 0 and dc == 0:
                continue
            if abs(dr) + abs(dc) > 2:
                continue
            nr = r + dr
            nc = c + dc
            if 0 <= nr < SIZE and 0 <= nc < SIZE:
                if board[nr][nc] == "O":
                    score += 2
                elif board[nr][nc] == "X":
                    x_count += 1
                    score += 4
    score += x_count * 3
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
    if depth >= 3:
        moves = moves[:15]
    else:
        moves = moves[:30]

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
    moves = get_moves(board)

    for r, c in moves:
        board[r][c] = "O"
        if check_win(board, "O"):
            board[r][c] = "."
            return (r, c)
        board[r][c] = "."

    for r, c in moves:
        board[r][c] = "X"
        if check_win(board, "X"):
            board[r][c] = "."
            return (r, c)
        board[r][c] = "."

    moves.sort(key=lambda m: move_score(board, m[0], m[1]), reverse=True)
    moves = moves[:20]
    best_score = -math.inf
    move = None

    for r, c in moves:
        board[r][c] = "O"
        score = minimax(board, 4, -math.inf, math.inf, False)
        board[r][c] = "."

        if score > best_score:
            best_score = score
            move = (r, c)

    return move