
import math
import pygame
from pygame.locals import *
import sys
import pdb
import time

def printArray(array):
    for a in array:
        print a

def fnManhattan(dx,dy):
    return dx + dy

def fnEuclidean(dx,dy):
    return math.sqrt(dx*dx + dy*dy)

def fnOctile(dx,dy):
    f = math.sqrt(2) - 1
    if dx < dy:
        return f * dx + dy
    else:
        return f * dy + dx

def fnChebyshev(dx,dy):
    return dx if dx > dy else dy


def cmpsort(nodeA,nodeB):
    if nodeA.f > nodeB.f:
        return 1
    if nodeA.f < nodeB.f:
        return -1
    return 0

class Node():
    def __init__(self):
        self.x = 0
        self.y = 0
        self.g = 0
        self.f = 0
        self.h = 0
        self.closed = False
        self.opened = False
        self.parent = None
        self.isWall = False

    def __str__(self):
        return 'Node[x=%d y=%d g=%f f=%f h=%f closed=%s opened=%s]' % (self.x,self.y,self.g,self.f,self.h,str(self.closed),str(self.opened))


class Grid():
    def __init__(self,width,height):
        self.width = width
        self.height = height
        self.nodes = []
        for row in range(self.height):
            rows = []
            for col in range(self.width):
                n = Node()
                n.x = col
                n.y = row
                rows.append(n)
            self.nodes.append(rows)

    def setWall(self,list):
        for v in list:
            n = self.getNodeAt(v[0],v[1])
            if n:
                n.isWall = True

    def getNodeAt(self,x,y):
        if x>=0 and y>=0 and x<self.width and y<self.height:
            return self.nodes[y][x]
        return None

    def __addnodes(self,result,x,y):
        n = self.getNodeAt(x,y)
        if n and not n.isWall:
            result.append(n)

    def getNeighbors(self,node):
        neighbors = []
        self.__addnodes(neighbors,node.x,node.y - 1)        # up
        self.__addnodes(neighbors,node.x + 1,node.y - 1)    # up right
        self.__addnodes(neighbors,node.x + 1,node.y)        # right
        self.__addnodes(neighbors,node.x + 1,node.y + 1)    # right down
        self.__addnodes(neighbors,node.x ,node.y + 1)       # down
        self.__addnodes(neighbors,node.x - 1,node.y + 1)    # left down
        self.__addnodes(neighbors,node.x - 1,node.y)        # left
        self.__addnodes(neighbors,node.x - 1,node.y - 1)    # left up
        return neighbors



class AStarFinder():
    def __init__(self,grid):
        self.openList = []
        self.grid = grid
        self.startNode = None
        self.endNode = None
        self.heuristic = fnOctile#fnEuclidean#fnManhattan #function call

    def openListPop(self):
        if len(self.openList) > 0:
            node = self.openList[0]
            self.openList = self.openList[1:]
            return node
        return None

    def findPath(self,start,end):
        self.startNode = self.grid.getNodeAt(start[0],start[1])
        self.endNode = self.grid.getNodeAt(end[0],end[1])

        self.startNode.g = 0
        self.startNode.f = 0

        self.openList.append(self.startNode)
        self.startNode.opened = True

        node = self.openListPop()
        while node :
            node.closed = True
            if node.x == self.endNode.x and node.y == self.endNode.y:
                return

            neighbors = self.grid.getNeighbors(node)
            for neighbor in neighbors:
                if neighbor.closed or neighbor.opened:
                    continue
                x = neighbor.x
                y = neighbor.y

                ng = node.g + (1 if x-node.x ==0 or y-node.y==0 else math.sqrt(2))

                if not neighbor.opened or ng < neighbor.g:
                    neighbor.g = ng
                    neighbor.h = self.heuristic(math.fabs(x - self.endNode.x),math.fabs(y - self.endNode.y))
                    neighbor.f = neighbor.g + neighbor.h
                    neighbor.parent = node

                    if not neighbor.opened:
                        self.openList.append(neighbor)
                        neighbor.opened = True

                    self.openList.sort(cmpsort)

            node = self.openListPop()




def drawcircle(ctx,color,x,y):
    pygame.draw.circle(ctx,color,(20*x+12,20*y+12),10)

mask = {}
result = []
nodeA = (0,0)
nodeB = (19,29)
fnIdx = 0

def refreshResult():
    global result,nodeA,nodeB,mask,fnIdx

    fnArray = [fnOctile,fnEuclidean,fnManhattan]

    g = Grid(32,32)
    g.setWall(mask.values())
    f = AStarFinder(g)
    f.heuristic = fnArray[fnIdx]

    st = time.time()
    f.findPath(nodeA,nodeB)
    st = time.time() - st
    print '[%d]use time:%f' % (fnIdx,st)

    p = f.endNode
    result= []
    while p:
        result.append(p)
        p = p.parent

def onKeyDown(key):
    global fnIdx
    if key == K_1:
        fnIdx = 0
        print 'fnOctile'
    if key == K_2:
        fnIdx = 1
        print 'fnEuclidean'
    if key == K_3:
        fnIdx = 2
        print 'fnManhattan'
    refreshResult()

def onMouseButtonUp(x,y):
    global mask
    xx = x/20
    yy = y/20
    skey = str(xx)+'-'+str(yy)
    mask[skey]=(xx,yy)

    refreshResult()

if __name__ == '__main__':
    color_read = (0xff,0x0,0x0)
    color_blue = (0x0,0x0,0xff)
    color_green = (0x0,0xff,0x0)
    color_gray = (0xaf,0xaf,0xaf)

    run = True
    pygame.display.init()
    screen = pygame.display.set_mode((640+1,640+1))
    pygame.display.set_caption('findpath')
    clock = pygame.time.Clock()

    while run:
        screen.fill((0,0,0))
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == QUIT:
                run = False
            elif event.type == KEYDOWN:
                if event.key == K_q:
                    run = False
                onKeyDown(event.key)
            elif event.type == MOUSEBUTTONUP:
                onMouseButtonUp(event.pos[0],event.pos[1])

        # draw path
        for nn in result:
            drawcircle(screen,color_green,nn.x,nn.y)
        # draw wall
        for m in mask.values():
            drawcircle(screen,color_gray,m[0],m[1])

        # draw start point
        drawcircle(screen,color_read,nodeA[0],nodeA[1])
        # draw end point
        drawcircle(screen,color_blue,nodeB[0],nodeB[1])
        pygame.display.update()
    pygame.quit()
