import pygame
import math
import random
import networkx as nx
import colorsys
import time

from Node import *


def makeGraph(graphType):  # Create a graph using the networkx library, and convert it to a list of nodes

    nodes = []  # Initialize nodes list; this list is used for all future calculations

    # Watts-Strogatz graph
    if graphType == "ws":
        print("Creating a Watts-Strogatz graph")
        adjMatrix = nx.to_numpy_matrix(nx.watts_strogatz_graph(100, 6, 0.15))

    # Barabasi-Albert graph
    if graphType == "ba":
        print("Creating a Barabasi-Albert graph")
        adjMatrix = nx.to_numpy_matrix(nx.barabasi_albert_graph(100, 1))

    # Erdős-Rényi graph
    if graphType == "er":
        print("Creating an Erdős-Rényi graph")
        adjMatrix = nx.to_numpy_matrix(nx.erdos_renyi_graph)

    # Create the right number of nodes, and add them to the list nodes
    for i in range(0, adjMatrix.shape[0]):
        nodes.append(Node([random.randint(-1000, 1000), random.randint(-1000, 1000)]))

    # Use the adjacency matrix to set the neighbors of each node
    for i in range(0, adjMatrix.shape[0]):
        for j in range(0, adjMatrix.shape[1]):
            if adjMatrix.item(i, j) != 0:
                nodes[i].addNieghbor(nodes[j])
                nodes[j].addNieghbor(nodes[i])

    # Find and recalculate overlap; otherwise, there will be a division by zero error in future calculations
    overlap = True
    while overlap:
        overlap = False
        for i in nodes:
            for j in nodes:
                if i != j and i.pos == j.pos:
                    overlap = True
                    i.pos = [random.randint(-1000, 1000), random.randint(-1000, 1000)]

    return nodes


def degreeInfo(nList):

    xD = 0           # Maximum degree
    nD = 1000000000  # Minimum degree

    for n in nList:
        if len(n.neighbors) > xD:
            xD = len(n.neighbors)
        if len(n.neighbors) < nD:
            nD = len(n.neighbors)

    dR = xD - nD  # Degree range
    if dR == 0:
        dR = 1

    return [nD, dR]


def calcSpringInteractions(n):  # Pull between neighboring nodes

    for neighbor in node.neighbors:
        xDiff = (neighbor.pos[0] - n.pos[0])
        yDiff = (neighbor.pos[1] - n.pos[1])
        d = math.sqrt(xDiff ** 2 + yDiff ** 2)
        n.vel[0] -= (xDiff / d) * (sLength - d) * springStrength
        n.vel[1] -= (yDiff / d) * (sLength - d) * springStrength


def calcRepulsiveInteractions(n, nList):  # Repulsion between all nodes
    for other in nList:
        if n != other:
            xDiff = (other.pos[0] - n.pos[0])
            yDiff = (other.pos[1] - n.pos[1])
            n.vel[0] -= (xDiff / math.sqrt(xDiff ** 2 + yDiff ** 2)) * (rConst / (xDiff ** 2 + yDiff ** 2) ** 0.54)
            n.vel[1] -= (yDiff / math.sqrt(xDiff ** 2 + yDiff ** 2)) * (rConst / (xDiff ** 2 + yDiff ** 2) ** 0.54)


def calcCenterPull(n, c):  # Pull nodes to the center
    n.vel[0] += (c[0] - n.pos[0]) * centerPull
    n.vel[1] += (c[1] - n.pos[1]) * centerPull


def updatePos(nList, f, fI):  # f = Friction constant, fI = Friction increase
    for n in nList:
        f *= fI
        n.vel[0] *= f
        n.vel[1] *= f
        n.pos[0] += n.vel[0]
        n.pos[1] += n.vel[1]


def colorByDegree(mD, dR):  # Minimum degree, degree range

    color = list(colorsys.hls_to_rgb(0.50 * (1 - ((len(node.neighbors) - mD) / dR)), 0.5, 1))
    color[0] *= 255
    color[1] *= 255
    color[2] *= 255
    return tuple(color)


def select(mP, nList, vX, vY, z, s, nS):  # Change selected node mouse position

    # Parameters are: (nodes list, view x, view y, zoom, selected, node size)
    for n in nList:
        if math.sqrt(((mP[0] - z * (n.pos[0] + vX)) ** 2) + ((mP[1] - z * (n.pos[1] + vY)) ** 2)) < nS * z:
            if n == selected:
                return None
            else:
                return n
    else:
        return None


# Pygame setup
pygame.init()
sLength = 1500
sWidth = 700
screen = pygame.display.set_mode((sLength, sWidth))
clock = pygame.time.Clock()
mouse = pygame.mouse

# Font setup
pygame.font.init()
font = pygame.font.SysFont("freesansbold.ttf", 36)

# User control parameters
zoom = 0.03
zoomSpeed = 0.05
viewX = (sLength / 2) / zoom
viewY = (sWidth / 2) / zoom
viewSpeed = 20

# Physics model parameters
springStrength = 0.05 * 10 ** 0  # Pull of each edge; if exceeds 1, model will certainly break
springLength = 100               # Edge resting length
rConst = 3 * 10 ** 4             # Push of each node against each other node
fConst = 0.99                    # Friction (Between 1 and 0; 1 is no friction, 0 is no movement)
fIncrease = 1 - 1 * 10 ** -3     # Increase of friction over time (Between 1 and 0; 1 is no slowdown, 0 is no friction)
centerPull = 0.001               # Pull of each node towards the center

nodes = makeGraph("ws")  # Initialize graph

# Visual preference parameters
nodeSize = 300
edgeWidth = 2

# Get degree information
degInfo = degreeInfo(nodes)
minDeg = degInfo[0]
degRange = degInfo[1]

selected = None

done = False  # Program termination variable

# Physics model loop:
while not done:
    for event in pygame.event.get():
        # Program Termination controls: X button in top right corner of PyGame window or delete key on keyboard
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_DELETE:
            done = True

        # Mouse input
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            selected = select(mouse.get_pos(), nodes, viewX, viewY, zoom, selected, nodeSize)

    # Check for keyboard input
    pressed = pygame.key.get_pressed()

    if pressed[pygame.K_w]:
        viewY += viewSpeed * (1 / zoom)
    if pressed[pygame.K_s]:
        viewY -= viewSpeed * (1 / zoom)
    if pressed[pygame.K_a]:
        viewX += viewSpeed * (1 / zoom)
    if pressed[pygame.K_d]:
        viewX -= viewSpeed * (1 / zoom)
    if pressed[pygame.K_z]:
        viewX *= 1 - zoomSpeed
        viewY *= 1 - zoomSpeed
        zoom *= 1 + zoomSpeed
    if pressed[pygame.K_c]:
        viewX *= 1 + zoomSpeed
        viewY *= 1 + zoomSpeed
        zoom *= 1 - zoomSpeed

    for node in nodes:
        calcSpringInteractions(node)                     # Spring interactions
        calcCenterPull(node, [sLength / 2, sWidth / 2])  # Center pull:
        calcRepulsiveInteractions(node, nodes)           # Repulsive interactions
    updatePos(nodes, fConst, fIncrease)                  # Move nodes based on velocity and friction

    screen.fill((0, 0, 0))  # Screen color (black)

    # Draw edges:
    for node in nodes:
        for neighbor in node.neighbors:
            start = [int(zoom * (node.pos[0] + viewX)), int(zoom * (node.pos[1] + viewY))]
            end = [int(zoom * (neighbor.pos[0] + viewX)), int(zoom * (neighbor.pos[1] + viewY))]
            pygame.draw.line(screen, (100, 100, 100), start, end, edgeWidth)

    # Draw vertices:
    for node in nodes:
        color = colorByDegree(minDeg, degRange)
        pygame.draw.circle(screen, color, [int(zoom * (node.pos[0] + viewX)), int(zoom * (node.pos[1] + viewY))], int(zoom * nodeSize))

    # Redraw selected node, and its edges
    if selected != None:
        for neighbor in selected.neighbors:
            start = [int(zoom * (selected.pos[0] + viewX)), int(zoom * (selected.pos[1] + viewY))]
            end = [int(zoom * (neighbor.pos[0] + viewX)), int(zoom * (neighbor.pos[1] + viewY))]
            pygame.draw.line(screen, (255, 255, 255), start, end, edgeWidth * 2)
        pygame.draw.circle(screen, (255, 255, 255), [int(zoom * (selected.pos[0] + viewX)), int(zoom * (selected.pos[1] + viewY))],
                           int(zoom * nodeSize))

    # Draw model parameters (Text)
    screen.blit(font.render("Spring Strength: " + str(springStrength), False, (255, 255, 255)), (10, 10))
    """
    springStrength = 0.05 * 10 ** 0  # Pull of each edge; if exceeds 1, model will certainly break
    springLength = 100  # Edge resting length
    rConst = 3 * 10 ** 4  # Push of each node against each other node
    fConst = 0.99  # Friction (Between 1 and 0; 1 is no friction, 0 is no movement)
    fIncrease = 1 - 1 * 10 ** -3  # Increase of friction over time (Between 1 and 0; 1 is no slowdown, 0 is no friction)
    centerPull = 0.001  # Pull of each node towards the center
    """
    pygame.display.flip()
    clock.tick(60)  # (60) FPS

# Program termination
