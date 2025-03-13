# Programmed by Abhijay Panwar
import pygame
import sys
import random
import colorsys

pygame.init()

# Constants
WIDTH, HEIGHT = 900, 600
FPS = 120

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

# Fonts
font20 = pygame.font.Font('freesansbold.ttf', 20)
font30 = pygame.font.Font('freesansbold.ttf', 30)
font40 = pygame.font.Font('freesansbold.ttf', 40)

# Create the main window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong")
clock = pygame.time.Clock()

# Helper function to draw text
def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(center=(x, y))
    surface.blit(text_obj, text_rect)


# Striker Class with color drifting
class Striker:
    def __init__(self, posx, posy, width, height, speed, base_color):
        self.posx = posx
        self.posy = posy
        self.width = width
        self.height = height
        # speed is in pixels per second
        self.speed = 2 * speed  
        self.base_color = base_color
        self.color = base_color
        self.geekRect = pygame.Rect(posx, posy, width, height)
        # initialize hue for drifting effect (0.0 to 1.0)
        self.hue = random.random()
        self.geek = pygame.draw.rect(screen, self.color, self.geekRect)

    def display(self):
        self.geek = pygame.draw.rect(screen, self.color, self.geekRect)

    def update(self, yFac, dt):
        self.posy += self.speed * yFac * dt
        # Keep within bounds
        if self.posy < 0:
            self.posy = 0
        elif self.posy + self.height > HEIGHT:
            self.posy = HEIGHT - self.height
        self.geekRect = (self.posx, self.posy, self.width, self.height)

        # Update hue for smooth drifting
        self.hue += 0.2 * dt
        if self.hue > 1:
            self.hue -= 1
        r, g, b = colorsys.hsv_to_rgb(self.hue, 1, 1)
        self.color = (int(r * 255), int(g * 255), int(b * 255))

    def displayScore(self, text, score, x, y, color):
        text_surf = font20.render(text + str(score), True, color)
        text_rect = text_surf.get_rect(center=(x, y))
        screen.blit(text_surf, text_rect)

    def getRect(self):
        return self.geekRect


# Ball Class with time-based movement
class Ball:
    def __init__(self, posx, posy, radius, speed, color):
        self.posx = posx
        self.posy = posy
        self.radius = radius
        # speed in pixels per second
        self.speed = 0.75 * speed  
        self.color = color
        self.xFac = 1
        self.yFac = -1
        self.ball = pygame.draw.circle(screen, self.color, (int(self.posx), int(self.posy)), self.radius)
        self.firstTime = True

    def display(self):
        self.ball = pygame.draw.circle(screen, self.color, (int(self.posx), int(self.posy)), self.radius)

    def update(self, dt):
        self.posx += self.speed * self.xFac * dt
        self.posy += self.speed * self.yFac * dt

        # Bounce off top/bottom
        if self.posy - self.radius <= 0 or self.posy + self.radius >= HEIGHT:
            self.yFac *= -1

        # Scoring: if ball goes out on left or right
        if self.posx - self.radius <= 0 and self.firstTime:
            self.firstTime = False
            return 1   # Player 2 scores
        elif self.posx + self.radius >= WIDTH and self.firstTime:
            self.firstTime = False
            return -1  # Player 1 scores
        return 0

    def reset(self):
        self.posx = WIDTH // 2
        self.posy = HEIGHT // 2
        self.xFac *= -1  # Switch serve
        self.yFac = random.choice([-1, 1])
        self.firstTime = True

    def hit(self, random_speed_change):
        self.xFac *= -1
        # Always change color on hit
        self.color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
        # If the random speed option is enabled, adjust speed
        if random_speed_change:
            self.speed = min(self.speed + 20, 600)
        # Otherwise, do not change speed

    def getRect(self):
        return pygame.Rect(self.posx - self.radius, self.posy - self.radius, self.radius * 2, self.radius * 2)


# Game Loop with settings applied
def game_loop(settings):
    # Unpack settings
    random_speed_change = settings["random_speed_change"]
    background_on = settings["background_on"]
    win_score = settings["win_score"]

    # Create paddles and ball. Speeds are in pixels/second.
    geek1 = Striker(20, HEIGHT // 2 - 50, 10, 100, 300, GREEN)
    geek2 = Striker(WIDTH - 30, HEIGHT // 2 - 50, 10, 100, 300, GREEN)
    ball = Ball(WIDTH // 2, HEIGHT // 2, 7, 400, WHITE)

    geek1Score, geek2Score = 0, 0
    geek1YFac, geek2YFac = 0, 0

    # Load game background if enabled
    if background_on:
        try:
            game_bg = pygame.image.load("assets/game_background.png").convert()
            game_bg = pygame.transform.scale(game_bg, (WIDTH, HEIGHT))
        except:
            game_bg = None
    else:
        game_bg = None

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        if game_bg:
            screen.blit(game_bg, (0, 0))
        else:
            screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    geek2YFac = -1
                elif event.key == pygame.K_DOWN:
                    geek2YFac = 1
                elif event.key == pygame.K_w:
                    geek1YFac = -1
                elif event.key == pygame.K_s:
                    geek1YFac = 1
            if event.type == pygame.KEYUP:
                if event.key in [pygame.K_UP, pygame.K_DOWN]:
                    geek2YFac = 0
                if event.key in [pygame.K_w, pygame.K_s]:
                    geek1YFac = 0

        # Update strikers and ball
        geek1.update(geek1YFac, dt)
        geek2.update(geek2YFac, dt)

        if pygame.Rect.colliderect(ball.getRect(), geek1.getRect()):
            ball.hit(random_speed_change)
        elif pygame.Rect.colliderect(ball.getRect(), geek2.getRect()):
            ball.hit(random_speed_change)

        point = ball.update(dt)
        if point == -1:
            geek1Score += 1
        elif point == 1:
            geek2Score += 1

        if point:
            ball.reset()

        # Check win condition
        if geek1Score >= win_score or geek2Score >= win_score:
            winner = "Player 1" if geek1Score >= win_score else "Player 2"
            game_over_screen(winner, settings)
            return

        geek1.display()
        geek2.display()
        ball.display()

        geek1.displayScore("Player 1: ", geek1Score, 100, 20, WHITE)
        geek2.displayScore("Player 2: ", geek2Score, WIDTH - 100, 20, WHITE)

        pygame.display.update()


# Settings Menu Screen
def settings_menu():
    # Default settings
    random_speed_change = True
    background_on = True
    win_score = 5

    # Define buttons' rectangles
    # Toggle buttons for random speed and background, and +/– for win score
    rs_button = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 80, 300, 40)
    bg_button = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 20, 300, 40)
    score_button_minus = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 40, 60, 40)
    score_button_plus = pygame.Rect(WIDTH//2 + 90, HEIGHT//2 + 40, 60, 40)
    start_button = pygame.Rect(WIDTH//2 - 75, HEIGHT//2 + 100, 150, 50)

    settings_running = True
    while settings_running:
        clock.tick(FPS)
        screen.fill(BLACK)
        draw_text("SETTINGS", font40, GREEN, screen, WIDTH//2, 100)

        # Display current settings as text on buttons
        rs_text = "Random Ball Speed: ON" if random_speed_change else "Random Ball Speed: OFF"
        bg_text = "Background: ON" if background_on else "Background: OFF"
        draw_text(rs_text, font30, WHITE, screen, WIDTH//2, HEIGHT//2 - 60)
        draw_text(bg_text, font30, WHITE, screen, WIDTH//2, HEIGHT//2)
        draw_text("First to: " + str(win_score), font30, WHITE, screen, WIDTH//2, HEIGHT//2 + 60)

        # Draw buttons (rectangles)
        pygame.draw.rect(screen, (70, 70, 70), rs_button, 2)
        pygame.draw.rect(screen, (70, 70, 70), bg_button, 2)
        pygame.draw.rect(screen, (70, 70, 70), score_button_minus, 2)
        pygame.draw.rect(screen, (70, 70, 70), score_button_plus, 2)
        pygame.draw.rect(screen, (70, 70, 70), start_button)
        draw_text("START GAME", font30, WHITE, screen, start_button.centerx, start_button.centery)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                # Toggle random ball speed
                if rs_button.collidepoint(mx, my):
                    random_speed_change = not random_speed_change
                # Toggle background
                if bg_button.collidepoint(mx, my):
                    background_on = not background_on
                # Adjust win score
                if score_button_minus.collidepoint(mx, my):
                    if win_score > 1:
                        win_score -= 1
                if score_button_plus.collidepoint(mx, my):
                    win_score += 1
                # Start game button pressed
                if start_button.collidepoint(mx, my):
                    settings_running = False

        pygame.display.update()

    # Return settings as a dictionary
    return {
        "random_speed_change": random_speed_change,
        "background_on": background_on,
        "win_score": win_score
    }


# Game Over Screen
def game_over_screen(winner, settings):
    play_again_button = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 20, 130, 50)
    quit_button = pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 20, 130, 50)
    over_running = True
    while over_running:
        clock.tick(FPS)
        screen.fill(BLACK)
        draw_text(f"{winner} Wins!", font40, GREEN, screen, WIDTH//2, HEIGHT//2 - 50)
        pygame.draw.rect(screen, (70, 70, 70), play_again_button)
        draw_text("Play Again", font30, WHITE, screen, play_again_button.centerx, play_again_button.centery)
        pygame.draw.rect(screen, (70, 70, 70), quit_button)
        draw_text("Quit", font30, WHITE, screen, quit_button.centerx, quit_button.centery)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                over_running = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if play_again_button.collidepoint(mx, my):
                    # Return to settings menu for a new game
                    new_settings = settings_menu()
                    game_loop(new_settings)
                    return
                if quit_button.collidepoint(mx, my):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()


# Main Menu
def main_menu():
    try:
        menu_bg = pygame.image.load("assets/game_background.png").convert()
        menu_bg = pygame.transform.scale(menu_bg, (WIDTH, HEIGHT))
    except:
        menu_bg = None

    logo_img = pygame.image.load("assets/logo.png")
    logo_img = pygame.transform.scale(logo_img, (175, 175))

    play_button_rect = pygame.Rect(WIDTH//2 - 60, HEIGHT//2 - 20, 120, 40)
    quit_button_rect = pygame.Rect(WIDTH//2 - 60, HEIGHT//2 + 40, 120, 40)

    menu_running = True
    while menu_running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if play_button_rect.collidepoint(mx, my):
                    # Move to settings menu before starting the game
                    settings = settings_menu()
                    game_loop(settings)
                if quit_button_rect.collidepoint(mx, my):
                    pygame.quit()
                    sys.exit()

        if menu_bg:
            screen.blit(menu_bg, (0, 0))
        else:
            screen.fill(BLACK)

        screen.blit(logo_img, (WIDTH//2 - 85, 100))
        pygame.draw.rect(screen, (70, 70, 70), play_button_rect)
        draw_text("PLAY", font30, WHITE, screen, play_button_rect.centerx, play_button_rect.centery)
        pygame.draw.rect(screen, (70, 70, 70), quit_button_rect)
        draw_text("QUIT", font30, WHITE, screen, quit_button_rect.centerx, quit_button_rect.centery)
        draw_text("PONG MAIN MENU", font40, GREEN, screen, WIDTH//2, 100)
        pygame.display.update()


# Main
if __name__ == "__main__":
    main_menu()
    pygame.quit()
