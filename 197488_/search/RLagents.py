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
        if self.index == 2:
            self.epsilon = 0.0
        self.gamma = 0.8
        self.alpha = 0.25
        self.nextPos = [0,0]

        self.numberJogos = 0
        self.episodes = 0
        self.episodes_previous = -1
        self.score_previous = 0
        self.score_ = 0
        self.reward_accumulative = 0

        self.initTableQ()

        nameFile = self.tableMode + "_episode" + "_table.txt"
        self.episodeFile = open(nameFile, 'w')
        self.episodeFile.write("numberJogos\t episode\t reward\t rewardAccumulative\n")


    def getAction(self, state):
        self.currentPos = state.getPacmanPosition()
        currentState = self.getState(self.currentPos)
        currentAction = self.chooseAction(state)

        actionTrue = self.getAction_()
        pos = self.setAction(self.currentPos)

        self.reward = self.score_ + state.getFood()[pos[0]][pos[1]]*5 #np.fmax(self.score_*1.0,-1.0) #
        legalAction = False
        if actionTrue in state.getLegalPacmanActions():
            legalAction = True
        else:
            self.reward -= 50
            actionTrue = Directions.STOP

        self.reward_accumulative += self.reward

        if self.index != 2:
            self.updateQtable(legalAction)
        self.saveEpisodes()

        if state.getScore() == 0.0 and abs(state.getScore() - self.score_previous) != 1:
            self.numberJogos += 1
            self.saveTableQ()
            if self.epsilon >= 0.0:
                if self.numberJogos > 250:
                    self.epsilon -= 0.001
            self.episodes_previous = -1
            self.reward_accumulative = 0
            print("Nro Jogos, Epsilon: ", self.numberJogos, self.epsilon)

        if self.episodes_previous >= 0:
            self.score_ = state.getScore() - self.score_previous
            self.score_previous = state.getScore()
        else:
            self.score_previous = state.getScore()

        self.episodes_previous += 1
        self.episodes += 1

        return actionTrue


    def saveEpisodes(self):
        self.episodeFile.write(str(self.numberJogos) + "\t")
        self.episodeFile.write(str(self.episodes) + "\t")
        self.episodeFile.write(str(self.reward) + "\t")
        self.episodeFile.write(str(self.reward_accumulative) )
        self.episodeFile.write("\n")


    def initTableQ(self):
        # STATES (Posições do tablero) X ACTIONS (STOP, EAST, SOUTH, WEST, NORTH)
        if(self.index == 0):
            self.table_ = np.zeros(((self.height_-1)*(self.width_-1), 5) )
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


    def chooseAction(self, state):
        if (random.random() < self.epsilon):
            self.action = random.randrange(5)
        else:
            states = self.table_[self.qstate]
            dist, idxGhost, ghostPos = self.distanceGhost(state)
            if dist < 3:
                dir = self.scapeGhost(state, idxGhost)
                if dir != Directions.STOP:
                    return dir
            self.action = np.argmax(states)
        return self.action

    def distanceGhost(self, state):
        posPacman = state.getPacmanPosition()
        dist = 99999
        ghostId = 0
        ghostpos = posPacman
        for j in range(len(state.data.agentStates) - 1):
            ghostpos = state.getGhostPosition(j+1)
            distG = abs( posPacman[0] - ghostpos[0] ) + abs(posPacman[1] - ghostpos[1] )
            if distG < dist:
                dist = distG
                ghostId = j+1
        return dist, ghostId, ghostpos

    def scapeGhost(self, state, idx):
        posPacman = state.getPacmanPosition()
        ghostpos = state.getGhostPosition(idx)
        #print(Directions.WEST, Directions.EAST, Directions.SOUTH, Directions.NORTH)
        diff = [posPacman[0] - ghostpos[0], posPacman[1] - ghostpos[1]]
        if diff[0] < 0 and Directions.WEST in state.getLegalPacmanActions():
            return 3#Directions.WEST
        elif diff[0] > 0 and Directions.EAST in state.getLegalPacmanActions():
            return 1#Directions.EAST

        if diff[1] < 0 and Directions.SOUTH in state.getLegalPacmanActions():
            return 2#Directions.SOUTH
        elif diff[1] > 0 and Directions.NORTH in state.getLegalPacmanActions():
            return 4#Directions.NORTH

        return 0#Directions.STOP
