import random
from enum import Enum
import pygame
import sys

#화면 설정
screenWeidth = 600
screenHeight = 400
pygame.init()
pygame.display.set_caption("Flappy Brid")
screen = pygame.display.set_mode((screenWeidth, screenHeight))
clock = pygame.time.Clock()
fps = 30
deltaTime = 1 / fps

#게임 설정
class GameState(Enum):
    Ready = 0
    Run = 1
    GameOver = -1
currenGameState = GameState.Ready
objects = []
gravity = 30
jumpForce = 10
gameSpeed = 150
initalHoleHight = 200
distanceBtwPipe = 200
holeHeightOffset = 50

#난이도 설정
holeHeightDecrease = 15
minHoleHeight = 115
gainIncrease = 0.05
difficultyIncrease = 5

#변수
frontalPipe = None
score = 0
difficulty = 0
amplification = 1
holeHeight = 200
highScore = 0

#상속용 게임 오브젝트 객체
class GameObject:
    def __init__(self, x = 0, y = 0, dx = 30, dy = 30, color = (0, 0, 0)):
        self.posX = x
        self.posY = y
        self.sizeX = dx
        self.sizeY = dy
        self.color = color

    #키 입력 처리
    def keyInput(self, event):
        pass

    #매 프래임 호출되는 메인 로직용 함수
    def update(self):
        pass

    #update() 이후 호출되는 스크린 표기용 함수
    def draw(self):
        pygame.draw.rect(screen, self.color, [self.posX, self.posY, self.sizeX, self.sizeY])

    #aabb 충돌감지
    def isCollideWith(self, object):
        left = self.posX < object.posX + object.sizeX
        right = self.posX + self.sizeX > object.posX
        up = self.posY < object.posY + object.sizeY
        down = self.posY + self.sizeY > object.posY

        return left and right and up and down

#플레이어 객체
class Player(GameObject):
    def __init__(self):
        super().__init__(x = 100, y = screenHeight / 2, color = (255, 0, 0))

        self.posY -= self.sizeY / 2     #중앙 정렬
        self.speedY = 0

    def keyInput(self, event):
        global currenGameState

        if not currenGameState == GameState.Run:
            return

        if event[pygame.K_SPACE]:
            self.speedY = -1 * jumpForce * amplification

    def update(self):
        global currenGameState
        global score

        if not currenGameState == GameState.Run:
            return

        #중력 적용
        self.speedY += gravity * deltaTime * amplification
        self.posY += self.speedY

        #게임 종료 감지
        if self.isCollideWith(frontalPipe[0]) or self.isCollideWith(frontalPipe[1]):
            gameOver()
        if self.posY <= 0 or self.posY + self.sizeY >= screenHeight:
            gameOver()
        
        #점수 가산
        if self.posX >= frontalPipe[0].posX + frontalPipe[0].sizeX:
            score += 1
            frontalPipe[0].next()

#파이프 객체
class Pipe(GameObject):
    def __init__(self, y, half = False):
        super().__init__(screenWeidth + 100, y, 50, screenHeight, (0, 255, 0))
        self.enable = True
        self.half = half    #위 아래 구분하는 용도
        self.nextPipe = None

    #최전방 파이프 순환
    def next(self):
        global frontalPipe

        frontalPipe = self.nextPipe

    def update(self):
        global currenGameState
        if not currenGameState == GameState.Run:
            return

        #이동
        self.posX -= gameSpeed * deltaTime * amplification
        
        #다음 파이프 생성 (위쪽 파이프에서만 처리됨 - 중복 생성 방지)
        if self.half and self.enable and screenWeidth - self.posX >= distanceBtwPipe:
            self.nextPipe = createNewPipe()
            self.enable = False

        #화면 넘어가면 삭제
        if self.posX + self.sizeX <= 0:
            objects.remove(self)

#게임 매니저 오브젝트
class GameManager(GameObject):
    def keyInput(self, event):
        if event[pygame.K_SPACE] and currenGameState == GameState.Ready:
            startGame()

    def update(self):
        global currenGameState
        global score
        global difficulty
        global amplification
        global holeHeight

        #게임 오버 후 1초 뒤에 Ready 상태로 전환
        if currenGameState == GameState.GameOver:
            self.timer += deltaTime

            if self.timer >= 1:
                currenGameState = GameState.Ready
                resetGame()
        
        #난이도 증가
        if score // difficultyIncrease > difficulty:
            difficulty += 1
            amplification += gainIncrease

            if holeHeight > minHoleHeight:
                holeHeight -= holeHeightDecrease

    #GUI 표기
    def draw(self):
        global currenGameState
        global score
        global currenGameState

        if currenGameState == GameState.Ready:
            displayText("Tap Space To Start", screenWeidth / 2, screenHeight / 2, 30)
            displayText("high score : " + str(highScore), screenWeidth / 2, screenHeight / 2 + 30, 20)
        elif currenGameState == GameState.Run:
            displayText(str(score), screenWeidth / 2, 50)
        elif currenGameState == GameState.GameOver:
            displayText("Score : " + str(score), screenWeidth / 2, screenHeight / 2, 30)

#다음 파이프 생성
def createNewPipe():
    height = random.randrange(0 + holeHeightOffset, screenHeight - holeHeight - holeHeightOffset)

    instance1 = Pipe(height + holeHeight, True)
    objects.append(instance1)

    instance2 = Pipe(height - screenHeight)
    objects.append(instance2)

    return (instance1, instance2)

#화면에 텍스트 표기
def displayText(str, x, y, size = 40):
    font = pygame.font.SysFont("arial", size)
    text = font.render(str, True, (0, 0, 0))
    rect = text.get_rect()
    rect.center = (x, y)
    screen.blit(text, rect)

#게임 초기화
def resetGame():
    global objects
    global score
    global frontalPipe
    global difficulty
    global amplification
    global holeHeight

    objects.clear()  
    frontalPipe = None
    score = 0
    difficulty = 0
    amplification = 1
    holeHeight = initalHoleHight

#변수 초기화 후 게임 시작
def startGame():
    global frontalPipe
    global score
    global objects
    global difficulty
    global amplification
    global holeHeight
    global currenGameState


    objects.clear()  
    objects.append(Player())
    frontalPipe = createNewPipe()
    score = 0
    difficulty = 0
    amplification = 1
    holeHeight = initalHoleHight
    currenGameState = GameState.Run

#게임 종료
def gameOver():
    global currenGameState
    global highScore

    currenGameState = GameState.GameOver
    manager.timer = 0

    if score > highScore:
        highScore = score

#게임 메니저 할당
manager = GameManager()

#메인 루프
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    #메인 로직 & 키 입력 처리
    keyEvent = pygame.key.get_pressed()
    manager.keyInput(keyEvent)
    for object in objects:
        object.update()
        object.keyInput(keyEvent)
    manager.update()

    #화면 표기
    screen.fill((150, 170, 255))
    for object in objects:
        object.draw()
    manager.draw()

    #화면 업데이트
    pygame.display.update()
    clock.tick(fps)
