import pygame
import math
import random
import networkx as nx
import time

from Node import *

pygame.init()

sLength = 1000
sWidth = 700
screen = pygame.display.set_mode((sLength, sWidth))
clock = pygame.time.Clock()
mouse = pygame.mouse

viewX = 0
viewY = 0
viewSpeed = 20

springStrength = 0.1 * 10 ** 0
springLength = 30
rConst = 10 ** 4
fConst = 0.90
zoom = 0.3

nodes = []


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
        viewY += viewSpeed
    if pressed[pygame.K_s]:
        viewY -= viewSpeed
    if pressed[pygame.K_a]:
        viewX += viewSpeed
    if pressed[pygame.K_d]:
        viewX -= viewSpeed
    if pressed[pygame.K_z]:
        zoom *= 1.01
    if pressed[pygame.K_c]:
        zoom *= 0.99


    for node in nodes:
        # print("---------------------------------------")
        # print("Looking at: " + str(node))
        # print("With nieghbors: " + str(node.neighbors))
        # Spring interactions
        for neighbor in node.neighbors:
            # print("Spring change by: " + str(springStrength * (neighbor.pos[0] - node.pos[0])) + ", " + str(springStrength * (neighbor.pos[1] - node.pos[1])))
            # print("Affected by: " + str(neighbor))
            x = (neighbor.pos[0] - node.pos[0])
            y = (neighbor.pos[1] - node.pos[1])
            d = math.sqrt(x ** 2 + y ** 2)
            node.vel[0] -= (x / d) * (sLength - d) * springStrength
            node.vel[1] -= (y / d) * (sLength - d) * springStrength
            # print("Node velocity is now: " + str(node.vel))
        # Repulsive interactions
        for other in nodes:
            if node != other:
                x = (other.pos[0] - node.pos[0])
                y = (other.pos[1] - node.pos[1])
                node.vel[0] -= (x / math.sqrt(x ** 2 + y ** 2)) * (rConst / (x ** 2 + y ** 2))
                node.vel[1] -= (y / math.sqrt(x ** 2 + y ** 2)) * (rConst / (x ** 2 + y ** 2))
                # print("Repulsion change by: " + str((x / math.sqrt(x ** 2 + y ** 2)) * (rConst / (x ** 2 + y ** 2))) + ", " + str((y / math.sqrt(x ** 2 + y ** 2)) * (rConst / (x ** 2 + y ** 2))))
                # print("Affected by: " + str(other))
    for node in nodes:
        # print("Node velocity is " + str(node.vel))
        fConst *= 1 - 10 ** -3
        node.vel[0] *= fConst
        node.vel[1] *= fConst
        node.pos[0] += node.vel[0]
        node.pos[1] += node.vel[1]
        # print("----------------------")
        # print("Node " + str(Node) + "at position: " + str(node.pos))

    screen.fill((0, 0, 0))

    # Draw nodes

    for node in nodes:
        for neighbor in node.neighbors:
            start = [int(zoom * (node.pos[0] + viewX)), int(zoom * (node.pos[1] + viewY))]
            end = [int(zoom * (neighbor.pos[0] + viewX)), int(zoom * (neighbor.pos[1] + viewY))]
            pygame.draw.line(screen, (100, 100, 100), start, end, 2)

    for node in nodes:
        pygame.draw.circle(screen, (0, 200, 255), [int(zoom * (node.pos[0] + viewX)), int(zoom * (node.pos[1] + viewY))], int(zoom * 20))
        # pygame.draw.circle(screen, (100, 100, 100), [int(zoom * (node.pos[0] + viewX)), int(zoom * (node.pos[1] + viewY))], int(zoom * 16))
        # pygame.draw.circle(screen, (0, 200, 255), [int(node.pos[0] + viewX), int(node.pos[1] + viewY)], 10)

    pygame.display.flip()
    clock.tick(60)
