import sys
import time
import math
import random
import pygame
from pygame.locals import *


wys = 800  # px
szer = 1600  # px

BIALY = 255, 255, 255
CIEMNY_ZIELONY = 0, 50, 0
CZARNY = 0, 0, 0
FIOLETOWY = 160, 50, 160
CZERWONY = 255, 0, 0
ZIELONY = 0, 255, 0
ZOLTY = 0, 255, 255
NIEBIESKI = 100, 150, 255

WS = WIELKOSC_SEGMENTU = 5
PJ = PROMIEN_JABLKA = 10
DS = DLUGOSC_POCZATKOWA = 10
PP = PREDKOSC_POCZATKOWA = 150
ZK = ZASIEG_KOLIZJI = WS + 2

class GameObject:
    def Draw(self, okno):
        pass

    def Update(self, deltaTime):
        pass

class Player(GameObject):

    def __init__(self, pos, color):
        self.size =  DS    #ilosc segmentow
        self.speed = PP   #predkosc poczatkowa
        self.angle = 0     #kierunek poczatkowy
        self.rotationStep = 3.0 #promien skretu
        self.parts = []    #lista segmentow
        self.pos = pos     #pozycja startowa
        self.isDead = False #czy gracz odpadl

        self.speedUpTimer = 0.0
        self.sickTimer = 0.0

        for i in range(2, self.size + 2):
            self.parts.append([pos[0],pos[1]])

        self.color=color


        #self.bite_sound = pygame.mixer.Sound("appleBite.mp3")

    def Update(self, deltaTime):
        #print("Updatuje gracza")
        if self.isDead == False:
            sv =  self.StepVector(deltaTime)
            self.parts[0] = [self.parts[0][0] + sv[0], self.parts[0][1] + sv[1]]

            for i in range(1, len(self.parts)):
                vector_distance = [self.parts[i-1][0] - self.parts[i][0], self.parts[i-1][1] - self.parts[i][1]]
                length = math.sqrt(vector_distance[0] * vector_distance[0] + vector_distance[1] * vector_distance[1])
                if (length > 1.5 * WS):
                    a = (length - 1.5 * WS) / length
                    self.parts[i][0] += vector_distance[0] * a
                    self.parts[i][1] += vector_distance[1] * a

            if self.speedUpTimer > 0.0:
                self.speed = 1.5 * PP
                self.speedUpTimer -= deltaTime
            else:
                self.speed = 1.0 * PP
                self.speedUpTimer = 0.0

            if self.sickTimer > 0.0:
                self.sickTimer -= deltaTime
            else:
                self.sickTimer = 0.0

    def Draw(self, okno):
        size = WS

        for i in range(1, len(self.parts)):
            if(i >= len(self.parts) - 3):
                size-=1
            pygame.draw.circle(okno, CZARNY, (int(self.parts[i][0]), int(self.parts[i][1])), size+2, size+1)

        size = WS
        for i in range(1, len(self.parts)):
            if(i >= len(self.parts) - 3):
                size-=1
            pygame.draw.circle(okno, self.color, (int(self.parts[i][0]), int(self.parts[i][1])), size, size)

        pygame.draw.circle(okno, CZARNY, (int(self.parts[0][0]), int(self.parts[0][1])), WS+3, WS+2)
        if(self.sickTimer == 0):
            pygame.draw.circle(okno, self.color, (int(self.parts[0][0]), int(self.parts[0][1])), WS+1, WS)

    def StepVector(self, dT):
        ds = dT*self.speed
        return [ds*math.cos(self.angle),ds*math.sin(self.angle)]

    def Turn(self, dT):
        #signed if turn left
        if(self.sickTimer > 0):
            dT *= -1
        self.angle += dT * self.rotationStep

    def eatApple(self, sick):
        #self.bite_sound.play()
        if(sick == False):
            self.speedUpTimer = 3.0
            for i in range(0,5):
                self.parts.append([self.parts[-1][0], self.parts[-1][1]])
        else:
            self.sickTimer = 5.0

class Apple(GameObject):

    def __init__(self, pos, is_sick):
        self.active = True
        self.sick = is_sick
        self.pos = pos
        if(is_sick):
            self.img = pygame.image.load("appleSick.png")
        else:
            self.img = pygame.image.load("apple.png")
        self.angle = 0
        self.rotated_img = pygame.transform.rotate(self.img, self.angle)
        self.SpeedX = 500

    def Update(self, deltaTime):
        if(self.active):
            self.pos[0] = self.pos[0] + self.SpeedX * deltaTime
            self.angle = (-3 * self.pos[0])
            self.rotated_img = pygame.transform.rotate(self.img, self.angle)
            self.SpeedX *= 0.99

    def Draw(self, okno):
        if(self.active):
            pygame.draw.circle(okno, CZARNY, (int(self.pos[0]), int(self.pos[1])), PJ-1, PJ-2)
            okno.blit(self.rotated_img, (self.pos[0] - PJ - 2, self.pos[1] - PJ - 2))

def isColliding(x1, y1, r1, x2, y2, r2):
    dx = x2 - x1
    dy = y2 - y1
    dist = math.sqrt(math.pow(dx, 2) + math.pow(dy, 2))
    if(dist <= r1 + r1):
        return True
    else:
        return False

class Game:

    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        pygame.display.set_caption('Snejx')
        self.gameRunning = True
        self.players = []
        self.apples = []
        self.okno = pygame.display.set_mode((szer, wys), 0, 24)
        self.backgroundTile = pygame.image.load("grassTile.png")

    def addPlayer(self, pos, kolor):
        p = Player(pos, kolor)
        self.players.insert(len(self.players), p)
        #self.players.append(p)

    def addApple(self, pos, sick, speedX):
        a = Apple(pos, sick)
        a.SpeedX = speedX
        self.apples.insert(len(self.players), a)

    def generateApples(self):
        los = random.randint(0, 600)
        maxPred = szer * 5
        if(los == 1 or los == 0):
            #dobre z lewej
            self.addApple([-10, random.randint(0, wys)], False, random.randint(10, maxPred))
            pass
        elif(los == 2 or los == 3):
            #dobre z prawej
            self.addApple([szer + 10, random.randint(0, wys)], False, random.randint(-maxPred, -10))
            pass
        elif(los == 5):
            #zatrute z lewej
            self.addApple([-10, random.randint(0, wys)], True, random.randint(10, maxPred))
            pass
        elif(los == 4):
            #zatrutesa assz prawej
            self.addApple([szer + 10, random.randint(0, wys)], True, random.randint(-maxPred, -10))
            pass


        #TODO generowanie jablek
        pass

    def printPlayers(self):
        print(self.players)

    def checkHeadsCollisions(self):
        for i in range(0, len(self.players)):
            if(self.players[i].isDead == False):
                head = self.players[i].parts[0]
                if head[0] < ZK or head[1] < ZK or head[0] > szer - ZK or head[1] > wys - ZK:
                    return i
                for j in range(0, len(self.players)):
                    if i != j:
                        for p in range(1, len(self.players[j].parts)):
                            part = self.players[j].parts[p]
                            if isColliding(part[0], part[1], ZK, head[0], head[1], ZK):
                                return i
                            pass
                for a in range(0, len(self.apples)):
                    apple = self.apples[a]
                    if(apple.active):
                        if(isColliding(head[0], head[1], ZK, apple.pos[0], apple.pos[1], PJ)):
                            self.players[i].eatApple(apple.sick)
                            apple.active = False
                            print("Kolizja z jablkiem")
        return -1

    def checkForWinners(self, okno):
        winners = 0
        winner_number = -1
        for p in range(0, len(self.players)):
            if not self.players[p].isDead:
                winners += 1
                winner_number = p
                pass
        if winners == 1:
            self.gameRunning = False
            print("Zwyciezyl gracz " + str(winner_number))
            sysfont = pygame.font.SysFont("arial", 70)
            sysfontback = pygame.font.SysFont("arial", 72)
            end_game_message = sysfont.render("Wygral gracz " + str(winner_number + 1), 1, self.players[winner_number].color)
            end_game_message_back = sysfont.render("Wygral gracz " + str(winner_number + 1), 1, CZARNY)
            okno.blit(end_game_message_back, (szer/4, wys/3))
            okno.blit(end_game_message, (szer/4 + 3, wys/3 +3))
            pygame.display.update()
            time.sleep(3)


    def runTheGame(self):
        #while(True):
        print("Odpalam gre")
        game_logo = pygame.image.load("logo.png")
        self.okno.fill(CZARNY)
        self.okno.blit(game_logo, (szer/2 - 320, wys/2 - 200))
        pygame.display.update()

        started = False
        while(started == False):
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    started = True

                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

        newTime = time.time()
        self.apples = []
        #self.players = []
        while self.gameRunning:
            ############OBLICZANIE KROKU CZASOWEGO
            oldTime = newTime
            newTime = time.time()
            deltaTime = newTime - oldTime

            ############POBRANIE WEJSCIA
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == KEYDOWN:
                    if event.key == K_F2:
                        self.players[0].eatApple(False)
                        pass

            keys_pressed = pygame.key.get_pressed()

            if(keys_pressed[K_ESCAPE]):
                pygame.quit()
                sys.exit()

            if keys_pressed[K_LEFT]:
                self.players[0].Turn(deltaTime*-1)
            elif keys_pressed[K_RIGHT]:
                self.players[0].Turn(deltaTime)

            if(len(self.players) >= 2):
                if keys_pressed[K_a]:
                    self.players[1].Turn(deltaTime*-1)
                elif keys_pressed[K_s]:
                    self.players[1].Turn(deltaTime)

                if(len(self.players) >= 3):
                    if keys_pressed[K_n]:
                        self.players[2].Turn(deltaTime*-1)
                    elif keys_pressed[K_m]:
                        self.players[2].Turn(deltaTime)


            ############ AKTUALIZACJA STANOW
            for player in self.players:
                player.Update(deltaTime)

            for apple in self.apples:
                apple.Update(deltaTime)

            loser = self.checkHeadsCollisions()
            if loser > -1:
                self.players[loser].isDead = True
                print("Przegral gracz " + str(loser))

            self.generateApples()

            ############ RYSOWANIE
            self.okno.fill(CZARNY)

            #Rysowanie tla z kwadratow
            for i in range(0, szer, 98):
                for j in range(0, wys, 98):
                    self.okno.blit(self.backgroundTile, [i, j])

            for player in self.players:
                player.Draw(self.okno)

            for apple in self.apples:
                apple.Draw(self.okno)

            self.checkForWinners(self.okno)
            pygame.display.update()

G = Game()
G.addPlayer([100, 100], CZERWONY)
G.addPlayer([100, wys - 100], NIEBIESKI)
#G.addPlayer([100, wys - 300], FIOLETOWY)

#G.addApple([0, 400], False, random.randint(0,1000))


G.runTheGame()

pygame.quit()
sys.exit()
raw_input("Nacisnij cos")
