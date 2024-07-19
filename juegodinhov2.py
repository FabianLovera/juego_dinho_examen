import pygame
import random

# Inicializar Pygame
pygame.init()

# Configuración de la pantalla
WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Juego del Dinosaurio")

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW_RED = (255, 150, 0)

# Cargar imágenes
dino_img1 = pygame.image.load("imagenes/dino1.png")
dino_img2 = pygame.image.load("imagenes/dino.png")
cactus_img1 = pygame.image.load("imagenes/cactus.png")
cactus_img2 = pygame.image.load("imagenes/captusuno.png")
bird_img = pygame.image.load("imagenes/cloud.png")
square_img = pygame.Surface((40, 40))
square_img.fill((255, 0, 0))
ground_img = pygame.image.load("imagenes/fondomenu.jpg")
start_img = pygame.image.load("imagenes/dinoinicio.jpg")
game_over_bg = pygame.image.load("imagenes/game_over_bg.jpeg")
scores_bg = pygame.image.load(
    "imagenes/game_over_bg.jpeg"
)  # Fondo para las puntuaciones

# Escalar imágenes
dino_img1 = pygame.transform.scale(dino_img1, (80, 100))
dino_img2 = pygame.transform.scale(dino_img2, (80, 100))
cactus_img1 = pygame.transform.scale(cactus_img1, (60, 90))
cactus_img2 = pygame.transform.scale(cactus_img2, (70, 90))
bird_img = pygame.transform.scale(bird_img, (40, 60))
ground_img = pygame.transform.scale(ground_img, (WIDTH, HEIGHT))
start_img = pygame.transform.scale(start_img, (WIDTH, HEIGHT))
game_over_bg = pygame.transform.scale(game_over_bg, (WIDTH, HEIGHT))
scores_bg = pygame.transform.scale(
    scores_bg, (WIDTH, HEIGHT)
)  # Escalar el fondo de las puntuaciones

# Cargar sonidos con manejo de errores
try:
    jump_sound = pygame.mixer.Sound("sonidos/salto.wav")
except pygame.error:
    print("No se pudo cargar 'salto.wav'. Asegúrate de que el archivo existe.")
    jump_sound = None

try:
    game_over_sound = pygame.mixer.Sound("sonidos/gameover.wav")
except pygame.error:
    print("No se pudo cargar 'gameover.wav'. Asegúrate de que el archivo existe.")
    game_over_sound = None

# Cargar música de fondo
try:
    menu_music = pygame.mixer.Sound("sonidos/menu_music.wav")
    menu_music.set_volume(0.5)
    pygame.mixer.music.load("sonidos/menu_music.wav")
    pygame.mixer.music.set_volume(0.5)
    game_music = pygame.mixer.Sound("sonidos/game_music.wav")
    game_music.set_volume(0.3)
except pygame.error:
    print(
        "No se pudo cargar la música de fondo. Asegúrate de que los archivos existen."
    )
    menu_music = None
    pygame.mixer.music = None
    game_music = None

# Definir el reloj
clock = pygame.time.Clock()

# Fuente para texto
font = pygame.font.Font(None, 36)


# Clase para el dinosaurio
class Dinosaur:
    def __init__(self):
        self.images = [dino_img1, dino_img2]
        self.image_index = 0
        self.image = self.images[self.image_index]
        self.rect = self.image.get_rect()
        self.rect.center = (100, HEIGHT - 120)
        self.jump = False
        self.double_jump = False
        self.fall_speed = 0
        self.last_jump_time = 0
        self.animation_timer = 0
        self.animation_delay = 150

    def update(self):
        keys = pygame.key.get_pressed()
        current_time = pygame.time.get_ticks()

        # Animación de caminar
        if current_time - self.animation_timer > self.animation_delay:
            self.image_index = (self.image_index + 1) % len(self.images)
            self.image = self.images[self.image_index]
            self.animation_timer = current_time

        # Detectar el primer salto
        if keys[pygame.K_SPACE] and not self.jump and not self.double_jump:
            self.jump = True
            self.fall_speed = -15
            self.last_jump_time = current_time
            if jump_sound:
                jump_sound.play()

        # Detectar el segundo salto
        elif (
            keys[pygame.K_SPACE]
            and self.jump
            and not self.double_jump
            and current_time - self.last_jump_time < 200
        ):
            self.double_jump = True
            self.fall_speed = -25
            if jump_sound:
                jump_sound.play()

        # Movimiento horizontal
        if keys[pygame.K_LEFT]:
            self.rect.x -= 8
        if keys[pygame.K_RIGHT]:
            self.rect.x += 8

        # Actualizar movimiento vertical
        if self.jump or self.double_jump:
            self.fall_speed += 1.7
            self.rect.y += self.fall_speed
            if self.rect.y >= HEIGHT - 120:
                self.rect.y = HEIGHT - 120
                self.jump = False
                self.double_jump = False

    def draw(self):
        screen.blit(self.image, self.rect)


# Clase para representar un obstáculo
class Obstacle:
    def __init__(self, image, speed, y_offset=0):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH + random.randint(300, 600)
        self.rect.y = HEIGHT - self.rect.height - y_offset
        self.speed = speed

    def update(self):
        self.rect.x -= self.speed

        # Si el obstáculo sale de la pantalla, reiniciar en una nueva posición
        if self.rect.right < 0:
            self.rect.x = WIDTH + random.randint(300, 600)
            self.rect.y = HEIGHT - self.rect.height - random.randint(0, 50)

    def draw(self):
        screen.blit(self.image, self.rect)


# Clase para el "meteoro" que cae y persigue al dinosaurio
class FallingMeteor(Obstacle):
    def update(self, dinosaur_rect):
        # Mover hacia abajo y hacia la posición del dinosaurio en el eje X
        if self.rect.x < dinosaur_rect.x:
            self.rect.x += self.speed
        elif self.rect.x > dinosaur_rect.x:
            self.rect.x -= self.speed

        self.rect.y += self.speed
        if self.rect.y > HEIGHT:
            self.rect.x = random.randint(0, WIDTH - self.rect.width)
            self.rect.y = -self.rect.height  # Reiniciar arriba de la pantalla


# Clase para representar el fondo en movimiento
class MovingBackground:
    def __init__(self, image, speed):
        self.image = image
        self.rect1 = self.image.get_rect()
        self.rect2 = self.image.get_rect()
        self.rect2.x = self.rect1.width
        self.speed = speed

    def update(self):
        self.rect1.x -= self.speed
        self.rect2.x -= self.speed
        if self.rect1.right < 0:
            self.rect1.x = self.rect2.right
        if self.rect2.right < 0:
            self.rect2.x = self.rect1.right

    def draw(self):
        screen.blit(self.image, self.rect1)
        screen.blit(self.image, self.rect2)


# Guardar la puntuación en un archivo
def save_score(score):
    with open("puntuaciones.txt", "a") as file:
        file.write(f"{score}\n")


# Cargar las puntuaciones desde un archivo
def load_scores():
    try:
        with open("puntuaciones.txt", "r") as file:
            scores = []
            for line in file.readlines():
                try:
                    scores.append(int(line.strip()))
                except ValueError:
                    # Ignorar líneas que no pueden ser convertidas a entero
                    continue
        return scores
    except FileNotFoundError:
        return []


# Mostrar la tabla de puntuaciones al final del juego
def display_scores(scores):
    screen.blit(scores_bg, (0, 0))  # Mostrar fondo de las puntuaciones personalizado
    scores.sort(reverse=True)
    title = font.render("Mejores Puntuaciones", True, BLACK)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))
    for i, score in enumerate(scores[:5]):
        score_text = font.render(f"{i + 1}. {score}", True, BLACK)
        text_rect = score_text.get_rect(center=(WIDTH // 2, 100 + i * 40))

        # Crear un fondo blanco detrás del texto
        pygame.draw.rect(screen, WHITE, text_rect)
        screen.blit(score_text, text_rect.topleft)

    pygame.display.update()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                pygame.quit()
                exit()


# Pantalla de inicio del juego
def show_start_screen():
    if menu_music:
        pygame.mixer.music.play(loops=-1)  # Reproducir música de fondo

    screen.blit(start_img, (0, 0))

    start_text = font.render(
        "Presiona ESPACIO para empezar", True, BLACK
    )  # Texto negro
    text_rect = start_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))

    # Crear un fondo blanco detrás del texto
    pygame.draw.rect(screen, WHITE, text_rect)

    # Dibujar el texto sobre el fondo blanco
    screen.blit(start_text, text_rect.topleft)

    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False

    pygame.mixer.music.fadeout(500)  # Detener música de fondo gradualmente en 500 ms


# Pantalla de fin del juego
def show_game_over_screen(score):
    screen.blit(game_over_bg, (0, 0))  # Mostrar fondo de Game Over personalizado
    game_over_text = font.render("GAME OVER", True, YELLOW_RED)
    score_text = font.render(f"Tu Puntuación: {score}", True, YELLOW_RED)
    retry_text = font.render("Presiona ESPACIO para reiniciar", True, YELLOW_RED)

    # Posicionamiento de los textos
    game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, 50))
    score_rect = score_text.get_rect(center=(WIDTH // 2, 150))
    retry_rect = retry_text.get_rect(center=(WIDTH // 2, 250))

    # Crear fondos blancos detrás de los textos
    pygame.draw.rect(screen, WHITE, game_over_rect)
    pygame.draw.rect(screen, WHITE, score_rect)
    pygame.draw.rect(screen, WHITE, retry_rect)

    # Dibujar textos sobre los fondos blancos
    screen.blit(game_over_text, game_over_rect.topleft)
    screen.blit(score_text, score_rect.topleft)
    screen.blit(retry_text, retry_rect.topleft)

    pygame.display.update()

    if game_over_sound:
        game_over_sound.play()

    save_score(score)

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False
                break
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                pygame.quit()
                exit()


# Definición de niveles y obstáculos por nivel
levels = [
    {"score": 0, "obstacles": [Obstacle(cactus_img1, 4)]},
    {"score": 500, "obstacles": [Obstacle(cactus_img1, 4), Obstacle(cactus_img2, 4)]},
    {
        "score": 1000,
        "obstacles": [
            Obstacle(cactus_img2, 4),
            Obstacle(bird_img, 4, 100),
        ],
    },
    {
        "score": 1500,
        "obstacles": [
            Obstacle(cactus_img1, 4),
            Obstacle(cactus_img2, 4),
            Obstacle(bird_img, 4, 100),
        ],
    },
    {
        "score": 2500,
        "obstacles": [
            Obstacle(cactus_img2, 4),
        ],
    },
    {
        "score": 3500,
        "obstacles": [
            Obstacle(cactus_img2, 4),
            Obstacle(bird_img, 4, 100),
        ],
    },
    {
        "score": 4500,
        "obstacles": [
            FallingMeteor(square_img, 4),
        ],
    },
    {
        "score": 5500,
        "obstacles": [
            Obstacle(cactus_img1, 4),
            Obstacle(cactus_img2, 4),
            Obstacle(bird_img, 4, 100),
            FallingMeteor(square_img, 4),
        ],
    },
    {
        "score": 6500,
        "obstacles": [
            Obstacle(cactus_img1, 4),
            Obstacle(cactus_img2, 4),
            Obstacle(bird_img, 4, 100),
            FallingMeteor(square_img, 4),
        ],
    },
    {
        "score": 15000,
        "obstacles": [
            Obstacle(cactus_img1, 4),
            Obstacle(cactus_img2, 4),
            Obstacle(bird_img, 4, 100),
            FallingMeteor(square_img, 4),
        ],
    },
]


# Bucle principal del juego
def game_loop():
    dinosaur = Dinosaur()
    obstacles = []
    score = 0
    game_over = False
    current_level = 0
    score_increment = 1  # Incremento de puntuación más rápido
    background = MovingBackground(ground_img, 4)  # Fondo en movimiento
    paused = False  # Estado de pausa

    # Reproducir música de fondo para el juego si está disponible
    if game_music:
        game_music.play(
            loops=-1
        )  # -1 indica que la música se reproducirá en un bucle indefinido

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                paused = not paused  # Alternar el estado de pausa

        if not paused:
            # Obtener el nivel actual y sus obstáculos
            level = levels[current_level]
            obstacles_to_add = level["obstacles"]

            # Generar nuevos obstáculos según el nivel actual
            if not obstacles:
                for obstacle in obstacles_to_add:
                    obstacles.append(obstacle)

            # Actualizar dinosaurio, obstáculos y fondo
            dinosaur.update()
            background.update()
            for obstacle in obstacles:
                obstacle.update()

            # Comprobar colisiones
            for obstacle in obstacles:
                if dinosaur.rect.colliderect(obstacle.rect):
                    game_over = True
                    break

            # Avanzar al siguiente nivel si se alcanza el puntaje objetivo del nivel actual
            if (
                score >= levels[current_level + 1]["score"]
                and current_level < len(levels) - 1
            ):
                current_level += 1

            # Ajustar la velocidad de los obstáculos y agregar más con el tiempo
            if score % 500 == 0 and score != 0:
                for obstacle in obstacles:
                    obstacle.speed += 1
                if (
                    random.randint(0, 100) < 10
                ):  # Probabilidad de agregar un nuevo obstáculo
                    new_obstacle = random.choice(levels[current_level]["obstacles"])
                    obstacles.append(new_obstacle)

            # Dibujar todo en la pantalla
            screen.fill(WHITE)  # Limpiar pantalla antes de dibujar
            background.draw()
            dinosaur.draw()
            for obstacle in obstacles:
                obstacle.draw()

            # Actualizar puntuación
            score += score_increment
            score_text = font.render(f"Puntuación: {int(score)}", True, BLACK)
            screen.blit(score_text, (10, 10))

            # Mostrar estado de pausa
            if paused:
                pause_text = font.render("Juego en Pausa", True, YELLOW_RED)
                screen.blit(
                    pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2)
                )

            pygame.display.update()
        else:
            pause_text = font.render("Juego en Pausa", True, YELLOW_RED)
            screen.blit(
                pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2)
            )
            pygame.display.update()
            pygame.time.wait(
                100
            )  # Esperar un corto tiempo para evitar el uso intensivo de la CPU

        clock.tick(30)

    # Detener música de fondo cuando el juego termine
    if game_music:
        game_music.fadeout(500)  # Detener música gradualmente en 500 ms

    # Mostrar pantalla de fin de juego
    show_game_over_screen(int(score))


# Iniciar el juego
show_start_screen()
while True:
    game_loop()
    scores = load_scores()
    display_scores(scores)
