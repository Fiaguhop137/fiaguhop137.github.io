import random
BOARD_SIZE=3
MUTATION_AMOUNT=0.1
def print_board(board):
    print("\033[H\033[J",end="")
    for row in board:
        for cell in row:
            print("O" if cell else ".", end=" ")
        print()
def flip_cell(board,x,y):
    if 0<=x<len(board) and 0<=y<len(board[0]):
        board[x][y]=not board[x][y]
def touch_board(board,x,y):
    flip_cell(board,x,y)
    flip_cell(board,x-1,y)
    flip_cell(board,x+1,y)
    flip_cell(board,x,y-1)
    flip_cell(board,x,y+1)
def copy_board(board):
    return [row[:] for row in board]
def solved(board):
    return not any(any(row) for row in board)
class ai:
    def __init__(self):
        self.weights=[[[[random.uniform(-1, 1) for _ in range(BOARD_SIZE)]for _ in range(BOARD_SIZE)]for _ in range(BOARD_SIZE)]for _ in range(BOARD_SIZE)]
        self.performance=0
def clone_ai(parent):
    child=ai()
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            for i in range(BOARD_SIZE):
                for j in range(BOARD_SIZE):
                    child.weights[x][y][i][j]=parent.weights[x][y][i][j]
    return child
def mutate_ai(parent):
    child=clone_ai(parent)
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            for i in range(BOARD_SIZE):
                for j in range(BOARD_SIZE):
                    if random.random()<0.1:
                        child.weights[x][y][i][j]+=random.uniform(-MUTATION_AMOUNT,MUTATION_AMOUNT)
    return child
def ai_logic(board,ai):
    best_score=float("-inf")
    best_move=None
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            test_board=copy_board(board)
            touch_board(test_board,x,y)
            score=0
            for i in range(BOARD_SIZE):
                for j in range(BOARD_SIZE):
                    if test_board[i][j]:
                        score+=ai.weights[x][y][i][j]
            if score>best_score:
                best_score=score
                best_move=(x,y)
    return best_move
def generate_board():
    board=[[False]*BOARD_SIZE for _ in range(BOARD_SIZE)]
    for _ in range(BOARD_SIZE*BOARD_SIZE):
        x=random.randint(0,BOARD_SIZE-1)
        y=random.randint(0,BOARD_SIZE-1)
        touch_board(board,x,y)
    return board
def test_ai(ai,original_board,show=False):
    board=copy_board(original_board)
    moves=0
    while not solved(board):
        move=ai_logic(board,ai)
        if move is None:
            break
        touch_board(board,*move)
        moves+=1
        if show:
            print_board(board)
        if moves>1000000:
            moves*=2
            return 1000000
    if solved(board):
        moves*=0.5
    ai.performance+=moves
    return moves
ai_1=ai()
ai_2=ai()
generation=0
while True:
    generation+=1
    print(f"Generation {generation}")
    board = generate_board()
    print("Starting board:")
    print_board(board)
    ai_1.performance=0
    ai_2.performance=0
    performance_1=test_ai(ai_1,board)
    performance_2=test_ai(ai_2,board)
    print()
    print(f"AI 1: {performance_1} moves")
    print(f"AI 2: {performance_2} moves")
    if solved(board):
        print("The original board was somehow already solved. 1 in a million chance. Go buy a lottery ticket.")
    if performance_1 < performance_2:
        print("AI 1 wins!")
        print("Disposing of AI 2...")
        ai_2 = mutate_ai(ai_1)
        print("AI 2 was cloned and mutated.")
    elif performance_2 < performance_1:
        print("AI 2 wins!")
        print("Disposing of AI 1...")
        ai_1 = mutate_ai(ai_2)
        print("AI 1 was cloned and mutated.")
    else:
        print("It's a tie!")
        ai_1 = mutate_ai(ai_1)
        ai_2 = mutate_ai(ai_2)
    print("This was generation", generation, "of the AI.")
    input("Press Enter to continue...")