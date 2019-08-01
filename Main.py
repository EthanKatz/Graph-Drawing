import pygame
import math
import random
import networkx as nx
import colorsys
import time

from Node import *
from graphSetup import *


# Original graph setup function:

def degreeInfo(nList):

    xD = 0           # Maximum degree
    nD = 1000000000  # Minimum degree

    for n in nList:
        if len(n.neighbors) > xD:
            xD = len(n.neighbors)
        if len(n.neighbors) < nD:
            nD = len(n.neighbors)

    dR = xD - nD  # Degree range

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

    if dR == 0:
        return (0, 230, 255)
    else:
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


def getNumberInput(eK):  # Get keyboard input necessary for changing parameters in program. (Function parameter is event key)
    if eK == pygame.K_PERIOD:
        return "."
    elif eK == pygame.K_0:
        return "0"
    elif eK == pygame.K_1:
        return "1"
    elif eK == pygame.K_2:
        return "2"
    elif eK == pygame.K_3:
        return "3"
    elif eK == pygame.K_4:
        return "4"
    elif eK == pygame.K_5:
        return "5"
    elif eK == pygame.K_6:
        return "6"
    elif eK == pygame.K_7:
        return "7"
    elif eK == pygame.K_8:
        return "8"
    elif eK == pygame.K_9:
        return "9"
    else:
        return ""


# Initialize graph
graphSetup = GraphSetup()
nodes = graphSetup.getGraph()

# Pygame setup
pygame.init()
sLength = 1000
sWidth = 700
screen = pygame.display.set_mode((sLength + 450, sWidth))
clock = pygame.time.Clock()
mouse = pygame.mouse
pygame.font.init()
font = pygame.font.SysFont("freesansbold.ttf", 36)
smallFont = pygame.font.SysFont("freesansbold.ttf", 24)
pygame.display.set_caption("Graph Visualizer")

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
centerPull = 0.0001                # Pull of each node towards the center

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

# Visual preference parameters
nodeSize = 300
edgeWidth = 2

minDeg, degRange = degreeInfo(nodes)  # Get degree information

outOfBounds = False  # Vertices out of bounds error detector

selected = None

if len(nodes) == 0:
    done = True  # Program termination variable
else:
    done = False

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
                if sLength + 350 < mouseX < sLength + 350 + font.size("Edit")[0] and \
                        55 + i * 70 < mouseY < 55 + i * 70 + font.size(str(round(physParams[i]["val"], 5)))[1]:
                    selected = physParams[i]
                    physParams[i]["color"] = (0, 255, 0)
            if sLength + 160 < mouseX < sLength + 160 + font.size("Reconfigure")[0] and \
                    40 + len(physParams) * 70 < mouseY < 40 + len(physParams) * 70 + font.size("Reconfigure")[1]:
                fConst = 0.95
                fIncrease = 0.999
                for node in nodes:
                    node.notMovingTick = 0
                    node.vel = [0, 0]
                    node.pos = [random.randint(-1000, 1000), random.randint(-1000, 1000)]
                outOfBounds = False
            elif sLength + 160 < mouseX < sLength + 160 + font.size("Set")[0] and \
                    100 + len(physParams) * 70 < mouseY < 100 + len(physParams) * 70 + font.size("Set")[1]:
                fConst = 0.0
                fIncrease = 0.0
                for node in nodes:
                    node.notMovingTick = 300
                    node.vel = [0, 0]
            elif 1250 < mouseX < 1250 + font.size("Unset")[0] and \
                    100 + len(physParams) * 70 < mouseY < 100 + len(physParams) * 70 + font.size("Unset")[1]:
                fConst = 0.80
                fIncrease = 1
                for node in nodes:
                    node.notMovingTick = 0
        # Keyboard input used for changing parameters
        if type(selected) == dict and event.type == pygame.KEYDOWN:
            if len(paramInput) < 10:
                paramInput += getNumberInput(event.key)
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
        if zoom < 0.5:
            viewX *= 1 - zoomSpeed
            viewY *= 1 - zoomSpeed
            zoom *= 1 + zoomSpeed
    if pressed[pygame.K_c]:
        if zoom > 0.005:
            viewX *= 1 + zoomSpeed
            viewY *= 1 + zoomSpeed
            zoom *= 1 - zoomSpeed

    screen.fill((0, 0, 0))  # Screen color (black)

    # Check for vertices out of bounds (Bounds at 10 ** 5 in both positive and negative directions
    for node in nodes:
        if abs(node.pos[0] + node.vel[0]) > 10 ** 8 or abs(node.pos[1] + node.vel[1]) > 10 ** 8:
            outOfBounds = True

    # Write warning message if nodes exceed positional limits:
    if outOfBounds:
        screen.blit(font.render(str("Vertices out of bounds: Adjust parameters and reconfigure"), False, (255, 0, 0)), (25, 25))
    else:
        for node in nodes:
            if node.notMovingTick < 300:
                calcSpringInteractions(node, springLength, springStrength)  # Spring interactions
                calcCenterPull(node, [sLength / 2, sWidth / 2])  # Center pull:
                calcRepulsiveInteractions(node, nodes)  # Repulsive interactions
            if math.sqrt(node.vel[0] ** 2 + node.vel[1] ** 2) < 1000 and node.notMovingTick <= 100:
                node.notMovingTick += 1
        updatePos(nodes, fConst)  # Move nodes based on velocity and friction
        fConst *= fIncrease
        physParams[3]["val"] = fConst
        physParams[4]["val"] = fIncrease

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
    # Draw background for off-screen visiuals:
    pygame.draw.rect(screen, (0, 0, 0), (1150, 0, 450, 700))
    pygame.draw.line(screen, (255, 255, 255), (1150, 0), (1150, 700), 2)

    # Draw model parameters (Text)
    for i in range(0, len(physParams)):
        screen.blit(font.render(physParams[i]["name"] + ": ", False, (255, 255, 255)), (sLength + 160, 20 + i * 70))
        screen.blit(font.render(str(round(physParams[i]["val"], 5)), False, physParams[i]["color"]), (sLength + 160, 55 + i * 70))
        screen.blit(font.render("Edit", False, physParams[i]["color"]), (sLength + 350, 55 + i * 70))
    screen.blit(font.render("Reconfigure", False, (255, 255, 255)), (sLength + 160, 40 + len(physParams) * 70))
    screen.blit(font.render("Set", False, (255, 255, 255)), (sLength + 160, 100 + len(physParams) * 70))
    screen.blit(font.render("Unset", False, (255, 255, 255)), (sLength + 250, 100 + len(physParams) * 70))
    if type(selected) == dict:
        screen.blit(font.render("New value: " + paramInput, False, (0, 255, 0)), (sLength + 160, 180 + len(physParams) * 70))

    # Draw color key
    if degRange > 0:
        screen.blit(font.render("Degree:", False, (255, 255, 255)), (1030, 20))
        for i in range(0, degRange + 1):
            rectColor = list(colorsys.hls_to_rgb(0.50 * (1 - (i / degRange)), 0.5, 1))
            rectColor[0] *= 255
            rectColor[1] *= 255
            rectColor[2] *= 255

            pygame.draw.rect(screen, rectColor, (1050, 50 + 600 * i / (degRange + 1), 50, math.ceil(600 / (degRange + 1))))
            pygame.draw.line(screen, (0, 0, 0), (1050, 50 + 600 * i / (degRange + 1)), (1100, 50 + 600 * i / (degRange + 1)), 3)
            screen.blit(smallFont.render(str(i + minDeg), False, (255, 255, 255)),
                        (1110, 50 + 600 * (i + 0.5) / (degRange + 1) - smallFont.size(str(i))[1] / 2))

    pygame.display.flip()
    clock.tick(60)  # (60) FPS

# Program termination
