import pygame, random, time
from pygame.locals import *

# CONSTANTS
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
SPEED = 20
GRAVITY = 2.5
GAME_SPEED = 15

GROUND_WIDTH = 2 * SCREEN_WIDTH
GROUND_HEIGHT = 100

PIPE_WIDTH = 80
PIPE_HEIGHT = 500
PIPE_GAP = 150

# Initialize Pygame and Sound Mixer
pygame.init()
pygame.mixer.init()

# Load resources
assets = {
    "background": pygame.transform.scale(pygame.image.load('assets/sprites/background-day.png'), (SCREEN_WIDTH, SCREEN_HEIGHT)),
    "begin_image": pygame.image.load('assets/sprites/message.png').convert_alpha(),
    "bird_images": [
        pygame.image.load('assets/sprites/bluebird-upflap.png').convert_alpha(),
        pygame.image.load('assets/sprites/bluebird-midflap.png').convert_alpha(),
        pygame.image.load('assets/sprites/bluebird-downflap.png').convert_alpha()
    ],
    "ground_image": pygame.transform.scale(pygame.image.load('assets/sprites/base.png').convert_alpha(), (GROUND_WIDTH, GROUND_HEIGHT)),
    "pipe_image": pygame.image.load('assets/sprites/pipe-green.png').convert_alpha(),
    "wing_sound": pygame.mixer.Sound('assets/audio/wing.wav'),
    "hit_sound": pygame.mixer.Sound('assets/audio/hit.wav')
}

class Bird(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.images = assets["bird_images"]
        self.current_image = 0
        self.image = self.images[self.current_image]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect[0] = SCREEN_WIDTH / 6
        self.rect[1] = SCREEN_HEIGHT / 2
        self.speed = SPEED

    def update(self):
        self.current_image = (self.current_image + 1) % 3
        self.image = self.images[self.current_image]
        self.speed += GRAVITY
        self.rect[1] += self.speed

    def bump(self):
        self.speed = -SPEED

    def begin(self):
        self.update()

class Pipe(pygame.sprite.Sprite):
    def __init__(self, inverted, xpos, ysize):
        super().__init__()
        self.image = pygame.transform.scale(assets["pipe_image"], (PIPE_WIDTH, PIPE_HEIGHT))
        self.rect = self.image.get_rect()
        self.rect[0] = xpos

        if inverted:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect[1] = -(self.rect[3] - ysize)
        else:
            self.rect[1] = SCREEN_HEIGHT - ysize

        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect[0] -= GAME_SPEED

class Ground(pygame.sprite.Sprite):
    def __init__(self, xpos):
        super().__init__()
        self.image = assets["ground_image"]
        self.rect = self.image.get_rect()
        self.rect[0] = xpos
        self.rect[1] = SCREEN_HEIGHT - GROUND_HEIGHT

    def update(self):
        self.rect[0] -= GAME_SPEED

def is_off_screen(sprite):
    return sprite.rect[0] < -(sprite.rect[2])

def get_random_pipes(xpos):
    size = random.randint(100, 300)
    pipe = Pipe(False, xpos, size)
    pipe_inverted = Pipe(True, xpos, SCREEN_HEIGHT - size - PIPE_GAP)
    return pipe, pipe_inverted

def handle_events():
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()
        if event.type == KEYDOWN:
            if event.key == K_SPACE or event.key == K_UP:
                bird.bump()
                assets["wing_sound"].play()
                return False
    return True

def check_collisions():
    if (pygame.sprite.groupcollide(bird_group, ground_group, False, False, pygame.sprite.collide_mask) or
            pygame.sprite.groupcollide(bird_group, pipe_group, False, False, pygame.sprite.collide_mask)):
        assets["hit_sound"].play()
        time.sleep(1)
        return True
    return False

# Main game setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Flappy Bird')

bird_group = pygame.sprite.Group()
bird = Bird()
bird_group.add(bird)

ground_group = pygame.sprite.Group()
for i in range(2):
    ground = Ground(GROUND_WIDTH * i)
    ground_group.add(ground)

pipe_group = pygame.sprite.Group()
for i in range(2):
    pipes = get_random_pipes(SCREEN_WIDTH * i + 800)
    pipe_group.add(pipes[0])
    pipe_group.add(pipes[1])

clock = pygame.time.Clock()
begin = True

# Start screen loop
while begin:
    clock.tick(15)
    begin = handle_events()

    screen.blit(assets["background"], (0, 0))
    screen.blit(assets["begin_image"], (120, 150))

    if is_off_screen(ground_group.sprites()[0]):
        ground_group.remove(ground_group.sprites()[0])
        new_ground = Ground(GROUND_WIDTH - 20)
        ground_group.add(new_ground)

    bird.begin()
    ground_group.update()
    bird_group.draw(screen)
    ground_group.draw(screen)
    pygame.display.update()

# Main game loop
while True:
    clock.tick(15)
    if not handle_events():
        continue

    screen.blit(assets["background"], (0, 0))

    if is_off_screen(ground_group.sprites()[0]):
        ground_group.remove(ground_group.sprites()[0])
        new_ground = Ground(GROUND_WIDTH - 20)
        ground_group.add(new_ground)

    if is_off_screen(pipe_group.sprites()[0]):
        pipe_group.remove(pipe_group.sprites()[0])
        pipe_group.remove(pipe_group.sprites()[0])
        pipes = get_random_pipes(SCREEN_WIDTH * 2)
        pipe_group.add(pipes[0])
        pipe_group.add(pipes[1])

    bird_group.update()
    ground_group.update()
    pipe_group.update()

    bird_group.draw(screen)
    pipe_group.draw(screen)
    ground_group.draw(screen)
    pygame.display.update()

    if check_collisions():
        break
