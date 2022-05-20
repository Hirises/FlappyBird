import random
from enum import Enum
import pygame
import sys

screenWeidth = 600
screenHeight = 400

pygame.init()
pygame.display.set_caption("Flappy Brid")

class GameState(Enum):
    Ready = 0
    Run = 1
    GameOver = -1

screen = pygame.display.set_mode((screenWeidth, screenHeight))
clock = pygame.time.Clock()
fps = 30
deltaTime = 1 / fps
objects = []
state = GameState.Ready
gravity = 30
jumpForce = 10
gameSpeed = 150
initalHoleHight = 200
holeHeight = 200
minHoleHeight = 115
holeHeightDecrease = 15
distanceBtwPipe = 200
offset = 50
currentPipe = None
score = 0
difficulty = 0
gain = 1
gainIncrease = 0.05
highScore = 0
difficultyIncrease = 5

class GameObject:
    def __init__(self, x = 0, y = 0, dx = 30, dy = 30, color = (0, 0, 0)):
        self.posX = x
        self.posY = y
        self.sizeX = dx
        self.sizeY = dy
        self.color = color

    def keyInput(self, event):
        pass

    def update(self):
        pass

    def draw(self):
        pygame.draw.rect(screen, self.color, [self.posX, self.posY, self.sizeX, self.sizeY])

    def isCollideWith(self, object):
        left = self.posX < object.posX + object.sizeX
        right = self.posX + self.sizeX > object.posX
        up = self.posY < object.posY + object.sizeY
        down = self.posY + self.sizeY > object.posY

        return left and right and up and down

class Player(GameObject):
    def __init__(self):
        super().__init__(x = 100, y = screenHeight / 2, color = (255, 0, 0))

        self.posY -= self.sizeY / 2     #중앙 정렬
        self.speedY = 0

    def keyInput(self, event):
        global state
        if not state == GameState.Run:
            return

        if event[pygame.K_SPACE]:
            self.speedY = -1 * jumpForce * gain

    def update(self):
        global state
        global score

        if not state == GameState.Run:
            return

        self.speedY += gravity * deltaTime * gain
        self.posY += self.speedY

        if self.isCollideWith(currentPipe[0]) or self.isCollideWith(currentPipe[1]):
            gameOver()

        if self.posY <= 0 or self.posY + self.sizeY >= screenHeight:
            gameOver()
        
        if self.posX >= currentPipe[0].posX + currentPipe[0].sizeX:
            score += 1
            currentPipe[0].next()
        
def createNewPipe():
    height = random.randrange(0 + offset, screenHeight - holeHeight - offset)

    instance1 = Pipe(height + holeHeight, True)
    objects.append(instance1)

    instance2 = Pipe(height - screenHeight)
    objects.append(instance2)

    return (instance1, instance2)

class Pipe(GameObject):
    def __init__(self, y, half = False):
        super().__init__(screenWeidth + 100, y, 50, screenHeight, (0, 255, 0))
        self.enable = True
        self.half = half
        self.nextPipe = None

    def next(self):
        global currentPipe
        currentPipe = self.nextPipe

    def update(self):
        global state
        if not state == GameState.Run:
            return

        self.posX -= gameSpeed * deltaTime * gain
        
        if self.half and self.enable and screenWeidth - self.posX >= distanceBtwPipe:
            self.nextPipe = createNewPipe()
            self.enable = False

        if self.posX + self.sizeX <= 0:
            objects.remove(self)

class GameManager(GameObject):
    def keyInput(self, event):
        global state
        if event[pygame.K_SPACE] and state == GameState.Ready:
            state = GameState.Run
            startGame()

    def update(self):
        global state
        global score
        global difficulty
        global gain
        global holeHeight

        if state == GameState.GameOver:
            self.timer += deltaTime

            if self.timer >= 1:
                state = GameState.Ready
                resetGame()
        
        if score // difficultyIncrease > difficulty:
            difficulty += 1
            gain += gainIncrease

            if holeHeight > minHoleHeight:
                holeHeight -= holeHeightDecrease

    def draw(self):
        global state
        global score
        global state

        if state == GameState.Ready:
            displayText("Tap Space To Start", screenWeidth / 2, screenHeight / 2, 30)
            displayText("high score : " + str(highScore), screenWeidth / 2, screenHeight / 2 + 30, 20)
        if state == GameState.Run:
            displayText(str(score), screenWeidth / 2, 50)
        if state == GameState.GameOver:
            displayText("Score : " + str(score), screenWeidth / 2, screenHeight / 2, 30)

def displayText(str, x, y, size = 40):
    font = pygame.font.SysFont("arial", size)
    text = font.render(str, True, (0, 0, 0))
    rect = text.get_rect()
    rect.center = (x, y)
    screen.blit(text, rect)

def resetGame():
    global objects
    global score
    global currentPipe
    global difficulty
    global gain
    global holeHeight

    objects.clear()  
    currentPipe = None
    score = 0
    difficulty = 0
    gain = 1
    holeHeight = initalHoleHight

def startGame():
    global currentPipe
    global score
    global objects
    global difficulty
    global gain
    global holeHeight


    objects.clear()  
    objects.append(Player())
    currentPipe = createNewPipe()
    score = 0
    difficulty = 0
    gain = 1
    holeHeight = initalHoleHight

def gameOver():
    global state
    global highScore

    state = GameState.GameOver
    manager.timer = 0

    if score > highScore:
        highScore = score

manager = GameManager()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    screen.fill((150, 170, 255))

    keyEvent = pygame.key.get_pressed()
    manager.keyInput(keyEvent)
    for object in objects:
        object.update()
        object.keyInput(keyEvent)
    manager.update()

    for object in objects:
        object.draw()
    manager.draw()

    pygame.display.update()
    clock.tick(fps)
