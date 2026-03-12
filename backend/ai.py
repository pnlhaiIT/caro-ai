from board import SIZE, check_win
import math

def evaluate(board):
    score = 0
    
    for r in range(SIZE):
        for c in range(SIZE):

            if board[r][c] == "O":
                score += 1
            elif board[r][c] == "X":
                score -= 1
    return score

def get_moves(board):
    moves = []
    
    for r in range(SIZE):
        for c in range(SIZE):
            if board[r][c] == ".":
                moves.append((r,c))
    return moves

def minimax(board, depth, alpha, beta, maximizing):
    if check_win(board, "O"):
        return 1000
    if check_win(board, "X"):
        return -1000
    
    if depth == 0:
        return evaluate(board)
    
    moves = get_moves(board)

    if maximizing:
        max_eval = math.inf
        
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

