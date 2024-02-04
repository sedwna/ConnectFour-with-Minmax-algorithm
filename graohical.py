import pygame
import numpy as np
import sys
import math
import random

# Define constants
ROW_COUNT = 6
COLUMN_COUNT = 7
SQUARESIZE = 100
RADIUS = int(SQUARESIZE / 2 - 5)
WIDTH = COLUMN_COUNT * SQUARESIZE
HEIGHT = (ROW_COUNT + 1) * SQUARESIZE
PLAYER_PIECE = 1
AI_PIECE = 2
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Create the game board
def create_board():
    return np.zeros((ROW_COUNT, COLUMN_COUNT))

# Drop a piece on the board
def drop_piece(board, row, col, piece):
    board[row][col] = piece

# Check if a location is a valid move
def is_valid_location(board, col):
    return board[ROW_COUNT-1][col] == 0

# Get the next available row for a piece to be dropped
def get_next_open_row(board, col):
    return np.argmax(board[:, col] == 0)

# Check for a winning move
def winning_move(board, piece):
    # Check horizontal
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if np.all(board[r, c:c+4] == piece):
                return True
    # Check vertical
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if np.all(board[r:r+4, c] == piece):
                return True
    # Check positively sloped diagonals
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if np.all(board[r:r+4, c:c+4].diagonal() == piece):
                return True
    # Check negatively sloped diagonals
    for c in range(COLUMN_COUNT - 3):
        for r in range(3, ROW_COUNT):
            if np.all(np.fliplr(board)[r-3:r+1, c:c+4].diagonal() == piece):
                return True
    return False

# Evaluate the score for a window
def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE if piece == AI_PIECE else AI_PIECE
    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(0) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(0) == 2:
        score += 2
    if window.count(opp_piece) == 3 and window.count(0) == 1:
        score -= 4
    return score

# Score the board
def score_position(board, piece):
    score = 0
    # Score center column
    center_array = [int(i) for i in list(board[:, COLUMN_COUNT//2])]
    center_count = center_array.count(piece)
    score += center_count * 3
    # Score horizontal
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r,:])]
        for c in range(COLUMN_COUNT-3):
            window = row_array[c:c+4]
            score += evaluate_window(window, piece)
    # Score vertical
    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:,c])]
        for r in range(ROW_COUNT-3):
            window = col_array[r:r+4]
            score += evaluate_window(window, piece)
    # Score positively sloped diagonal
    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT-3):
            window = [board[r+i][c+i] for i in range(4)]
            score += evaluate_window(window, piece)
    # Score negatively sloped diagonal
    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT-3):
            window = [board[r+3-i][c+i] for i in range(4)]
            score += evaluate_window(window, piece)
    return score

# Find the best move using Minimax algorithm with alpha-beta pruning
def get_best_move(board):
    valid_locations = [col for col in range(COLUMN_COUNT) if is_valid_location(board, col)]
    best_score = -math.inf
    best_col = random.choice(valid_locations)
    for col in valid_locations:
        row = get_next_open_row(board, col)
        temp_board = board.copy()
        drop_piece(temp_board, row, col, AI_PIECE)
        score = minimax(temp_board, 4, -math.inf, math.inf, False)
        if score > best_score:
            best_score = score
            best_col = col
    return best_col

# Minimax algorithm with alpha-beta pruning
def minimax(board, depth, alpha, beta, maximizing_player):
    valid_locations = [col for col in range(COLUMN_COUNT) if is_valid_location(board, col)]
    if depth == 0 or winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(valid_locations) == 0:
        if winning_move(board, AI_PIECE):
            return 100000000000000
        elif winning_move(board, PLAYER_PIECE):
            return -10000000000000
        else:
            return score_position(board, AI_PIECE)
    if maximizing_player:
        value = -math.inf
        for col in valid_locations:
            row = get_next_open_row(board, col)
            temp_board = board.copy()
            drop_piece(temp_board, row, col, AI_PIECE)
            score = minimax(temp_board, depth-1, alpha, beta, False)
            value = max(value, score)
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return value
    else:
        value = math.inf
        for col in valid_locations:
            row = get_next_open_row(board, col)
            temp_board = board.copy()
            drop_piece(temp_board, row, col, PLAYER_PIECE)
            score = minimax(temp_board, depth-1, alpha, beta, True)
            value = min(value, score)
            beta = min(beta, value)
            if alpha >= beta:
                break
        return value

# Initialize Pygame
pygame.init()

# Set up the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Connect Four")

# Initialize the game board
board = create_board()
print(board)
pygame.display.update()

# Create font
myfont = pygame.font.SysFont("monospace", 75)

# Draw the game board
def draw_board(board):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BLACK, (int(c * SQUARESIZE + SQUARESIZE / 2), int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2)), RADIUS)
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == PLAYER_PIECE:
                pygame.draw.circle(screen, RED, (int(c * SQUARESIZE + SQUARESIZE / 2), HEIGHT - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
            elif board[r][c] == AI_PIECE:
                pygame.draw.circle(screen, YELLOW, (int(c * SQUARESIZE + SQUARESIZE / 2), HEIGHT - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
    pygame.display.update()

# Game loop
turn = random.randint(PLAYER_PIECE, AI_PIECE)
game_over = False
draw_board(board)
game_end_time = None

# Game loop
while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.MOUSEMOTION:
            pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
            posx = event.pos[0]
            pygame.draw.circle(screen, RED if turn == PLAYER_PIECE else YELLOW, (posx, int(SQUARESIZE/2)), RADIUS)
            pygame.display.update()

        if event.type == pygame.MOUSEBUTTONDOWN and turn == PLAYER_PIECE:
            pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
            col = event.pos[0] // SQUARESIZE
            if is_valid_location(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, PLAYER_PIECE)
                if winning_move(board, PLAYER_PIECE):
                    label = myfont.render("Player wins!", 1, RED)
                    screen.blit(label, (40, 10))
                    game_over = True
                turn = AI_PIECE
                draw_board(board)

        # AI's turn
        if turn == AI_PIECE and not game_over:
            pygame.time.wait(500)
            pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
            col = get_best_move(board)
            if is_valid_location(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, AI_PIECE)
                if winning_move(board, AI_PIECE):
                    label = myfont.render("AI wins!", 1, YELLOW)
                    screen.blit(label, (40, 10))
                    game_over = True
                else:
                    pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
                    label = myfont.render("AI's Turn", 1, YELLOW)
                    screen.blit(label, (40, 10))  # Adjust position as needed
                    pygame.display.update()
                turn = PLAYER_PIECE
                draw_board(board)

    if game_over and game_end_time is None:
        game_end_time = pygame.time.get_ticks() + 5000  # 5 seconds

    if game_over and pygame.time.get_ticks() >= game_end_time:
        sys.exit()
