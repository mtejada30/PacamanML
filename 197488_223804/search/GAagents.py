from game import Agent
from game import Directions
from game import GameStateData
import distanceCalculator

import random
import numpy as np


class GAagents(Agent):

    def __init__(self, tableMode, f):
        self.data = GameStateData()
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

        self.firstGame = True

        self.posX = {}
        self.posY = {}
        j = self.height_-1
        for i in range(self.height_):
            self.posX[i] = j
            j -= 1
        j = self.width_-1
        for i in range(self.width_):
            self.posY[i] = i
            j -= 1

        self.optionsTotal = self.splitDataReceiv(f)
        self.functionBasic= {'d1': self.distanceGhost,
                             'd2': self.distancePills,
                             'a1': self.moveAleatorio,
                             'a2': self.scapeGhost,
                             'a3': self.eatPills}

    def splitDataReceiv(self, f):
        file =  open(f, 'r')
        dataT = ""
        for line in file:
            dataT = line.rstrip('\n').split('\t')
        dataT = dataT[0]
        final = []
        d = dataT.split(',')
        d0 = d[0].split('[')
        final.append(int(d0[1]))
        for i in range(1, len(d)-1):
            d1 = d[i].split("'")
            if len(d1) > 1:
                final.append(d1[1])
            else:
                final.append(int(d1[0]))

        d0 = d[len(d)-1].split(']')[0].split("'")
        final.append(d0[1])
        return final


    def getAction(self, state):
        posPacman = state.getPacmanPosition()
        if self.firstGame:
            self.initTable(state.getFood(), state.getCapsules())
            self.firstGame = True
        else:
            self.updateTable(posPacman)
            self.saveTableQ()

        #return self.gameOptions_1(self.optionsTotal, state, posPacman)
        if self.optionsTotal[0] == 1:
            return self.gameOptions_1(self.optionsTotal, state, posPacman)
        elif self.optionsTotal[0] == 2:
            return self.gameOptions_2(self.optionsTotal, state, posPacman)
        elif self.optionsTotal[0] == 3:
            return self.gameOptions_3(self.optionsTotal, state, posPacman)
        else:
            return self.gameOptions_4(self.optionsTotal, state, posPacman)


    def initTable(self, state, capsules):
        self.tableGame = np.ones((self.height_, self.width_) )
        for i in range(self.height_):
            for j in range(self.width_):
                if not state[j][i]:
                    X = self.posX[i]
                    Y = self.posY[j]
                    self.tableGame[X][Y] = -1
        for i in range(len(capsules)):
            cap = capsules[i]
            X = self.posX[cap[1]]
            Y = self.posY[cap[0]]
            self.tableGame[X][Y] = 2

    def saveTableQ(self):
        nameFile = self.tableMode + "_ttttable.txt"
        row, cols = self.tableGame.shape
        with open(nameFile, 'w') as f:
            for i in range(row):
                for j in range(cols):
                    f.write(str(self.tableGame[i,j]) + "\t")
                f.write("\n")

    def updateTable(self, pos):
        self.tableGame[self.posX[pos[1]], self.posY[pos[0]]] = 0

    def distancePills(self, state):
        posPacman = state.getPacmanPosition()
        X, Y = self.posX[posPacman[1]], self.posY[posPacman[0]]
        axisMinor = self.width_
        if self.height_ < self.width_:
            axisMinor = self.height_

        pos = posPacman
        dist = 99999
        k_x = 0
        k_y = 0
        for k in range(1, axisMinor):
            if X - k >= 0:
                if self.tableGame[X-k][Y] >= 1:
                    pos = [posPacman[0], posPacman[1] + k]
                    k_x = -k
            if X + k <= self.height_-1:
                if self.tableGame[X+k][Y] >= 1:
                    pos = [posPacman[0], posPacman[1] - k]
                    k_x = k
            if Y - k >= 0:
                if self.tableGame[X][Y-k] >= 1:
                    pos = [posPacman[0] - k, posPacman[1]]
                    k_y = -k
            if Y + k <= self.width_-1:
                if self.tableGame[X][Y+k] >= 1:
                    pos = [posPacman[0] + k, posPacman[1]]
                    k_y = k
            dist = abs( posPacman[0] - pos[0] ) + abs(posPacman[1] - pos[1] )
            if dist > 0:
                break
        return dist, 1, pos

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

    def scapeGhost(self, state, idx, pils):
        posPacman = state.getPacmanPosition()
        ghostpos = state.getGhostPosition(idx)
        diff = [posPacman[0] - ghostpos[0], posPacman[1] - ghostpos[1]]
        if diff[0] < 0 and Directions.WEST in state.getLegalPacmanActions():
            return Directions.WEST
        elif diff[0] > 0 and Directions.EAST in state.getLegalPacmanActions():
            return Directions.EAST

        if diff[1] < 0 and Directions.SOUTH in state.getLegalPacmanActions():
            return Directions.SOUTH
        elif diff[1] > 0 and Directions.NORTH in state.getLegalPacmanActions():
            return Directions.NORTH

        return Directions.STOP

    def moveAleatorio(self, state, p, q):
        posLegal = state.getLegalPacmanActions()
        return posLegal[random.randint(0, len(posLegal)-1)]

    def eatPills(self, state, index, pos):
        posPacman = state.getPacmanPosition()
        diff = [pos[0] - posPacman[0], pos[1] - posPacman[1]]
        if diff[0] < 0 and Directions.WEST in state.getLegalPacmanActions():
            return Directions.WEST
        elif diff[0] > 0 and Directions.EAST in state.getLegalPacmanActions():
            return Directions.EAST

        if diff[1] < 0 and Directions.SOUTH in state.getLegalPacmanActions():
            return Directions.SOUTH
        elif diff[1] > 0 and Directions.NORTH in state.getLegalPacmanActions():
            return Directions.NORTH

        return Directions.STOP

    def gameOptions_1(self,vector_, state, pos):
        dist, indexGhost, _ = self.functionBasic[vector_[1]](state)
        distP, _, pills = self.functionBasic[vector_[2]](state)

        if dist < vector_[3]:
            return self.functionBasic[vector_[5]](state, indexGhost, pills)
        elif distP < vector_[4]:
            return self.functionBasic[vector_[6]](state, indexGhost, pills)
        else:
            return self.functionBasic[vector_[7]](state, indexGhost, pills)

    def gameOptions_2(self,vector_, state, pos):
        dist, indexGhost, _ = self.functionBasic[vector_[1]](state)
        distP, _, pills = self.functionBasic[vector_[2]](state)

        if dist < vector_[3]:
            return self.functionBasic[vector_[5]](state, indexGhost, pills)
        else:
            return self.functionBasic[vector_[6]](state, indexGhost, pills)

        if distP < vector_[4]:
            return self.functionBasic[vector_[7]](state, indexGhost, pills)

    def gameOptions_3(self,vector_, state, pos):
        dist, indexGhost, _ = self.functionBasic[vector_[1]](state)
        distP, _, pills = self.functionBasic[vector_[2]](state)

        if dist < vector_[3]:
            if distP < vector_[4]:
                return self.functionBasic[vector_[5]](state, indexGhost, pills)
            return self.functionBasic[vector_[6]](state, indexGhost, pills)
        else:
            return self.functionBasic[vector_[7]](state, indexGhost, pills)

    def gameOptions_4(self,vector_, state, pos):
        dist, indexGhost, _ = self.functionBasic[vector_[1]](state)
        distP, _, pills = self.functionBasic[vector_[2]](state)

        if dist < vector_[3]:
            if distP < vector_[4]:
                return self.functionBasic[vector_[5]](state, indexGhost, pills)
            else:
                return self.functionBasic[vector_[6]](state, indexGhost, pills)
            return Directions.STOP
        else:
            return self.functionBasic[vector_[7]](state, indexGhost, pills)
