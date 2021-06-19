from game import Agent
from game import Directions

import random
import numpy as np


class RLagents(Agent):
    #Index: 0 -> Create Table
    #Index: 1 -> Learn Table
    #Index: 2 -> Test
    def __init__(self, index, tableMode):
        self.index = int(index)
        self.tableMode = tableMode
        self.count = 0
        self.height_ = 0
        self.width_ = 0
        if (self.tableMode == "Small"):
            self.height_ = 7
            self.width_ = 20
        elif (self.tableMode == "Medium"):
            self.height_ = 11
            self.width_ = 20
        else:
            self.height_ = 27
            self.width_ = 28

        self.action = 0
        self.epsilon = 1.0
        self.gamma = 0.9
        self.alpha = 0.1
        self.nextPos = [0,0]
        self.numberJogos = 0

        self.initTableQ()

    def initTableQ(self):
        # STATES (Posições do tablero) X ACTIONS (STOP, EAST, SOUTH, WEST, NORTH)
        if(self.index == 0):
            self.table_ = np.zeros(((self.height_-2)*(self.width_-2), 5) )
        else:
            self.readTableQ()

    def readTableQ(self):
        nameFile = self.tableMode + "_table.txt"
        self.table_ = []
        aux  = []
        with open(nameFile, 'r') as f:
            for line in f:
                line_ = line.rstrip('\n').split('\t')
                for i in range(len(line_)-1):
                    aux.append(float(line_[i]))
                self.table_.append(np.array(aux))
                aux = []
        self.table_ = np.array(self.table_)

    def saveTableQ(self):
        nameFile = self.tableMode + "_table.txt"
        row, cols = self.table_.shape
        with open(nameFile, 'w') as f:
            for i in range(row):
                for j in range(cols):
                    f.write(str(self.table_[i,j]) + "\t")
                f.write("\n")

    def getAction(self, state):
        self.currentPos = state.getPacmanPosition()

        currentState = self.getState(self.currentPos)
        currentAction = self.chooseAction()

        self.reward = 0
        actionTrue = self.getAction_()
        legalAction = False
        if actionTrue in state.getLegalPacmanActions():
            legalAction = True
        else:
            self.reward -= 50
            actionTrue = Directions.STOP
        self.reward += state.getScore()

        self.updateQtable(legalAction)

        """
        if self.numberJogos != numberJogos:
            self.epsilon -= 0.08
            self.numberJogos = numberJogos
            print("Jogos jugados: ", self.numberJogos)
        """
        self.epsilon -= 0.0008
        self.saveTableQ()
        return actionTrue


    def updateQtable(self, legalAction):
        qactual = self.table_[self.qstate, self.action]
        nexState = self.getState(self.setAction(self.currentPos))
        if not legalAction:
            nexState = self.getState(self.currentPos)

        qnext = np.max(self.table_[nexState])
        newValueQ = qactual + self.alpha*(self.reward + self.gamma*qnext - qactual)
        self.table_[self.qstate, self.action] = newValueQ


    def setAction(self, pos):
        if self.action == 0:
            return pos
        elif self.action == 1:
            return (pos[0]-1, pos[1])
        elif self.action == 2:
            return (pos[0], pos[1]-1)
        elif self.action == 3:
            return (pos[0]+1, pos[1])
        return (pos[0], pos[1]+1)

    def getAction_(self):
        if self.action == 0:
            return Directions.STOP
        elif self.action == 1:
            return Directions.EAST
        elif self.action == 2:
            return Directions.SOUTH
        elif self.action == 3:
            return Directions.WEST
        return Directions.NORTH

    def getState(self, pos_):
        #conversion indx*c + indy
        self.qstate = (pos_[1]-1)*(self.width_-2) + (pos_[0]-1)
        return self.qstate

    def chooseAction(self):
        if (random.random() < self.epsilon):
            self.action = random.randrange(5)
        else:
            states = self.table_[self.qstate]
            self.action = np.argmax(states)
        return self.action





"""
Init TabelaQ
CHoose Action
RUn Action
Reward
Update State (TabelaQ)
"""
