import torch
import random
import numpy as np
from collections import deque
from game import PlaySnake, Coordinate
from model import Linear_QNet, QTrainer
import matplotlib.pyplot as plt
from IPython import display

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Agent:

    def __init__(self):
        self.n_games = 0
        self.epsilon = 0 # randomness
        self.gamma = 0.9 # discount rate
        self.memory = deque(maxlen=MAX_MEMORY) # popleft()
        self.model = Linear_QNet(11, 256, 3) #256
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)


    def get_state(self, game):
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
        self.memory.append((state, action, reward, next_state, done)) # popleft if MAX_MEMORY is reached

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)
        #for state, action, reward, nexrt_state, done in mini_sample:
        #    self.trainer.train_step(state, action, reward, next_state, done)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # random moves: tradeoff exploration / exploitation
        self.epsilon = 80 - self.n_games
        final_move = [0,0,0]
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
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = PlaySnake()
    while True:
        # get old state
        state_old = agent.get_state(game)

        # get move
        final_move = agent.get_action(state_old)

        # perform move and get new state
        reward, done, score = game.play_step(final_move)
        state_new = agent.get_state(game)

        # train short memory
        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        # remember
        agent.remember(state_old, final_move, reward, state_new, done)

        if done:
            # train long memory, plot result
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
    
    # Update display and clear output
    plt.ion()
    display.clear_output(wait=True)
    display.display(plt.gcf())
    plt.clf()
    
    # Plot current score and mean score
    plt.plot(scores, color = 'black')
    plt.plot(mean_scores, color = 'red')
    
    # Add lables and title
    plt.title('Scores Each Game')
    plt.xlabel('Game Number')
    plt.ylabel('Score')
    
    # Set x and y lim
    plt.ylim(ymin=0)
    plt.xlim(xmin=0)
    
    # Add text for most recent score and mean score
    plt.text(len(scores)-1, scores[-1], str(scores[-1]))
    plt.text(len(mean_scores)-1, mean_scores[-1], str(mean_scores[-1]))
    plt.legend(['Score', 'Mean Score'], loc=2)
    plt.show()


if __name__ == '__main__':
    train()
