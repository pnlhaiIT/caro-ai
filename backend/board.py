SIZE = 10

def create_board():
    return [["." for _ in range(SIZE)] for _ in range(SIZE)]

def check_win(board, player):
    directions = [(1,0),(0,1),(1,1),(1,-1)]

    for r in range(SIZE):
        for c in range(SIZE):
            if board[r][c] != player:
                continue

            for dr, dc in directions:
                count = 0
                for i in range(5):
                    nr = r + dr*i
                    nc = c + dc*i

                    if 0 <= nr < SIZE and 0 <= nc < SIZE and board[nr][nc] == player:
                        count += 1
                    else:
                        break
                
                if count == 5:
                    return True
    return False