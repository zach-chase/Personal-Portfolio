import torch
import random
import numpy as np
from collections import deque
from game import PlaySnake, Coordinate
from model import Linear_QNet, QTrainer
import matplotlib.pyplot as plt
from IPython import display

MAX_MEMORY = 100_000  # Maximum size of the replay memory
BATCH_SIZE = 1000     # Size of the batch used for training
LR = 0.001            # Learning rate for the optimizer

class Agent:
    """
    Agent class that implements the Q-learning algorithm for the Snake game.
    """
    def __init__(self):
        self.n_games = 0       # Number of games played
        self.epsilon = 0       # Randomness parameter for exploration-exploitation tradeoff
        self.gamma = 0.9       # Discount factor for future rewards
        self.memory = deque(maxlen=MAX_MEMORY) # Replay memory to store experiences
        self.model = Linear_QNet(11, 256, 3) # Neural network model for Q-learning
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma) # Trainer for the neural network

    def get_state(self, game):
        """
        Gets the current state of the game.

        Args:
            game (PlaySnake): The Snake game object.

        Returns:
            numpy.ndarray: The state representation as a numpy array.
        """
        head = game.snake[0]
        point_l = Coordinate(head.x - 20, head.y)
        point_r = Coordinate(head.x + 20, head.y)
        point_u = Coordinate(head.x, head.y - 20)
        point_d = Coordinate(head.x, head.y + 20)

        dir_l = game.direction == 'left'
        dir_r = game.direction == 'right'
        dir_u = game.direction == 'up'
        dir_d = game.direction == 'down'

        state = [
            # Danger straight
            (dir_r and game.check_crash(point_r)) or
            (dir_l and game.check_crash(point_l)) or
            (dir_u and game.check_crash(point_u)) or
            (dir_d and game.check_crash(point_d)),

            # Danger right
            (dir_u and game.check_crash(point_r)) or
            (dir_d and game.check_crash(point_l)) or
            (dir_l and game.check_crash(point_u)) or
            (dir_r and game.check_crash(point_d)),

            # Danger left
            (dir_d and game.check_crash(point_r)) or
            (dir_u and game.check_crash(point_l)) or
            (dir_r and game.check_crash(point_u)) or
            (dir_l and game.check_crash(point_d)),

            # Move direction
            dir_l,
            dir_r,
            dir_u,
            dir_d,

            # Food location
            game.food.x < game.head.x,  # food left
            game.food.x > game.head.x,  # food right
            game.food.y < game.head.y,  # food up
            game.food.y > game.head.y  # food down
        ]

        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, done):
        """
        Stores an experience in the replay memory.

        Args:
            state (numpy.ndarray): The current state.
            action (list): The action taken.
            reward (int): The reward received.
            next_state (numpy.ndarray): The next state.
            done (bool): Whether the game is over.
        """
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self):
        """
        Trains the neural network using a batch of experiences from the replay memory.
        """
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        """
        Trains the neural network using a single experience.

        Args:
            state (numpy.ndarray): The current state.
            action (list): The action taken.
            reward (int): The reward received.
            next_state (numpy.ndarray): The next state.
            done (bool): Whether the game is over.
        """
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        """
        Gets the action to take based on the current state.

        Args:
            state (numpy.ndarray): The current state.

        Returns:
            list: The action to take.
        """
        self.epsilon = 80 - self.n_games
        final_move = [0, 0, 0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move

def train():
    """
    Trains the agent by playing the Snake game.
    """
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = PlaySnake()
    while True:
        state_old = agent.get_state(game)
        final_move = agent.get_action(state_old)
        reward, done, score = game.play_step(final_move)
        state_new = agent.get_state(game)
        agent.train_short_memory(state_old, final_move, reward, state_new, done)
        agent.remember(state_old, final_move, reward, state_new, done)

        if done:
            game.start()
            agent.n_games += 1
            agent.train_long_memory()

            if score > record:
                record = score
                agent.model.save()

            print('Game', agent.n_games, 'Score', score, 'Record:', record)

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)

def plot(scores, mean_scores):
    """
    Plots the scores and mean scores during training.

    Args:
        scores (list): List of scores.
        mean_scores (list): List of mean scores.
    """
    plt.ion()
    display.clear_output(wait=True)
    display.display(plt.gcf())
    plt.clf()

    plt.plot(scores, color='black')
    plt.plot(mean_scores, color='red')

    plt.title('Scores Each Game')
    plt.xlabel('Game Number')
    plt.ylabel('Score')

    plt.ylim(ymin=0)
    plt.xlim(xmin=0)

    plt.text(len(scores) - 1, scores[-1], str(scores[-1]))
    plt.text(len(mean_scores) - 1, mean_scores[-1], str(mean_scores[-1]))
    plt.legend(['Score', 'Mean Score'], loc=2)
    plt.show()

if __name__ == '__main__':
    train()
