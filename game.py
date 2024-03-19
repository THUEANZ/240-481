import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

# initialize Pygame
pygame.init()
font = pygame.font.SysFont('Arial', 32)

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    STILL = 3

Point = namedtuple('Point', 'x, y')

# colors
WHITE = (255, 255, 255)
ORANGE = (255, 100, 0)
GREEN1 = (0, 255, 0)
BROWN1 = (100, 100, 50)
BROWN2 = (150, 150, 100)
BLACK = (0,0,0)

BLOCK_SIZE = 20
SPEED = 150

# define game objects
class FruitGameAI:
    def __init__(self, w = 400, h = 600):
        self.w = w
        self.h = h
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Fruit')
        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self):
        # init game state
        self.direction = Direction.STILL
        self.leftmost = Point(self.w/2-(2*BLOCK_SIZE), self.h-BLOCK_SIZE)
        self.basket = [self.leftmost, 
                      Point(self.leftmost.x+(BLOCK_SIZE), self.leftmost.y),
                      Point(self.leftmost.x+(2*BLOCK_SIZE), self.leftmost.y),
                      Point(self.leftmost.x+(3*BLOCK_SIZE), self.leftmost.y),
                      Point(self.leftmost.x+(4*BLOCK_SIZE), self.leftmost.y)]
        
        self.score = 0
        self.speed = 0
        self.fruit = None
        self.place_fruit()

    def place_fruit(self):
        x = random.randint(0, (self.w-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        y = -BLOCK_SIZE
        self.fruit = Point(x, y)

    def play_step(self, action):
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # 2. move
        self.fall() # update fruit
        self.move(action) # update basket

        # 3. check if game over
        reward = 0
        game_over = False
        if self.fruit.y > self.h:
            game_over = True
            reward -= 10
            return reward, game_over, self.score

        # 4. place new fruit
        if self.fruit in self.basket:
            self.score += 1
            # reach limit score
            if (self.score == 100):
                return reward, game_over, self.score
            self.speed += 1
            reward = 10
            self.place_fruit()

        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED + self.speed)

        # 6. return game over and score
        return reward, game_over, self.score


    def _update_ui(self):
        self.display.fill(BLACK)
        for pt in self.basket: # draw basket
            pygame.draw.rect(self.display, BROWN1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, BROWN2, pygame.Rect(pt.x+4, pt.y+4, 12, 12))
        # draw fruit
        pygame.draw.rect(self.display, ORANGE, pygame.Rect(self.fruit.x, self.fruit.y, BLOCK_SIZE, BLOCK_SIZE))
        pygame.draw.rect(self.display, GREEN1, pygame.Rect(self.fruit.x+7, self.fruit.y, 5, 6))
        
        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()

    def fall(self):
        x = self.fruit.x
        y = self.fruit.y
        y += BLOCK_SIZE
        self.fruit = Point(x, y)

    def move(self, action):
        # [left, still, right]
        move = [Direction.LEFT, Direction.STILL, Direction.RIGHT]

        if np.array_equal(action, [1, 0, 0]):
            new_dir = move[0] # go left
        elif np.array_equal(action, [0, 1, 0]):
            new_dir = move[1] # stay still
        elif np.array_equal(action, [0, 0, 1]):
            new_dir = move[2] # go right

        self.direction = new_dir

        if self.direction == Direction.RIGHT and self.basket[4].x < self.w - BLOCK_SIZE:
            modified_basket = [Point(x+BLOCK_SIZE, y) for x, y in self.basket]
            self.basket = modified_basket
        elif self.direction == Direction.LEFT and self.basket[0].x > 0:
            modified_basket = [Point(x-BLOCK_SIZE, y) for x, y in self.basket]
            self.basket = modified_basket