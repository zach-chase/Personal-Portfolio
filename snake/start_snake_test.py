#snake_game.py

import pygame


pygame.init()



class SnakeGame:
    
    def __init__(self, w=800, h=500):
        self.w = w
        self.h = h
        self.speed = 10
        
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()
        
        self.direction = 'right'
        
        self.head = (self.w/2, self.h/2)
        self.snake = [self.head, (self.head, self.head), (self.head, self.head)]
        
        self.score = 0
        self.food = None
        
   