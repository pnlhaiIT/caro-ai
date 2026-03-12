from board import SIZE, check_win
import math

def score_pattern(line, player):
    s = "".join(line)
    score = 0
    if player == "O":
        if "OOOOO" in s: score += 100000
        if ".OOOO." in s: score += 30000
        if "OOOO." in s or ".OOOO" in s: score += 15000
        if ".OOO." in s: score += 8000
        if "OOO." in s or ".OOO" in s: score += 3000
        if "OO.OO" in s: score += 7000
        if "OO.O" in s or "O.OO" in s: score += 2000
        if ".OO." in s: score += 500
    else:
        if "XXXXX" in s: score -= 200000
        if ".XXXX." in s: score -= 80000
        if "XXXX." in s or ".XXXX" in s: score -= 50000

        if ".XXX." in s: score -= 50000
        if "XXX." in s or ".XXX" in s: score -= 15000

        if "XX.XX" in s: score -= 50000
        if "XX.X" in s or "X.XX" in s: score -= 25000

        if ".XX." in s: score -= 1000
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

def evaluate(board):
    score = 0
    lines = get_lines(board)

    for line in lines:
        if len(line) < 5:
            continue
        score += score_pattern(line, "O")
        score += score_pattern(line, "X")

    center = SIZE // 2

    for r in range(SIZE):
        for c in range(SIZE):
            if board[r][c] == "O":
                score += 2
                score += 4 - (abs(r-center) + abs(c-center))
            elif board[r][c] == "X":
                score -= 2
                score -= 4 - (abs(r-center) + abs(c-center))
    return score

def get_moves(board):
    moves = []

    for r in range(SIZE):
        for c in range(SIZE):
            if board[r][c] != ".":
                continue
            found = False
            for dr in [-1,0,1]:
                for dc in [-1,0,1]:
                    if dr == 0 and dc == 0:
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
    score = 0
    x_count = 0
    o_count = 0

    for dr in [-1,0,1]:
        for dc in [-1,0,1]:
            if dr == 0 and dc == 0:
                continue
            nr = r + dr
            nc = c + dc
            if 0 <= nr < SIZE and 0 <= nc < SIZE:
                if board[nr][nc] == "O":
                    o_count += 1
                    score += 2
                elif board[nr][nc] == "X":
                    x_count += 1
                    score += 4
    score += x_count * 3
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
    moves = moves[:12]

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
        return  max_eval
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
        return min_eval

def best_move(board):
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
    moves = moves[:22]
    best_score = -math.inf
    move = None

    for r, c in moves:
        board[r][c] = "O"
        score = minimax(board, 3, -math.inf, math.inf, False)
        board[r][c] = "."

        if score > best_score:
            best_score = score
            move = (r, c)

    return move