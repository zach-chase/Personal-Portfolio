import pygame
import random
from collections import namedtuple
import numpy as np

# Start pygame
pygame.init()

# Create a namedtuple to track location on grid
Coordinate = namedtuple('Coordinate', 'x, y')

# Initialize colors to be used
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

# Initialize pixel size
IMAGE_SIZE = 20


class PlaySnake:
    """
    Class that plays the video game Snake using the library.
    
    ...
    
    Attributes
    ----------
    width : int
        The width of the pygame screen
    height: int
        The height of the pygame screen
    display: pygame.Surface
        The display of the game, using the pygame library
    clock: Clock
         A clock tracking time of game
    head: Coordinate
        Using the namedtuple Coordinate, gives x,y coordinate of snake's head
    snake: list
        List of namedtuple Coordinates of location of each point in snake's body
    direction: str
        String stating direction the snake is currently heading
    score: int
        Current score of snake game
    food: Coordinate
        Current namedtuple Coordinate of food location
    move_counter: int
        Current frame without collecting food
    

        
    Methods
    -------
    start:
        Initializes the start of a snake game. Creates a snake, initializes scores, places food.
        
    new_food:
        Places a new food in the game. Ensures food is not in snake body.
        
    play_step:
        D
        
    check_crash:
        Checks if the current location has caused a crash with wall or snake.
        
    update_display:
        Updates the pygame display at each step of game
        
    move_snake:
        Takes user input/action to determine new direction snake is moving
    """

    def __init__(self, width=640, height=480, speed=100):
        """
        Initializes a game of Snake by defining screen and calling start method

        Parameters
        ----------
        width : int, optional
            Width of the pygame screen. The default is 640.
        height : int, optional
            Height of the pygame screen. The default is 480.
        speed : int, optional
            Speed of the snake game. The default is 40.
        """
        
        # Initialize width, height, and speed
        self.width = width
        self.height = height
        self.speed = speed
    
        
        # Initialize pygame display
        self.display = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Snake')
        
        # Get clock 
        self.clock = pygame.time.Clock()
        
        # Call the start attribute
        self.start()


    def start(self):
        """
        Initializes the start of a snake game. Creates a snake, initializes scores, places food.
        """

        # Start the snake at the center of the display
        self.head = Coordinate(self.width/2, self.height/2)
        
        # Give the snake 3 points to start
        first_point = self.head
        second_point = Coordinate(self.head.x-IMAGE_SIZE, self.head.y)
        third_point = Coordinate(self.head.x-(2*IMAGE_SIZE), self.head.y)
        self.snake = [first_point, second_point, third_point]
        
        # Start snake facing to the right
        self.direction = 'right'

        # Initialize the score, food location, and frame iteration
        self.score = 0
        self.food = None
        self.move_counter = 0
        
        # Add a new food to the display
        self.new_food()


    def new_food(self):
        """
        Places a new food in the game. Ensures food is not in snake body
        """
            
        # Iterate until food is in an appropriate position
        while True:
            
            # Get random location for food
            x = random.randint(0, (self.width-IMAGE_SIZE )//IMAGE_SIZE )*IMAGE_SIZE
            y = random.randint(0, (self.height-IMAGE_SIZE )//IMAGE_SIZE )*IMAGE_SIZE
            self.food = Coordinate(x, y)
            
            # Check if food is in appropriate position
            if self.food not in self.snake:
                break


    def play_step(self, action):
        """
        Plays an entire iteration of the game

        Parameters
        ----------
        action : list
            [1, 0, 0] -> snake moves in same direction
            [0, 1, 0] -> snake turns to the right
            [0, 0, 1] -> snake turns to the left

        Returns
        -------
        reward : int
            The current reward of the game
        game_over : bool
            True if game is over. False otherwise.
        self.score: int
            Current game score.

        """
        
        # Add frame iteration
        self.move_counter += 1
        
        # Check if user has quit game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        #current_direction = self.direction
        # Get new direction and move snake
        self.move_snake(action) # update the head
        self.snake.insert(0, self.head)
        #new_direction = self.direction
        
        
        # Check if game is over
        reward = 0
        #if current_direction != new_direction:
        #    reward -= 1
        game_over = False
        if self.check_crash() or self.move_counter > 100*len(self.snake):
            game_over = True
            reward = -10
            return reward, game_over, self.score

        # Add food if needed
        if self.head == self.food:
            self.score += 1
            reward = 10
            self.new_food()
        else:
            self.snake.pop()
        
        # Update display
        self.update_display()
        self.clock.tick(self.speed)

        return reward, game_over, self.score


    def check_crash(self, location=None):
        """
        Checks if the current location has caused a crash with wall or snake

        Parameters
        ----------
        location : coordinate, optional
            Location to check if collosion has occurred. The default is None.

        Returns
        -------
        bool
            True if collision has occurred. False otherwise.
        """
        
        # Defaults to head of snake
        if location is None:
            location = self.head
        
        # Check right wall crash
        if location.x > self.width - IMAGE_SIZE:
            return True
        
        # Check left wall crash
        elif location.x < 0:
            return True
        
        # Check top wall crash
        elif location.y > self.height - IMAGE_SIZE:
            return True
        
        # Check bottom wall crash
        elif location.y < 0:
            return True
        
        # Check crash with self
        elif location in self.snake[1:]:
            return True

        # Return no crash
        return False


    def update_display(self):
        """
        Function that updates the pygame display
        """
        
        # Start with black screen
        self.display.fill(BLACK)

        # Draw the snake
        for i in self.snake:
           pygame.draw.rect(self.display, GREEN, pygame.Rect(i.x+4, i.y+4, 15, 15))
       
        # Draw the food
        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, IMAGE_SIZE, IMAGE_SIZE))

        # Add text to top of screen
        font = pygame.font.SysFont('arial', 25)
        score_text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(score_text, [0, 0])
        pygame.display.flip()


    def move_snake(self, action):
        """
        Determines which direction snake moves based off of user input or action

        Parameters
        ----------
        action : list
            [1, 0, 0] -> snake moves in same direction
            [0, 1, 0] -> snake turns to the right
            [0, 0, 1] -> snake turns to the left
        """
        
        # Create list of potential directions
        clock_wise = ['right', 'down', 'left', 'up']
        
        # Get current direction
        current_index = clock_wise.index(self.direction)

        # User input/action is to keep in same direction
        if np.array_equal(action, [1, 0, 0]):
            self.direction = clock_wise[current_index]
            
        # User input/action is to turn right
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (current_index + 1) % 4
            self.direction = clock_wise[next_idx] 
            
        # User input/action is to turn left
        else: 
            next_idx = (current_index - 1) % 4
            self.direction = clock_wise[next_idx]

        # Update new head location
        x = self.head.x
        y = self.head.y
        if self.direction == 'right':
            x += IMAGE_SIZE
        elif self.direction == 'left':
            x -= IMAGE_SIZE
        elif self.direction == 'down':
            y += IMAGE_SIZE
        elif self.direction == 'up':
            y -= IMAGE_SIZE

        self.head = Coordinate(x, y)