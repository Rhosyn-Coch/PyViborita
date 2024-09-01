import pygame
import numpy as np
import sys

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (50, 200, 50)
RED = (200, 50, 50)
BLUE = (50, 50, 200)

class Block(pygame.sprite.Sprite):

    def __init__(self, color, width, height):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()

    def update(self, d_):
        self.rect.x += d_[0]
        self.rect.y += d_[1]

class Food(Block):

    def __init__(self, color, width, height, limits):
        Block.__init__(self, color, width, height)
        self.rect.x = int(np.random.randint(1, int(limits[0] // width)-1) * width)
        self.rect.y = int(np.random.randint(1, int(limits[1] // height)-1) * height)

    def draw(self, surface):
        surface.blit(self.image, self.rect[:2])

class Body:

    def __init__(self, head_size):
        self.head_size = head_size
        self.head = Block(GREEN, self.head_size, self.head_size)
        self.body = pygame.sprite.Group()
        self.body.add(self.head)

    def add(self):
        growth = Block(GREEN, self.head_size, self.head_size)
        growth.rect[:2] = self.body.sprites()[-1].rect[:2]
        self.body.add(growth)

    def update(self, position):
        new_body = pygame.sprite.Group()
        for i in range(position.shape[0]):
            body_part = self.body.sprites()[i]
            body_part.rect[:2] = position[i]
            new_body.add(body_part)
        self.body = new_body
        self.head = self.body.sprites()[0]

class Renderer:

    def __init__(self, screen, snake_body, portal_size):
        self.screen = screen
        self.snake_body = snake_body
        self.portal_size = portal_size
        self.food = None
        self.background_color = WHITE
        self.game_size = [self.screen.get_width() - 20, self.screen.get_height() - 20]
        self.game_area = pygame.Surface(self.game_size)
        self.game_area.fill(self.background_color)
        self.portals = pygame.Surface(self.portal_size)
        self.portals.fill(BLUE)

    def draw(self):
        self.screen.fill(BLACK)
        self.screen.blit(self.game_area, (10, 10))
        self.screen.blit(self.portals, (self.screen.get_width() - 10, int(self.screen.get_height()/2 - self.portal_size[1]/2 + 10)))
        self.screen.blit(self.portals, (0, int(self.screen.get_height()/2 - self.portal_size[1]/2 + 10)))
        self.game_area.fill(self.background_color)
        self.snake_body.draw(self.game_area)
        if self.food != None:
            self.food.draw(self.game_area)
        pygame.display.update()

    def restart(self):
        font = pygame.font.SysFont(None, 48)
        img1 = font.render('Press Q to exit the game.', True, WHITE)
        img2 = font.render('Press R to restart it.', True, WHITE)
        self.screen.blit(img1, (50, 50))
        self.screen.blit(img2, (50, 100))
        pygame.display.update()

    def welcome(self):
        font1 = pygame.font.SysFont(None, 48)
        font2 = pygame.font.SysFont(None, 30)
        img1 = font1.render('~~~ Snake Game ~~~', True, WHITE)
        img2 = font2.render('Welcome! Keys are:', True, WHITE)
        img3 = font2.render('Keyboard arrows for moving, W to accelerate and S to brake', True, WHITE)
        self.screen.blit(img1, (int(self.screen.get_width()/2 - img1.get_width()/2), 50))
        self.screen.blit(img2, (50, 100))
        self.screen.blit(img3, (50, 150))
        pygame.display.update()

class Game:

    def __init__(self, width, height):
        self.WIDTH, self.HEIGHT = width, height
        self.initial_variables()

    def initial_variables(self):
        self.head_size = 20
        self.velocity = 10
        self.direction = np.array([1, 0])
        self.movement = pygame.USEREVENT + 0
        self.food_event = pygame.USEREVENT + 1
        self.food = None
        self.snake = Body(self.head_size)
        self.position = np.array([self.snake.head.rect[:2]])
        self.portal_size = [10, self.head_size * 6]

    def start(self):
        pygame.init()
        self.exit = False
        self.running = True
        while not self.exit:
            screen = pygame.display.set_mode([self.WIDTH, self.HEIGHT])
            self.render = Renderer(screen, self.snake.body, self.portal_size)
            self.movement_timer = pygame.time.set_timer(self.movement, int(1000/self.velocity))
            pygame.time.set_timer(self.food_event, int(1000/1))
            clock = pygame.time.Clock()
            if self.running:
                self.initial_screen = True
                while self.initial_screen:
                    self.welcome()
            while self.running:
                self.input()
                self.update()
                self.render.draw()
                clock.tick(self.velocity)
            self.restart()
        pygame.quit()

    def input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT and self.direction[0] == 0:
                    self.direction = np.array([1, 0])
                    self.snake_body_movement()
                elif event.key == pygame.K_LEFT and self.direction[0] == 0:
                    self.direction = np.array([-1, 0])
                    self.snake_body_movement()
                elif event.key == pygame.K_DOWN and self.direction[1] == 0:
                    self.direction = np.array([0, 1])
                    self.snake_body_movement()
                elif event.key == pygame.K_UP and self.direction[1] == 0:
                    self.direction = np.array([0, -1])
                    self.snake_body_movement()
                elif event.key == pygame.K_w:
                    self.velocity += 5
                    self.movement_timer = pygame.time.set_timer(self.movement, int(1000/self.velocity))
                elif event.key == pygame.K_s:
                    self.velocity -= 5
                    if self.velocity <= 0:
                        self.velocity = 5
                    self.movement_timer = pygame.time.set_timer(self.movement, int(1000/self.velocity))
            elif event.type == self.movement:
                self.snake_body_movement()
            elif event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                pos = [int(pos[0] / self.head_size) * self.head_size, int(pos[1] / self.head_size) * self.head_size]
                self.position[0] = pos
                pygame.draw.circle(self.render.game_area, BLUE, pos, 10)
            if event.type == self.food_event and self.food == None:
                self.food = Food(RED, self.head_size, self.head_size, self.render.game_size)
                self.render.food = self.food

    def snake_body_movement(self):
        self.position[1:] = self.position[:-1]
        self.position[0] = self.position[0] + self.direction * self.head_size

    def update(self):
        if self.food != None:
            if self.snake.head.rect[0] == self.food.rect[0] and self.snake.head.rect[1] == self.food.rect[1]:
                self.eat_food()
        self.snake.update(self.position)
        self.collisions(self.snake.body.sprites()[0].rect[0], self.snake.body.sprites()[0].rect[1])

    def collisions(self, x, y):
        if x >= self.render.game_size[0]:
            if y > int(self.render.game_size[1]/2 - self.portal_size[1]/2) and y <= int(self.render.game_size[1]/2 + self.portal_size[1]/2):
                self.position[0, 0] = 0
            else:
                self.running = False
        elif x < 0:
            if y > int(self.render.game_size[1]/2 - self.portal_size[1]/2) and y <= int(self.render.game_size[1]/2 + self.portal_size[1]/2):
                self.position[0, 0] = self.render.game_size[0] - self.head_size
            else:
                self.running = False
        if y >= self.render.game_size[1]:
            self.running = False
            #self.position[0, 1] = 0
        elif y < 0:
            self.running = False
            #self.position[0, 1] = self.render.game_size[1] - self.head_size
        body = self.snake.body.copy()
        body.remove(self.snake.head)
        if pygame.sprite.spritecollideany(self.snake.head, body) != None:
            self.running = False

    def eat_food(self):
        self.snake.add()
        self.position = np.concatenate([self.position, [self.snake.body.sprites()[-1].rect[:2]]], axis=0)
        self.render.snake_body = self.snake.body
        self.food = None
        self.render.food = self.food

    def restart(self):
        self.render.restart()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self.exit = True
                elif event.key == pygame.K_r:
                    self.running = True
                    self.initial_variables()
    
    def welcome(self):
        self.render.welcome()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.initial_screen = False

if __name__ == "__main__":
    print(pygame.version.ver)
    print(np.version.version)
    game = Game(800, 800)
    game.start()