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
        D
        
        
    _move:
        D
        
        
    
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
        

        Parameters
        ----------
        action : TYPE
            DESCRIPTION.

        Returns
        -------
        reward : TYPE
            DESCRIPTION.
        game_over : TYPE
            DESCRIPTION.
        TYPE
            DESCRIPTION.

        """
        
        # Add frame iteration
        self.move_counter += 1
        
        # Check if user has quit game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        # 2. move
        
        current_direction = self.direction
        
        self._move(action) # update the head
        self.snake.insert(0, self.head)
        
        new_direction = self.direction
        
        
        # 3. check if game over
        reward = 0
        if current_direction != new_direction:
            reward -= 1
        game_over = False
        if self.check_crash() or self.move_counter > 100*len(self.snake):
            game_over = True
            reward = -20
            return reward, game_over, self.score

        # 4. place new food or just move
        if self.head == self.food:
            self.score += 1
            reward = 50
            self.new_food()
        else:
            self.snake.pop()
        
        # 5. update ui and clock
        self.update_display()
        self.clock.tick(self.speed)
        # 6. return game over and score
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
        

        Returns
        -------
        None.

        """
        self.display.fill(BLACK)

        for i in self.snake:
           pygame.draw.rect(self.display, GREEN, pygame.Rect(i.x+4, i.y+4, 15, 15))
       
        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, IMAGE_SIZE, IMAGE_SIZE))

        # Initialize font to be used
        font = pygame.font.SysFont('arial', 25)

        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()


    def _move(self, action):
        """
        

        Parameters
        ----------
        action : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        # [straight, right, left]

        clock_wise = ['right', 'down', 'left', 'up']
        idx = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):
            new_dir = clock_wise[idx] # no change
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx] # right turn r -> d -> l -> u
        else: # [0, 0, 1]
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx] # left turn r -> u -> l -> d

        self.direction = new_dir

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