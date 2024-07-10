import pygame
import sys
import time
import os

from minesweeper import Minesweeper, MinesweeperAI

HEIGHT = 10
WIDTH = 10
MINES = 10

# Colors
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
WHITE = (255, 255, 255)

# Create game
pygame.init()
size = width, height = 1200, 800
screen = pygame.display.set_mode(size)

# Fonts
OPEN_SANS = "assets/fonts/OpenSans-Regular.ttf"
smallFont = pygame.font.Font(OPEN_SANS, 20)
mediumFont = pygame.font.Font(OPEN_SANS, 28)
largeFont = pygame.font.Font(OPEN_SANS, 40)

# Compute board size
BOARD_PADDING = 20
board_width = ((2 / 3) * width) - (BOARD_PADDING * 2)
board_height = height - (BOARD_PADDING * 2)
cell_size = int(min(board_width / WIDTH, board_height / HEIGHT))
board_origin = (BOARD_PADDING, BOARD_PADDING)

# Add images
flag = pygame.image.load("assets/images/flag.png")
flag = pygame.transform.scale(flag, (cell_size, cell_size))
mine = pygame.image.load("assets/images/mine.png")
mine = pygame.transform.scale(mine, (cell_size, cell_size))

# Create game and AI agent
game = Minesweeper(height=HEIGHT, width=WIDTH, mines=MINES)
ai = MinesweeperAI(game, height=HEIGHT, width=WIDTH)

# Keep track of revealed cells, flagged cells, and if a mine was hit
revealed = set()
flags = set()
lost = False

# Show instructions initially
instructions = True

# Variables that track game state
game_started = False
game_over = False
start_ticks = 0
timer_stopped = None
game_restarted = False
final_time = None
new_high_score = False

def load_high_score(file_path="high_score.txt"):
    if not os.path.exists(file_path):
        return None
    with open(file_path, "r") as file:
        scores = file.readlines()
    return [float(score.strip()) for score in scores]

def save_high_score(score, file_path="high_score.txt"):
    with open(file_path, "a") as file:
        file.write(f"{score}\n")

def display_high_score():
    high_scores = load_high_score()
    if high_scores:
        high_score = min(high_scores)
        high_score_text = smallFont.render(f"High Score: {high_score}", True, BLACK)
        high_score_rect = high_score_text.get_rect(center=(5 * width / 6, height/4))
        screen.blit(high_score_text, high_score_rect)

# Main loop
while True:

    # Check if game quit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    screen.fill(WHITE)

    # Show game instructions
    if instructions:

        # Title
        title = largeFont.render("Play Minesweeper", True, BLACK)
        titleRect = title.get_rect()
        titleRect.center = ((width / 2), 50)
        screen.blit(title, titleRect)

        # Rules
        rules = [
            "Click a cell to reveal it.",
            "Right-click a cell to mark it as a mine.",
            "Mark all mines successfully to win!"
        ]
        for i, rule in enumerate(rules):
            line = smallFont.render(rule, True, BLACK)
            lineRect = line.get_rect()
            lineRect.center = ((width / 2), 150 + 30 * i)
            screen.blit(line, lineRect)

        # Play game button
        buttonRect = pygame.Rect((width / 4), (3 / 4) * height, width / 2, 50)
        buttonText = mediumFont.render("Play Game", True, WHITE)
        buttonTextRect = buttonText.get_rect()
        buttonTextRect.center = buttonRect.center
        pygame.draw.rect(screen, BLACK, buttonRect)
        screen.blit(buttonText, buttonTextRect)

        # Check if play button clicked
        click, _, _ = pygame.mouse.get_pressed()
        if click == 1:
            mouse = pygame.mouse.get_pos()
            if buttonRect.collidepoint(mouse):
                instructions = False
                game_started = True
                start_ticks = pygame.time.get_ticks()
                time.sleep(0.3)


        pygame.display.flip()
        continue

    # Draw board
    cells = []
    for i in range(HEIGHT):
        row = []
        for j in range(WIDTH):

            # Draw rectangle for cell
            rect = pygame.Rect(
                board_origin[0] + j * cell_size,
                board_origin[1] + i * cell_size,
                cell_size, cell_size
            )
            pygame.draw.rect(screen, GRAY, rect)
            pygame.draw.rect(screen, WHITE, rect, 3)

            # Add a mine, flag, or number if needed
            if game.is_mine((i, j)) and lost:
                screen.blit(mine, rect)
            elif (i, j) in flags:
                screen.blit(flag, rect)
            elif (i, j) in revealed:
                neighbors = smallFont.render(
                    str(game.nearby_mines((i, j))),
                    True, BLACK
                )
                neighborsTextRect = neighbors.get_rect()
                neighborsTextRect.center = rect.center
                screen.blit(neighbors, neighborsTextRect)

            row.append(rect)
        cells.append(row)
    
    # Number of Flags Left Displayed
    flags_display_x = (2 / 3) * width + BOARD_PADDING
    flags_display_y = BOARD_PADDING

    flags_display_rect = pygame.Rect(
        flags_display_x, flags_display_y,
        (width / 3) - BOARD_PADDING * 2, 50
    )

    flag_image_rect = flag.get_rect()
    flag_image_rect.topleft = flags_display_rect.topleft
    screen.blit(flag, flag_image_rect)

    flag_count_text = mediumFont.render(f" {MINES - len(flags)}", True, BLACK)
    flag_count_rect = flag_count_text.get_rect()
    flag_count_rect.midleft = flag_image_rect.midright
    screen.blit(flag_count_text, flag_count_rect)

    # Implementing the timer
    if lost or (game.mines == flags):
        game_over = True
        if timer_stopped is None:
            timer_stopped = pygame.time.get_ticks()

    if game_started:
        if not game_over:
            # Calculate elapsed time only if the game has started
            elapsed_time = (pygame.time.get_ticks() - start_ticks) / 1000
        else:
            # If game is over, keep the timer stopped
            elapsed_time = (timer_stopped - start_ticks) / 1000
            if game.mines == flags:
                final_time = elapsed_time

        mins, secs = divmod(elapsed_time, 60)
        # Display the timer nex to flag count
        font = pygame.font.Font(OPEN_SANS, 36)
        timer_surface = font.render(f"{int(mins):02}:{int(secs):02}", True, BLACK)
        # Adjust the position of the timer
        screen.blit(timer_surface, (flags_display_x + (width/6), flags_display_y))
    
    if game_restarted:
        start_ticks = pygame.time.get_ticks()
        game_restarted = False
        timer_stopped = None
        game_started = True
        game_over = False

    # High Scores
    high_scores = load_high_score()
    high_score = min(high_scores)
    if high_score is not None:
        display_high_score()

    if final_time is not None:
        if high_score is None:
            save_high_score(final_time)

        elif final_time < high_score and final_time not in high_scores:
            save_high_score(final_time)
            new_high_score = True
    
    if new_high_score:
        t = "New High Score"
        t = mediumFont.render(t, True, BLACK)
        tRect = t.get_rect()
        tRect.center = ((5 / 6) * width, (2 / 3) * height - 100)
        screen.blit(t, tRect)

    # AI Move button
    aiButton = pygame.Rect(
        (2 / 3) * width + BOARD_PADDING, (1 / 3) * height - 50,
        (width / 3) - BOARD_PADDING * 2, 50
    )
    buttonText = mediumFont.render("AI Move", True, WHITE)
    buttonRect = buttonText.get_rect()
    buttonRect.center = aiButton.center
    pygame.draw.rect(screen, BLACK, aiButton)
    screen.blit(buttonText, buttonRect)

    # Reset button
    resetButton = pygame.Rect(
        (2 / 3) * width + BOARD_PADDING, (1 / 3) * height + 20,
        (width / 3) - BOARD_PADDING * 2, 50
    )
    buttonText = mediumFont.render("Reset", True, WHITE)
    buttonRect = buttonText.get_rect()
    buttonRect.center = resetButton.center
    pygame.draw.rect(screen, BLACK, resetButton)
    screen.blit(buttonText, buttonRect)

    # Display text
    text = "Lost" if lost else "Won" if game.mines == flags else ""
    text = mediumFont.render(text, True, BLACK)
    textRect = text.get_rect()
    textRect.center = ((5 / 6) * width, (2 / 3) * height)
    screen.blit(text, textRect)

    move = None

    left, _, right = pygame.mouse.get_pressed()

    # Check for a right-click to toggle flagging
    if right == 1 and not lost:
        mouse = pygame.mouse.get_pos()
        for i in range(HEIGHT):
            for j in range(WIDTH):
                if cells[i][j].collidepoint(mouse) and (i, j) not in revealed:
                    if (i, j) in flags:
                        flags.remove((i, j))
                    else:
                        flags.add((i, j))
                    time.sleep(0.2)

    elif left == 1:
        mouse = pygame.mouse.get_pos()

        # If AI button clicked, make an AI move
        if aiButton.collidepoint(mouse) and not lost:
            move = ai.make_safe_move()
            if move is None:
                move = ai.make_random_move()
                if move is None:
                    flags = ai.mines.copy()
                    print("No moves left to make.")
                else:
                    print("No known safe moves, AI making random move.")
            else:
                print("AI making safe move.")
            time.sleep(0.2)

        # Reset game state
        elif resetButton.collidepoint(mouse):
            game = Minesweeper(height=HEIGHT, width=WIDTH, mines=MINES)
            ai = MinesweeperAI(game, height=HEIGHT, width=WIDTH)
            revealed = set()
            flags = set()
            lost = False
            game_restarted = True
            new_high_score = False
            continue

        # User-made move
        elif not lost:
            for i in range(HEIGHT):
                for j in range(WIDTH):
                    if (cells[i][j].collidepoint(mouse)
                            and (i, j) not in flags
                            and (i, j) not in revealed):
                        move = (i, j)

    # Make move and update AI knowledge
    if move:
        if game.is_mine(move):
            lost = True
        else:
            game.uncover_cell(move)  # Uncover the cell using the new method
            revealed = game.cells_revealed  # Update revealed cells
            nearby = game.nearby_mines(move)
            ai.add_knowledge(move, nearby)

    pygame.display.flip()
