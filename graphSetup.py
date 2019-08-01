import pygame
import networkx as nx
import random

from Node import Node

pygame.init()

clock = pygame.time.Clock()
mouse = pygame.mouse
pygame.font.init()
font = pygame.font.SysFont("freesansbold.ttf", 36)
pygame.display.set_caption("Setup")

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

class GraphSetup():
    def modelSelect(self):

        sLength = 700
        sWidth = 400

        screen = pygame.display.set_mode((sLength, sWidth))

        done = False  # Setup termination variable
        selected = "default"  # Selected model

        # Select Model loop:
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouseX, mouseY = mouse.get_pos()
                    if 20 < mouseX < 20 + font.size("Watts-Strogatz")[0] and 85 < mouseY < 85 + font.size("Watts-Strogatz")[1]:
                        done = True
                        selected = "ws"
                    elif 20 < mouseX < 20 + font.size("Barabasi-Albert")[0] and 145 < mouseY < 145 + font.size("Barabasi-Albert")[1]:
                        done = True
                        selected = "ba"
                    elif 20 < mouseX < 20 + font.size("Erdős-Rényi")[0] and 205 < mouseY < 205 + font.size("Erdős-Rényi")[1]:
                        done = True
                        selected = "er"

            screen.blit(font.render("Choose a random graph generation model:", False, (255, 255, 255)), (20, 25))
            screen.blit(font.render("Watts-Strogatz", False, (255, 255, 255)), (20, 85))
            screen.blit(font.render("Barabasi-Albert", False, (255, 255, 255)), (20, 145))
            screen.blit(font.render("Erdős-Rényi", False, (255, 255, 255)), (20, 205))

            screen.blit(font.render("Created by Ethan Katz", False, (255, 255, 255)), (20, sWidth - 85))
            screen.blit(font.render("Contributions by Isaac Hoffman", False, (255, 255, 255)), (20, sWidth - 45))

            pygame.display.flip()
            clock.tick(60)  # (60) FPS
        return selected

    def createModel(self, params, modelType):

        sLength = 700
        sWidth = 400

        screen = pygame.display.set_mode((sLength, sWidth))

        selected = None

        for param in params:
            param["color"] = (150, 150, 150)

        paramInput = ""

        done = False

        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if type(selected) == dict:
                        selected["color"] = (150, 150, 150)
                        selected = None
                    mouseX, mouseY = mouse.get_pos()

                    for i in range(0, len(params)):
                        if 200 < mouseX < 200 + font.size("Edit")[0] and \
                                55 + i * 70 < mouseY < 55 + i * 70 + font.size(str(round(params[i]["val"], 5)))[1]:
                            selected = params[i]
                            params[i]["color"] = (0, 255, 0)

                    if 20 < mouseX < 20 + font.size("Draw!")[0] and sWidth - font.size("Draw!")[1] - 20 < mouseY < sWidth - 20:
                        done = True

                if event.type == pygame.KEYDOWN and type(selected) == dict:
                    paramInput += getNumberInput(event.key)
                    if event.key == pygame.K_BACKSPACE:
                        paramInput = paramInput[0: -1]
                    if event.key == pygame.K_RETURN:
                        selected["val"] = float(paramInput)
                        paramInput = ""
                        selected["color"] = (150, 150, 150)
                        selected = None
                    if event.key == pygame.K_ESCAPE:
                        paramInput = ""
                        selected["color"] = (150, 150, 150)
                        selected = None
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    done = True

            screen.fill((0, 0, 0))  # Screen color (black)

            for i in range(0, len(params)):
                screen.blit(font.render(params[i]["name"] + ": ", False, (255, 255, 255)), (20, 20 + i * 70))
                screen.blit(font.render(str(round(params[i]["val"], 5)), False, params[i]["color"]), (20, 55 + i * 70))
                screen.blit(font.render("Edit", False, params[i]["color"]), (200, 55 + i * 70))

            if type(selected) == dict:
                screen.blit(font.render("New value: " + paramInput, False, (0, 255, 0)),
                            (20, 35 + len(params) * 70))

            screen.blit(font.render("Draw!", False, (255, 255, 255)), (20, sWidth - font.size("Draw!")[1] - 20))

            pygame.display.flip()
            clock.tick(60)  # (60) FPS

        if modelType == "ws":
            return nx.to_numpy_matrix(nx.watts_strogatz_graph(int(params[0]["val"]), int(params[1]["val"]), params[2]["val"]))
        elif modelType == "ba":
            return nx.to_numpy_matrix(nx.barabasi_albert_graph(int(params[0]["val"]), int(params[1]["val"])))
        elif modelType == "er":
            return nx.to_numpy_matrix(nx.erdos_renyi_graph(int(params[0]["val"]), params[1]["val"]))
        else:
            return None

    def getGraph(self):
        self.modelType = self.modelSelect()
        self.adjMatrix = None
        self.nodes = []

        if self.modelType == "ws":
            self.adjMatrix = self.createModel([
            {"name": "Number of nodes", "val": 50},
            {"name": "Number of connections each node has", "val": 4},
            {"name": "Probability of random edge rearrangement", "val": 0.10},
        ], "ws")
        elif self.modelType == "ba":
            self.adjMatrix = self.createModel([
                {"name": "Number of nodes", "val": 50},
                {"name": "Number of connections each node has", "val": 1}
            ], "ba")
        elif self.modelType == "er":
            self.adjMatrix = self.createModel([
                {"name": "Number of nodes", "val": 50},
                {"name": "Probability of random connection", "val": 0.1}
            ], "er")

        else:
            return []

        # Create the right number of nodes, and add them to the list nodes
        for i in range(0, self.adjMatrix.shape[0]):
            self.nodes.append(Node([random.randint(-1000, 1000), random.randint(-1000, 1000)]))

        # Use the adjacency matrix to set the neighbors of each node
        for i in range(0, self.adjMatrix.shape[0]):
            for j in range(0, self.adjMatrix.shape[1]):
                if self.adjMatrix.item(i, j) != 0:
                    self.nodes[i].addNieghbor(self.nodes[j])
                    self.nodes[j].addNieghbor(self.nodes[i])

        # Find and recalculate overlap; otherwise, there will be a division by zero error in future calculations
        overlap = True
        while overlap:
            overlap = False
            for i in self.nodes:
                for j in self.nodes:
                    if i != j and i.pos == j.pos:
                        overlap = True
                        i.pos = [random.randint(-1000, 1000), random.randint(-1000, 1000)]

        return self.nodes
