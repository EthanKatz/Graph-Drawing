import pygame
import math
import random
import networkx as nx
import colorsys
import time

from Node import *

pygame.init()

sLength = 1000
sWidth = 700
screen = pygame.display.set_mode((sLength, sWidth))
clock = pygame.time.Clock()
mouse = pygame.mouse

viewX = -1 * sLength / 2
viewY = -1 * sWidth / 2
viewSpeed = 20

springStrength = 0.01 * 10 ** 0
springLength = 100
rConst = 3 * 10 ** 4
fConst = 0.99
fIncrease = 1 - 1 * 10 ** -5
centerPull = 0.0

zoom = 0.03


nodes = []

ba = nx.barabasi_albert_graph(100, 1)
ws = nx.watts_strogatz_graph(30, 4, 0.0)

adjMatrix = nx.to_numpy_matrix(ws)
for i in range(0, adjMatrix.shape[0]):
    nodes.append(Node([random.randint(-1000, 1000), random.randint(-1000, 1000)]))

overlap = True
while(overlap):
    overlap = False
    for i in nodes:
        for j in nodes:
            if i != j and i.pos == j.pos:
                overlap = True
                i.pos = [random.randint(-1000, 1000), random.randint(-1000, 1000)]

maxDeg = 0
minDeg = 1000000000

for i in range(0, adjMatrix.shape[0]):
    for j in range(0, adjMatrix.shape[1]):
        if adjMatrix.item(i, j) != 0:
            nodes[i].addNieghbor(nodes[j])
            nodes[j].addNieghbor(nodes[i])
    if len(nodes[i].neighbors) > maxDeg:
        maxDeg = len(nodes[i].neighbors)
    if len(nodes[i].neighbors) < minDeg:
        minDeg = len(nodes[i].neighbors)
degRange = maxDeg - minDeg
if degRange == 0:
    degRange = 1

print([minDeg, maxDeg, degRange])

"""
for i in range(0, 25):
    nodes.append(Node([random.randint(50, sLength - 50), random.randint(50, sWidth - 50)]))

for a in nodes:
    for b in nodes:
        if a != b and random.randint(0, 10) == 0:
            a.addNieghbor(b)
            b.addNieghbor(a)
"""
done = False

while not done:
    for event in pygame.event.get():
        # End game
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_DELETE:
            done = True

    pressed = pygame.key.get_pressed()

    # Check for user input
    if pressed[pygame.K_w]:
        viewY += viewSpeed * (1 / zoom)
    if pressed[pygame.K_s]:
        viewY -= viewSpeed * (1 / zoom)
    if pressed[pygame.K_a]:
        viewX += viewSpeed * (1 / zoom)
    if pressed[pygame.K_d]:
        viewX -= viewSpeed * (1 / zoom)
    if pressed[pygame.K_z]:
        zoom *= 1.01
    if pressed[pygame.K_c]:
        zoom *= 0.99


    for node in nodes:
        # Spring interactions
        for neighbor in node.neighbors:
            x = (neighbor.pos[0] - node.pos[0])
            y = (neighbor.pos[1] - node.pos[1])
            d = math.sqrt(x ** 2 + y ** 2)
            node.vel[0] -= (x / d) * (sLength - d) * springStrength
            node.vel[1] -= (y / d) * (sLength - d) * springStrength
        # Center pull (Towards 0, 0:
        node.vel[0] -= node.pos[0] * centerPull
        node.vel[1] -= node.pos[1] * centerPull
        # Repulsive interactions
        for other in nodes:
            if node != other:
                x = (other.pos[0] - node.pos[0])
                y = (other.pos[1] - node.pos[1])
                node.vel[0] -= (x / math.sqrt(x ** 2 + y ** 2)) * (rConst / (x ** 2 + y ** 2) ** 0.54)
                node.vel[1] -= (y / math.sqrt(x ** 2 + y ** 2)) * (rConst / (x ** 2 + y ** 2) ** 0.54)
    for node in nodes:
        # print("Node velocity is " + str(node.vel))
        fConst *= fIncrease
        node.vel[0] *= fConst
        node.vel[1] *= fConst
        node.pos[0] += node.vel[0]
        node.pos[1] += node.vel[1]

    screen.fill((0, 0, 0))

    # Draw nodes

    for node in nodes:
        for neighbor in node.neighbors:
            start = [int(zoom * (node.pos[0] + viewX)), int(zoom * (node.pos[1] + viewY))]
            end = [int(zoom * (neighbor.pos[0] + viewX)), int(zoom * (neighbor.pos[1] + viewY))]
            pygame.draw.line(screen, (100, 100, 100), start, end, 2)

    for node in nodes:
        color = colorsys.hls_to_rgb(0.55 * (1 - ((len(node.neighbors) - minDeg) / degRange)), 0.5, 1)
        color = list(color)
        color[0] *= 255
        color[1] *= 255
        color[2] *= 255
        color = tuple(color)
        pygame.draw.circle(screen, color, [int(zoom * (node.pos[0] + viewX)), int(zoom * (node.pos[1] + viewY))], int(zoom * 100))
        # pygame.draw.circle(screen, (100, 100, 100), [int(zoom * (node.pos[0] + viewX)), int(zoom * (node.pos[1] + viewY))], int(zoom * 16))
        # pygame.draw.circle(screen, (0, 200, 255), [int(node.pos[0] + viewX), int(node.pos[1] + viewY)], 10)

    pygame.display.flip()
    clock.tick(40)
