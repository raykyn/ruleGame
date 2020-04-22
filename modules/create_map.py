#!/usr/bin/env python3

"""
Created after the great tutorial by catlikecoding (Jasper Flick),
found here: https://catlikecoding.com/unity/tutorials/hex-map/part-23/
"""

import json
import math
import random
import sys


class PriorityQueue:
    def __init__(self):
        self.list = []
        self.count = 0
        self.minimum = sys.maxsize

    def enqueue(self, obj):
        self.count += 1
        priority = obj.getSearchPriority()
        if priority < self.minimum:
            self.minimum = priority
        while(priority >= len(self.list)):
            self.list.append(None)
        obj.nextWithSamePriority = self.list[priority]
        self.list[priority] = obj

    def dequeue(self):
        self.count -= 1
        for i in range(self.minimum, len(self.list)):
            obj = self.list[i]
            if obj != None:
                self.list[i] = obj.nextWithSamePriority
                return obj
            self.minimum += 1
        return None
    
    def change(self, obj, oldPriority):
        current = self.list[oldPriority]
        next_obj = current.nextWithSamePriority
        if current == obj:
            self.list[oldPriority] = next_obj
        else:
            while next_obj != obj:
                current = next_obj
                next_obj = current.nextWithSamePriority
            current.nextWithSamePriority = obj.nextWithSamePriority
        self.enqueue(obj)
        self.count -= 1

    def clear(self):
        self.list = []
        self.count = 0


class Cell:
    def __init__(self, index, y, x, map):
        self.index = index
        self.y = y
        self.x = x
        self.height = 0
        
        # Up, Right, Down, Left
        self.neighbors = [None, None, None, None]

        # parameters for A* search
        self.searchHeuristic = 0
        self.distance = 0
        self.nextWithSamePriority = None
        self.searchPhase = 0

        self.set_neighbors(map)

    def getCoordinates(self):
        return self.y, self.x

    def getSearchPriority(self):
        return self.distance + self.searchHeuristic

    def set_neighbors(self, map):
        if self.y > 0:
            neighbor = map.getCellAtCoords(self.y - 1, self.x)
            self.neighbors[0] = neighbor
            neighbor.neighbors[2] = self
        if self.x > 0:
            neighbor = map.getCellAtCoords(self.y, self.x - 1)
            self.neighbors[3] = neighbor
            neighbor.neighbors[1] = self

    def __str__(self):
        return str(self.index)
    
    def __repr__(self):
        return str(self.index)


class Map:
    def __init__(self):
        self.height = 0
        self.width = 0
        self.cells = []

    def initialize(self, height, width, cities):
        self.height = height
        self.width = width
        self.generateCells(height, width)

    def generateCells(self, height, width):
        index = 0
        for i in range(height):
            for j in range(width):
                cell = Cell(index, i, j, self)
                self.cells.append(cell)
                index += 1

    def getCellAtIndex(self, index):
        return self.cells[index]

    def getCellAtCoords(self, y, x):
        return self.cells[y * self.width + x]

    def getDistanceOfCells(self, a, b):
        return math.sqrt(math.pow(a.y-b.y, 2) + math.pow(a.x-b.x, 2))

    def printMap(self):
        data = []
        for cell in self.cells:
            data.append({"x": cell.x, "y": cell.y, "height": cell.height})

        with open("map.json", mode="w", encoding="utf8") as outf:
            json.dump(data, outf)

        with open("map.json", encoding="utf8") as inf:
            content = inf.read()
            content = "var data = " + content
        
        with open("map.json", mode="w", encoding="utf8") as outf:
            outf.write(content)



class MapGenerator:
    def __init__(self, map):
        self.map = map

        # pathfinding variables
        self.searchFrontier = None
        self.searchFrontierPhase = 0

        # map generation options
        self.jitterprobability = 0.5
        self.chunkSizeMin = 30
        self.chunkSizeMax = 500
        self.landpercentage = 0.7
        self.waterlevel = 30
        self.sinkProbability = 0.2
        self.mapBorderX = 10
        self.mapBorderY = 10
        
        self.xMin = self.mapBorderX
        #self.xMax = self.map.width - self.mapBorderX
        self.xMax = self.map.width
        self.yMin = self.mapBorderY
        #self.yMax = self.map.height - self.mapBorderY
        self.yMax = self.map.height

    def createMap(self):
        if self.searchFrontier is None:
            self.searchFrontier = PriorityQueue()
        self.createLand()
        for cell in self.map.cells:
            cell.searchPhase = 0

    def getRandomCell(self):
        return self.map.getCellAtCoords(
            random.randrange(self.yMin, self.yMax),
            random.randrange(self.xMin, self.xMax))

    def createLand(self):
        landBudget = int(len(self.map.cells) * self.landpercentage)
        guard = 0
        while landBudget > 0 and guard < 10000:
            chunkSize = random.randrange(self.chunkSizeMin, self.chunkSizeMax)
            if random.random() < self.sinkProbability:
                landBudget = self.sinkTerrain(chunkSize, landBudget)
            else:
                landBudget = self.raiseTerrain(chunkSize, landBudget)
            guard += 1
        if landBudget > 0:
            print("WARNING: Failed to use up land budget.")

    def raiseTerrain(self, chunkSize, budget):
        self.searchFrontierPhase += 1
        firstCell = self.getRandomCell()
        firstCell.searchPhase = self.searchFrontierPhase
        firstCell.distance = 0
        firstCell.searchHeuristic = 0
        self.searchFrontier.enqueue(firstCell)

        #rise = 20 if random.random() < 0.25 else 10
        size = 0
        while(size < chunkSize and self.searchFrontier.count > 0):
            current = self.searchFrontier.dequeue()
            originalheight = current.height
            current.height += 10
            #current.height += random.randint(10, 10)
            #current.height = current.height + rise
            if originalheight < self.waterlevel and current.height >= self.waterlevel:
                budget -= 1
                if budget == 0:
                    break
            size += 1

            for neighbor in current.neighbors:
                if neighbor and neighbor.searchPhase < self.searchFrontierPhase:
                    neighbor.searchPhase = self.searchFrontierPhase
                    neighbor.distance = int(self.map.getDistanceOfCells(firstCell, neighbor) * 10)
                    neighbor.searchHeuristic = 10 if random.random() < self.jitterprobability else 0
                    self.searchFrontier.enqueue(neighbor)
        self.searchFrontier.clear()
        return budget

    def sinkTerrain(self, chunkSize, budget):
        self.searchFrontierPhase += 1
        firstCell = self.getRandomCell()
        firstCell.searchPhase = self.searchFrontierPhase
        firstCell.distance = 0
        firstCell.searchHeuristic = 0
        self.searchFrontier.enqueue(firstCell)

        #rise = 20 if random.random() < 0.25 else 10
        size = 0
        while(size < chunkSize and self.searchFrontier.count > 0):
            current = self.searchFrontier.dequeue()
            originalheight = current.height
            current.height -= 10
            #current.height += random.randint(10, 10)
            #current.height = current.height + rise
            if originalheight >= self.waterlevel and current.height < self.waterlevel:
                budget += 1
            size += 1

            for neighbor in current.neighbors:
                if neighbor and neighbor.searchPhase < self.searchFrontierPhase:
                    neighbor.searchPhase = self.searchFrontierPhase
                    neighbor.distance = int(self.map.getDistanceOfCells(firstCell, neighbor) * 10)
                    neighbor.searchHeuristic = 10 if random.random() < self.jitterprobability else 0
                    self.searchFrontier.enqueue(neighbor)
        self.searchFrontier.clear()
        return budget


def create_map():
    random.seed(42)

    map = Map()
    map.initialize(100, 100, 1550)
    mapgenerator = MapGenerator(map)
    mapgenerator.createMap()
    map.printMap()



if __name__ == "__main__":
    create_map()