'''
	NOTES
	------
	- Use pygame.image.save() to save the image of the gamestate, http://www.pygame.org/docs/ref/image.html
	- source of pong code -> https://trevorappleton.blogspot.com/2014/04/writing-pong-using-python-and-pygame.html
	- assignment 4 link -> http://slazebni.cs.illinois.edu/fall16/assignment4.html
'''

import pygame, sys, random
from random import randint
from pygame.locals import *
from state import state
from copy import deepcopy
import numpy as np
import time

# Number of frames per second
# Change this value to speed up or slow down your game
FPS = 20

#Action Constants
GO_NOWHERE = 0
GO_UP = 1
GO_DOWN = 2
ACTIONS = (GO_NOWHERE, GO_UP, GO_DOWN)
disc_cur_state = (0,0,0,0,0,0)
disc_prev_state = None
prev_reward = 0
gameLengths = []
paddleHitList = []
iters = []
game = 0

lr_const = 0
discount_factor = 0
NUMBER_EXPLORED_THRESHOLD = 0
R_PLUS = 5

#Global Variables to be used through our program

WINDOWWIDTH = 400
WINDOWHEIGHT = 400
LINETHICKNESS = 10
PADDLESIZE = WINDOWHEIGHT * .2
PADDLEOFFSET = 0

#Q_dict = dict() #stores the Q values
#N_dict = dict() #stores the number of times visting state-action
Q = np.ndarray((12,12,2,2,12,3))
N = np.ndarray((12,12,2,2,12,3))
Q.fill(0)
N.fill(0)

# Set up the colours
BLACK     = (0  ,0  ,0  )
RED       = (255,0  ,0  )
WHITE     = (255,255,255)

# initialization of the game variables
FPSCLOCK = pygame.time.Clock()
DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH,WINDOWHEIGHT)) 
pygame.display.set_caption('Pong')

'''
def playGraphicGame():

    global disc_cur_state
    global disc_prev_state 
    global prev_reward
    global game
    global DISPLAYSURF
    global FPSCLOCK

    #Initiate variable and set starting positions
    #any future changes made within rectangles
    ballX = WINDOWWIDTH/2 - LINETHICKNESS/2
    ballY = WINDOWHEIGHT/2 - LINETHICKNESS/2
    leftWallPosition = 0.0
    paddlePosition = (WINDOWHEIGHT - PADDLESIZE) /2

    # Keeps track of ball direction
    # 1/FPS scalar to account for the FPS
    ballDirX = 0.03 * WINDOWWIDTH
    ballDirY = 0.01 * WINDOWHEIGHT

    cont_cur_state = state(ballX, ballY, ballDirX, ballDirY, paddlePosition, True)
    disc_cur_state = cont_cur_state.getState() + (GO_NOWHERE,)
    disc_prev_state = None

    paddleHitList.append(0)

    next_action = 0

    leftWall = pygame.Rect(PADDLEOFFSET, leftWallPosition, LINETHICKNESS, WINDOWHEIGHT)
    paddle = pygame.Rect(WINDOWWIDTH - PADDLEOFFSET - LINETHICKNESS, paddlePosition, LINETHICKNESS, PADDLESIZE)
    ball = pygame.Rect(ballX, ballY, LINETHICKNESS, LINETHICKNESS)

    lines = getXYLines()

    #Draws the starting position of the Arena
    drawArena()
    cont_cur_state = drawPaddle(paddle, cont_cur_state)
    drawBall(ball, cont_cur_state)
    drawLines(lines)

    while True: #main game loop

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        paddle_move = 0
        if next_action == 1:
            paddle_move = -0.04 * WINDOWHEIGHT
        elif next_action == 2:
            paddle_move = 0.04 * WINDOWHEIGHT

        cont_cur_state.ball_x = cont_cur_state.ball_x + cont_cur_state.v_x
        cont_cur_state.ball_y = cont_cur_state.ball_y + cont_cur_state.v_y

        if(cont_cur_state.paddle_y + paddle_move < 0.8 * WINDOWHEIGHT and cont_cur_state.paddle_y + paddle_move > 0):
            cont_cur_state.paddle_y = cont_cur_state.paddle_y + paddle_move

        next_action = QLearningAgent(cont_cur_state)
        disc_prev_state = deepcopy(disc_cur_state)
        disc_cur_state = cont_cur_state.getState() + (next_action, )   

        paddleHit = cont_cur_state.v_x > 0 and cont_cur_state.ball_x >= WINDOWWIDTH - LINETHICKNESS and cont_cur_state.ball_y >= cont_cur_state.paddle_y and cont_cur_state.ball_y <= cont_cur_state.paddle_y + PADDLESIZE

        if paddleHit:
            print 'paddle hit'
            paddleHitList[game] += 1
            cont_cur_state.ball_x = WINDOWWIDTH - abs(cont_cur_state.ball_x - WINDOWWIDTH)
            V = (random.random() * 0.03 * WINDOWHEIGHT) - 0.015 * WINDOWWIDTH
            U = (random.random() * 0.06 * WINDOWWIDTH) - 0.03 * WINDOWWIDTH
            while abs(cont_cur_state.v_x + U) < 0.03 * WINDOWWIDTH:
                U = (random.random() * 0.06 * WINDOWWIDTH) - 0.03 * WINDOWWIDTH
            cont_cur_state.v_y = cont_cur_state.v_y + V
            cont_cur_state.v_x = (cont_cur_state.v_x + U) * -1
        else:
            if cont_cur_state.ball_x > WINDOWWIDTH:
                # look at this
                updateQ(cont_cur_state.getState())
                game += 1
                break
            cont_cur_state = checkEdgeCollision(cont_cur_state)

        drawArena()
        pygame.draw.rect(DISPLAYSURF, BLACK, leftWall)
        cont_cur_state = drawPaddle(paddle, cont_cur_state)
        drawBall(ball, cont_cur_state)
        drawLines(lines)

        pygame.display.update()
        FPSCLOCK.tick(FPS)

def getXYLines():
    sizeOfState = WINDOWWIDTH / 12.0
    curr_line = 0
    lines = []
    for i in range(0,11):
        curr_line = curr_line + sizeOfState
        lines.append(curr_line)
    return lines

#Checks for a collision with a wall, and 'bounces' ball off it.
#Returns new direction
def checkEdgeCollision(cur_state):
    if cur_state.ball_y < LINETHICKNESS or cur_state.ball_y > (WINDOWHEIGHT - LINETHICKNESS):
        if cur_state.ball_y < LINETHICKNESS:
            cur_state.ball_y = 0
        else: 
            cur_state.ball_y = (WINDOWHEIGHT - 2 * LINETHICKNESS)
        cur_state.v_y = cur_state.v_y * -1
    if cur_state.ball_x < LINETHICKNESS:
        cur_state.ball_x = LINETHICKNESS + (LINETHICKNESS - cur_state.ball_x)
        cur_state.v_x = cur_state.v_x * -1
    return cur_state

#Draws the arena the game will be played in. 
def drawArena():
    DISPLAYSURF.fill(WHITE)

#Draws the paddle
def drawPaddle(paddle, cont_cur_state):
    #Stops paddle moving too low
    if cont_cur_state.paddle_y + PADDLESIZE >= WINDOWHEIGHT:
        cont_cur_state.paddle_y = WINDOWHEIGHT - PADDLESIZE
    #Stops paddle moving too high
    elif cont_cur_state.paddle_y < 0:
        cont_cur_state.paddle_y = 0
    #Draws paddle
    paddle.y = cont_cur_state.paddle_y
    pygame.draw.rect(DISPLAYSURF, BLACK, paddle)
    return cont_cur_state

#draws the ball
def drawBall(ball, cont_cur_state):
    ball.y = cont_cur_state.ball_y
    ball.x = cont_cur_state.ball_x
    pygame.draw.rect(DISPLAYSURF, RED, ball)

# draws separating lines
def drawLines(lines):
    # draw horizontal lines
    for line in lines:
        pygame.draw.line(DISPLAYSURF, BLACK, (0, line), (WINDOWWIDTH, line), 1)

    # draw vertical lines
    for line in lines:
        pygame.draw.line(DISPLAYSURF, BLACK, (line, 0), (line, WINDOWHEIGHT), 1)

# moves the ball, passes in new x and y position
def moveBall(ball, ballX, ballY):
    ball.x = ballX
    ball.y = ballY
    return ball

'''

# non graphical check
def checkWallCollision(cur_state):
    if cur_state.ball_x < 0:
        cur_state.ball_x = cur_state.ball_x * -1
        cur_state.v_x = cur_state.v_x * -1
    if cur_state.ball_y < 0:
        cur_state.ball_y = cur_state.ball_y * -1
        cur_state.v_y = cur_state.v_y * -1
    if cur_state.ball_y > 1:
        cur_state.ball_y = 2 - cur_state.ball_y
        cur_state.v_y = cur_state.v_y * -1
    return cur_state

def getReward(cur_state):
    if cur_state.v_x > 0 and cur_state.ball_x >= 1 and cur_state.ball_y >= cur_state.paddle_y and cur_state.ball_y <= cur_state.paddle_y + 0.2:
        return 1
    elif checkGameOver(cur_state):
        return -1
    return 0

def checkGameOver(cur_state):
    return cur_state.ball_x > 1

def exploration_function(cur_state):
    global Q
    global N

    x = cur_state[0]
    y = cur_state[1]
    v_x = cur_state[2]
    v_y = cur_state[3]
    paddle_y = cur_state[4]

    up_utility = R_PLUS
    num_visited_up = N[x][y][v_x][v_y][paddle_y][GO_UP]
    if num_visited_up >= NUMBER_EXPLORED_THRESHOLD:
        up_utility = Q[x][y][v_x][v_y][paddle_y][GO_UP]

    down_utility = R_PLUS
    num_visited_down = N[x][y][v_x][v_y][paddle_y][GO_DOWN]
    if num_visited_down >= NUMBER_EXPLORED_THRESHOLD:
        down_utility = Q[x][y][v_x][v_y][paddle_y][GO_DOWN]

    nowhere_utility = R_PLUS
    num_visited_nowhere = N[x][y][v_x][v_y][paddle_y][GO_NOWHERE]
    if num_visited_nowhere >= NUMBER_EXPLORED_THRESHOLD:
        nowhere_utility = Q[x][y][v_x][v_y][paddle_y][GO_NOWHERE]

    best_utility = max(up_utility, down_utility, nowhere_utility)

    # Choose random direction when all the utilities are the same
    if up_utility == down_utility and down_utility == nowhere_utility:
        rand_index = randint(0,2)
        return ACTIONS[rand_index]
    if best_utility == up_utility:
        return GO_UP
    elif best_utility == down_utility:
        return GO_DOWN
    elif best_utility == nowhere_utility:
        return GO_NOWHERE

def QLearningAgent(cont_cur_state):
    global prev_reward
    cur_state = cont_cur_state.getState()
    action = exploration_function(cur_state)
    reward = 0
    if not disc_prev_state is None:
        reward = getReward(cont_cur_state)
        updateQ(cur_state)
    prev_reward = reward
    return action

def updateQ(cur_state):
    global disc_prev_state
    global Q
    global N
    global prev_reward
    global lr_const
    global discount_factor

    p_x = disc_prev_state[0]
    p_y = disc_prev_state[1]
    p_v_x = disc_prev_state[2]
    p_v_y = disc_prev_state[3]
    p_paddle_y = disc_prev_state[4]
    p_action = disc_prev_state[5]

    x = cur_state[0]
    y = cur_state[1]
    v_x = cur_state[2]
    v_y = cur_state[3]
    paddle_y = cur_state[4]

    N[p_x][p_y][p_v_x][p_v_y][p_paddle_y][p_action] += 1
    
    up_utility = Q[x][y][v_x][v_y][paddle_y][GO_UP]
    down_utility = Q[x][y][v_x][v_y][paddle_y][GO_DOWN]
    nowhere_utility = Q[x][y][v_x][v_y][paddle_y][GO_NOWHERE]

    max_utility = max(up_utility, down_utility, nowhere_utility)

    learning_rate = float(lr_const)/(lr_const + N[p_x][p_y][p_v_x][p_v_y][p_paddle_y][p_action])

    second_term = prev_reward + (discount_factor * max_utility) - Q[p_x][p_y][p_v_x][p_v_y][p_paddle_y][p_action]
    Q[p_x][p_y][p_v_x][p_v_y][p_paddle_y][p_action] += learning_rate * second_term

def playGame(lr, discount, threshold):

    global disc_cur_state
    global disc_prev_state 
    global prev_reward
    global game
    global iters
    global it
    global lr_const
    global discount_factor
    global NUMBER_EXPLORED_THRESHOLD

    lr_const = lr
    discount_factor = discount
    NUMBER_EXPLORED_THRESHOLD = threshold

    #Initiate variable and set starting positions
    #any future changes made within rectangles
    paddle_height = 0.2 

    cont_cur_state = state(0.5, 0.5, 0.03, 0.01, 0.5 - paddle_height/2, False)
    disc_cur_state = cont_cur_state.getState() + (GO_NOWHERE,)
    disc_prev_state = None

    paddleHitList.append(0)
    iters.append(0)

    next_action = 0

    while not checkGameOver(cont_cur_state): #main game loop

        iters[game] += 1

        paddle_move = 0
        if next_action == 1:
            paddle_move = -0.04
        elif next_action == 2:
            paddle_move = 0.04

        cont_cur_state.ball_x = cont_cur_state.ball_x + cont_cur_state.v_x
        cont_cur_state.ball_y = cont_cur_state.ball_y + cont_cur_state.v_y

        if(cont_cur_state.paddle_y + paddle_move < 0.8 and cont_cur_state.paddle_y + paddle_move > 0):
            cont_cur_state.paddle_y = cont_cur_state.paddle_y + paddle_move

        next_action = QLearningAgent(cont_cur_state)
        disc_prev_state = deepcopy(disc_cur_state)
        disc_cur_state = cont_cur_state.getState() + (next_action, )   

        paddleHit = cont_cur_state.v_x > 0 and cont_cur_state.ball_x >= 1 and cont_cur_state.ball_y >= cont_cur_state.paddle_y and cont_cur_state.ball_y <= cont_cur_state.paddle_y + .2

        if paddleHit:
            paddleHitList[game] += 1
            cont_cur_state.ball_x = 2 - cont_cur_state.ball_x
            V = (random.random() * 0.06) - 0.03
            while abs(cont_cur_state.v_y + V) > 1: 
                V = (random.random() * 0.03) - 0.015
            U = (random.random() * 0.03) - 0.015
            while abs(cont_cur_state.v_x + U) < 0.03 or abs(cont_cur_state.ball_x + U) > 1:
                U = (random.random() * 0.03) - 0.015
            cont_cur_state.v_y = cont_cur_state.v_y + V
            cont_cur_state.v_x = (cont_cur_state.v_x + U) * -1
        else:
            cont_cur_state = checkWallCollision(cont_cur_state)

    updateQ(cont_cur_state.getState())
    game += 1

#Main function
def main():
    global paddleHitList
    iterations = 100000
    avgPaddleHits = 0

    for threshold in range(5, 150, 10):
        for d in range(1, 10, 2):
            discount = d/10.0
            for lr in range(5, threshold, 10):
                if lr == 5 and discount == 0.1 and threshold == 15:
                    continue
                # training
                print 'learning rate const: ' + str(lr)
                print 'discount factor: ' + str(discount)
                print 'threshold: ' + str(threshold)
                paddleHitList = []
                start = time.time()
                for game in range(0, iterations):
                    playGame(lr, discount, threshold)
                for paddleHits in paddleHitList:
                    avgPaddleHits += paddleHits
                end = time.time()
                print 'avg paddle hits: ' + str(float(avgPaddleHits)/iterations)
                print 'time taken: ' + str(end - start)
                print

                # testing
                avgPaddleHits = 0
                paddleHitList = []
                testRuns = 2000
                for test in range(0,testRuns):
                    playGame(lr, discount, threshold)
                for paddleHits in paddleHitList:
                    avgPaddleHits += paddleHits
                print 'Test avg paddle hits: ' + str(float(avgPaddleHits)/testRuns) 
                print


    #pygame.init()
    #playGraphicGame()
    
if __name__=='__main__':
    main()