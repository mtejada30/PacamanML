from game import Agent
from game import Directions
import random

class DumbAgent(Agent):
    #Agent go to west XD

    def getAction(self, state):
        print ("Location: ", state.getPacmanPosition())
        print ("Actions Available: ", state.getLegalPacmanActions())
        if Directions.WEST in state.getLegalPacmanActions():
            print ("Goint to West")
            return Directions.WEST
        else:
            print("Not goint to west")
            return Directions.STOP

class RandomAgent21(Agent):
    #Agent go to west XD
    def __init__(self, index):
        self.index = index

    def getAction(self, state):
        print ("Location: ", state.getPacmanPosition())
        print ("Actions Available: ", state.getLegalPacmanActions())

        dir = random.choice(state.getLegalPacmanActions())
        if dir in state.getLegalPacmanActions():
            print ("Goint to West")
            return dir
        else:
            print("Not goint to west")
            return Directions.STOP

class ReflexAgent(Agent):
    def getAction(self, state):
        print ("Location: ", state.getPacmanPosition())
        print ("Score: ", state.getScore())
        print ("LOcation of food: ", state.getFood())
        print ("Location ghost: ", state.getGhostPosition(1))

        dir = random.choice(state.getLegalPacmanActions())
        if dir in state.getLegalPacmanActions():
            print ("Goint to West")
            return dir
        else:
            print("Not goint to west")
            return Directions.STOP
