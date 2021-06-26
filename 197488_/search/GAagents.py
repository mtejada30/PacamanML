from game import Agent
from game import Directions
import distanceCalculator

import random
import numpy as np


class GAagents(Agent):

    def __init__(self, tableMode):
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

    def getAction(self, state):
        posPacman = state.getPacmanPosition()
        if self.firstGame:
            self.initTable(state.getFood())
            self.firstGame = False
        else:
            self.updateTable(posPacman)
            self.saveTableQ()

        dist, indexGhost = self.distanceGhost(state)
        distP, pills = self.distancePills(state)

        if dist < 2:
            print("AHHHHHHH UM FANTASMA")
            return self.scapeGhost(state, indexGhost)
        elif distP < 3:
            print("UHMMM QUE RICO!! ", posPacman, pills)
            return self.eatPills(state, pills)
        else:
            return self.moveAleatorio(state)


    def initTable(self, state):
        self.tableGame = np.ones((self.height_, self.width_) )
        for i in range(self.height_):
            for j in range(self.width_):
                if not state[j][i]:
                    X = self.posX[i]
                    Y = self.posY[j]
                    self.tableGame[X][Y] = -1

    def saveTableQ(self):
        nameFile = self.tableMode + "_ttttable.txt"
        row, cols = self.tableGame.shape
        with open(nameFile, 'w') as f:
            for i in range(row):
                for j in range(cols):
                    f.write(str(self.tableGame[i,j]) + "\t")
                f.write("\n")

    def updateTable(self, pos):
        #print("POs: ", pos[0], pos[1])
        self.tableGame[self.posX[pos[1]], self.posY[pos[0]]] = 0

    def distanceGhost(self, state):
        posPacman = state.getPacmanPosition()
        dist = 99999
        ghostId = 0
        for j in range(len(state.data.agentStates) - 1):
            ghostpos = state.getGhostPosition(j+1)
            distG = abs( posPacman[0] - ghostpos[0] ) + abs(posPacman[1] - ghostpos[1] )
            if distG < dist:
                dist = distG
                ghostId = j+1
        return dist, ghostId

    def scapeGhost(self, state, idx):
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

    def moveAleatorio(self, state):
        posLegal = state.getLegalPacmanActions()
        return posLegal[random.randint(0, len(posLegal)-1)]

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
                if self.tableGame[X-k][Y] == 1:
                    pos = [posPacman[0], posPacman[1] + k]
                    k_x = -k
            elif X + k <= self.height_-1:
                if self.tableGame[X+k][Y] == 1:
                    pos = [posPacman[0], posPacman[1] - k]
                    k_x = k
            if Y - k >= 0:
                if self.tableGame[X][Y-k] == 1:
                    pos = [posPacman[0] - k, posPacman[1]]
                    k_y = -k
            elif Y + k <= self.width_-1:
                if self.tableGame[X][Y+k] == 1:
                    pos = [posPacman[0] + k, posPacman[1]]
                    k_y = k
            dist = abs( posPacman[0] - pos[0] ) + abs(posPacman[1] - pos[1] )
            if dist > 0:
                print("X, Y", X, Y)
                break
        return dist, pos

    def eatPills(self, state, pos):
        posPacman = state.getPacmanPosition()
        diff = [pos[0] - posPacman[0], pos[1] - posPacman[1]]
        print(diff)
        if diff[0] < 0 and Directions.WEST in state.getLegalPacmanActions():
            return Directions.WEST
        elif diff[0] > 0 and Directions.EAST in state.getLegalPacmanActions():
            return Directions.EAST

        if diff[1] < 0 and Directions.SOUTH in state.getLegalPacmanActions():
            return Directions.SOUTH
        elif diff[1] > 0 and Directions.NORTH in state.getLegalPacmanActions():
            return Directions.NORTH

        return Directions.STOP
