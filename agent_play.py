import torch
import numpy as np
from game import FruitGameAI, Direction
from model import Linear_QNet

class Agent:

    def __init__(self):
        self.model = Linear_QNet(6, 6, 3)
        self.model.load_state_dict(torch.load('./model/model6-12-3.pth'))
        self.model.eval()

    def get_state(self, game):
        dir_l = game.direction == Direction.LEFT
        dir_s = game.direction == Direction.STILL
        dir_r = game.direction == Direction.RIGHT

        state = [
            # move direction
            dir_l,
            dir_s,
            dir_r,
            
            # fruit location 
            game.fruit.x < game.basket[0].x,  # fruit left
            game.fruit.x > game.basket[0].x and game.fruit.x < game.basket[4].x,  # fruit above
            game.fruit.x > game.basket[4].x # fruit right
            ]

        return np.array(state, dtype=int)

    def get_action(self, state):
        final_move = [0,0,0]
        state0 = torch.tensor(state, dtype=torch.float)
        prediction = self.model(state0) # raw value
        move = torch.argmax(prediction).item() # choose max value -> 1
        final_move[move] = 1
        return final_move
    

def play():
    agent = Agent()
    game = FruitGameAI()
    while True:
        # get game state
        state = agent.get_state(game)

        # get action using the model
        final_move = agent.get_action(state)

        # perform move
        reward, done, score = game.play_step(final_move)

        if done:
            game.reset()
            print('Completed: Score', score)


if __name__ == '__main__':
    play()