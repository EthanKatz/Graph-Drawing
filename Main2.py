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
        adjMatrix = nx.to_numpy_matrix(nx.barabasi_albert_graph(1000, 1))

    # Erdős-Rényi graph
    if graphType == "er":
        print("Creating an Erdős-Rényi graph")
        adjMatrix = nx.to_numpy_matrix(nx.erdos_renyi_graph(100, 0.03))

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


def calcSpringInteractions(n, sL, sS):  # Pull between neighboring nodes

    for neighbor in node.neighbors:
        xDiff = (neighbor.pos[0] - n.pos[0])
        yDiff = (neighbor.pos[1] - n.pos[1])
        d = math.sqrt(xDiff ** 2 + yDiff ** 2)
        n.vel[0] -= (xDiff / d) * (sL - d) * sS
        n.vel[1] -= (yDiff / d) * (sL - d) * sS


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


def updatePos(nList, f):  # f = Friction constant, fI = Friction increase
    for n in nList:
        n.vel[0] *= f
        n.vel[1] *= f
        n.pos[0] += n.vel[0]
        n.pos[1] += n.vel[1]


def colorByDegree(mD, dR, b):  # Minimum degree, degree range, brightness

    color = list(colorsys.hls_to_rgb(0.50 * (1 - ((len(node.neighbors) - mD) / dR)), b, 1))
    color[0] *= 255
    color[1] *= 255
    color[2] *= 255
    return tuple(color)


def select(mP, nList, vX, vY, z, s, nS):  # Change selected node mouse position

    # Parameters are: (nodes list, view x, view y, zoom, selected, node size)
    for n in nList:
        if math.sqrt(((mP[0] - z * (n.pos[0] + vX)) ** 2) + ((mP[1] - z * (n.pos[1] + vY)) ** 2)) < nS * z:
            if n == s:
                return None
            else:
                return n
    else:
        return None


# Pygame setup
pygame.init()
sLength = 1000
sWidth = 700
screen = pygame.display.set_mode((sLength + 300, sWidth))
clock = pygame.time.Clock()
mouse = pygame.mouse
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
springLength = 1000              # Edge resting length
rConst = 5 * 10 ** 4             # Push of each node against each other node
fConst = 0.95                    # Friction (Between 1 and 0; 1 is no friction, 0 is no movement)
fIncrease = 0.999                # Increase of friction over time (Between 1 and 0; 1 is no slowdown, 0 is no friction)
centerPull = 0.01                # Pull of each node towards the center

# List for user control of physics parameters
physParams = [
    {"val": springStrength, "name": "Spring Strength"},
    {"val": springLength, "name": "Spring Length"},
    {"val": rConst, "name": "Repulsion Strength"},
    {"val": fConst, "name": "Friction Constant"},
    {"val": fIncrease, "name": "Friction Increase"},
    {"val": centerPull, "name": "Center Pull"},
]
for param in physParams:
    param["color"] = (150, 150, 150)

paramInput = ""  # Variable to store user input for editing parameters

nodes = makeGraph("ba")  # Initialize graph

# Visual preference parameters
nodeSize = 300
edgeWidth = 2

minDeg, degRange = degreeInfo(nodes)  # Get degree information

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
            if type(selected) == dict:
                selected["color"] = (150, 150, 150)
            mouseX, mouseY = mouse.get_pos()
            selected = select((mouseX, mouseY), nodes, viewX, viewY, zoom, selected, nodeSize)
            for i in range(0, len(physParams)):
                if 1200 < mouseX < 1200 + font.size("Edit")[0] and \
                        55 + i * 70 < mouseY < 55 + i * 70 + font.size(str(round(physParams[i]["val"], 5)))[1]:
                    selected = physParams[i]
                    physParams[i]["color"] = (0, 255, 0)
            if 1010 < mouseX < 1010 + font.size("Reconfigure")[0] and \
                    40 + len(physParams) * 70 < mouseY < 40 + len(physParams) * 70 + font.size("Reconfigure")[1]:
                print("Reconfiguring...")
                fConst = 0.95
                fIncrease = 0.999
                for node in nodes:
                    node.notMovingTick = 0
                    node.vel = [0, 0]
                    node.pos = [random.randint(-1000, 1000), random.randint(-1000, 1000)]
            elif 1010 < mouseX < 1010 + font.size("Set")[0] and \
                    100 + len(physParams) * 70 < mouseY < 100 + len(physParams) * 70 + font.size("Reconfigure")[1]:
                fConst = 0.0
                fIncrease = 0.0
                for node in nodes:
                    node.notMovingTick = 300
                    node.vel = [0, 0]
            elif 1100 < mouseX < 1100 + font.size("Unset")[0] and \
                    100 + len(physParams) * 70 < mouseY < 100 + len(physParams) * 70 + font.size("Reconfigure")[1]:
                fConst = 0.80
                fIncrease = 1
                for node in nodes:
                    node.notMovingTick = 0
        # Keyboard input used for changing parameters
        if type(selected) == dict and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_PERIOD:
                paramInput += "."
            elif event.key == pygame.K_0:
                paramInput += "0"
            elif event.key == pygame.K_1:
                paramInput += "1"
            elif event.key == pygame.K_2:
                paramInput += "2"
            elif event.key == pygame.K_3:
                paramInput += "3"
            elif event.key == pygame.K_4:
                paramInput += "4"
            elif event.key == pygame.K_5:
                paramInput += "5"
            elif event.key == pygame.K_6:
                paramInput += "6"
            elif event.key == pygame.K_7:
                paramInput += "7"
            elif event.key == pygame.K_8:
                paramInput += "8"
            elif event.key == pygame.K_9:
                paramInput += "9"
            if event.key == pygame.K_BACKSPACE:
                paramInput = paramInput[0: -1]
            if event.key == pygame.K_RETURN:
                selected["val"] = float(paramInput)
                paramInput = ""
                selected["color"] = (150, 150, 150)
                selected = None
                springStrength = float(physParams[0]["val"])
                springLength = float(physParams[1]["val"])
                rConst = float(physParams[2]["val"])
                fConst = float(physParams[3]["val"])
                fIncrease = float(physParams[4]["val"])
                centerPull = float(physParams[5]["val"])
            if event.key == pygame.K_ESCAPE:
                paramInput = ""
                selected["color"] = (150, 150, 150)
                selected = None

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
        if node != selected and node.notMovingTick < 300:
            calcSpringInteractions(node, springLength, springStrength)  # Spring interactions
            calcCenterPull(node, [sLength / 2, sWidth / 2])  # Center pull:
            calcRepulsiveInteractions(node, nodes)  # Repulsive interactions
        if math.sqrt(node.vel[0] ** 2 + node.vel[1] ** 2) < 1000 and node.notMovingTick <= 100:
            node.notMovingTick += 1
    updatePos(nodes, fConst)                  # Move nodes based on velocity and friction
    fConst *= fIncrease
    physParams[3]["val"] = fConst
    physParams[4]["val"] = fIncrease
    screen.fill((0, 0, 0))  # Screen color (black)

    # Draw edges:
    for node in nodes:
        for neighbor in node.neighbors:
            start = [int(zoom * (node.pos[0] + viewX)), int(zoom * (node.pos[1] + viewY))]
            end = [int(zoom * (neighbor.pos[0] + viewX)), int(zoom * (neighbor.pos[1] + viewY))]
            pygame.draw.line(screen, (100, 100, 100), start, end, edgeWidth)

    # Draw vertices:
    for node in nodes:
        if type(selected) != Node or selected in node.neighbors:
            color = colorByDegree(minDeg, degRange, 0.5)
        else:
            color = colorByDegree(minDeg, degRange, 0.3)
        pygame.draw.circle(screen, color, [int(zoom * (node.pos[0] + viewX)), int(zoom * (node.pos[1] + viewY))], int(zoom * nodeSize))

    # Redraw selected node, and its edges
    if type(selected) == Node:
        for neighbor in selected.neighbors:
            start = [int(zoom * (selected.pos[0] + viewX)), int(zoom * (selected.pos[1] + viewY))]
            end = [int(zoom * (neighbor.pos[0] + viewX)), int(zoom * (neighbor.pos[1] + viewY))]
            pygame.draw.line(screen, (255, 255, 255), start, end, edgeWidth * 2)
            pygame.draw.circle(screen, (255, 255, 255), [int(zoom * (neighbor.pos[0] + viewX)), int(zoom * (neighbor.pos[1] + viewY))],
                               int(zoom * nodeSize / 2))
        pygame.draw.circle(screen, (255, 255, 255), [int(zoom * (selected.pos[0] + viewX)), int(zoom * (selected.pos[1] + viewY))],
                           int(zoom * nodeSize))

    # Draw model parameters (Text)
    pygame.draw.rect(screen, (0, 0, 0), (1000, 0, 300, 700))
    pygame.draw.line(screen, (255, 255, 255), (1000, 0), (1000, 700), 2)

    i = 0
    for i in range(0, len(physParams)):
        screen.blit(font.render(physParams[i]["name"] + ": ", False, (255, 255, 255)), (1010, 20 + i * 70))
        screen.blit(font.render(str(round(physParams[i]["val"], 5)), False, physParams[i]["color"]), (1010, 55 + i * 70))
        screen.blit(font.render("Edit", False, physParams[i]["color"]), (1200, 55 + i * 70))
        i += 1
    screen.blit(font.render("Reconfigure", False, (255, 255, 255)), (1010, 40 + len(physParams) * 70))
    screen.blit(font.render("Set", False, (255, 255, 255)), (1010, 100 + len(physParams) * 70))
    screen.blit(font.render("Unset", False, (255, 255, 255)), (1100, 100 + len(physParams) * 70))
    if type(selected) == dict:
        screen.blit(font.render("New value: " + paramInput, False, (0, 255, 0)), (1010, 180 + len(physParams) * 70))

    pygame.display.flip()
    clock.tick(60)  # (60) FPS

# Program termination
# Test
