import pygame
import random
from collections import namedtuple

# Start pygame
pygame.init()

# Initialize the game's font
FONT = pygame.font.SysFont('freesans', 20)
    
# Initialize colors to be used
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

# Initialize size of images
IMAGE_SIZE = 20
    
# Initialize namedTuple for points
Coordinate = namedtuple("Coordinate", 'x, y')

class SnakeGame:
    
    def __init__(self, width=800, height=480, speed=10):
        
        # Create class variables from inputs
        self.w = width
        self.h = height
        self.speed = speed
        
        # Create our snake in the middle of the board
        self.head = Coordinate(self.w/2, self.h/2)
        
        # Give the snake 3 points to start
        first_point = self.head
        second_point = Coordinate(self.head.x-IMAGE_SIZE, self.head.y)
        third_point = Coordinate(self.head.x-(2*IMAGE_SIZE), self.head.y)
        self.snake = [first_point, second_point, third_point]
        
        # Initialize the score, food, and direction
        self.score = 0
        self.food_location = 0
        self.direction = 'right'
        
        # Place food on the board
        self.new_food_location()
        
        # Create display of the game
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()
        
    def new_food_location(self):
        
        # Intialize new food location
        self.food_location = self.head
        
        # Make new location not in current snake's location
        while self.food_location in self.snake:
            x = random.randint(0, (self.w-IMAGE_SIZE)//IMAGE_SIZE) * IMAGE_SIZE
            y = random.randint(0, (self.h-IMAGE_SIZE)//IMAGE_SIZE) * IMAGE_SIZE
            self.food_location = Coordinate(x,y)
            
    def move(self, direction):
        
        # Get current location
        x = self.head.x
        y = self.head.y
            
        # Create new head location
        if direction == 'right':
            x += IMAGE_SIZE
        elif direction == 'left': 
            x -= IMAGE_SIZE
        elif direction == 'down': 
            y += IMAGE_SIZE
        elif direction == 'up': 
            y -= IMAGE_SIZE
                
        self.head = Coordinate(x, y)
            
    def check_crash(self):
        
        # Check if snake crashes into wall
        if self.head.x > self.w - IMAGE_SIZE:
            return True
        elif self.head.x < 0:
            return True
        elif self.head.y > self.h - IMAGE_SIZE:
            return True
        elif self.head.y < 0:
            return True
        
        # Check if snake crashes into self
        elif self.head in self.snake[1:]:
            return True

        return False
    
    def update_display(self):
        
        # Initialize screen and fill
        self.display.fill(BLACK)
        
        # Add food to screen
        pygame.draw.rect(self.display, RED, pygame.Rect(self.food_location.x, self.food_location.y, IMAGE_SIZE, IMAGE_SIZE))
        
        # Add snake to screen
        for i in self.snake:
            pygame.draw.rect(self.display, GREEN, pygame.Rect(i.x+4, i.y+4, 15, 15))

        # Add text labels to screen (score and current speed)
        text = FONT.render("Score: " + str(self.score), True, WHITE)
        score_text = FONT.render("Speed" + str(self.speed), True, WHITE)
        self.display.blit(text, [IMAGE_SIZE, 0])
        self.display.blit(score_text, [self.w*(8.5/10), 0])
        pygame.display.flip()
        
    def play_step(self):
        
        # Check for events of game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                
            # Get keypad direction
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.direction = 'left'
                elif event.key == pygame.K_RIGHT:
                    self.direction = 'right'
                elif event.key == pygame.K_UP:
                    self.direction = 'up'
                elif event.key == pygame.K_DOWN:
                    self.direction = 'down'
                    
        # Move in direction 
        self.move(self.direction)
        self.snake.insert(0, self.head)
        
        # Check if snake has crash
        game_over = False
        if self.check_crash():
            game_over = True
            return game_over, self.score

        # Check if snake is at food location
        if self.head == self.food_location:
            self.score += 1
            self.new_food_location()
            self.speed += 2
        else:
            self.snake.pop()
         
        # Update the display
        self.update_display()
        self.clock.tick(self.speed)
        
        return game_over, self.score
    



        
        
if __name__ == '__main__':
    
    # Start a new game
    game = SnakeGame()
    
    # Play until the player loses or quits
    while True:
        game_over, score = game.play_step()
        
        if game_over == True:
            break 
        
    # Display final score
    print('Final Score', score)

    # Exit out of pygame
    pygame.quit()
    
    
    
    