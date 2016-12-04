'''
	NOTES
	------
	- Use pygame.image.save() to save the image of the gamestate, http://www.pygame.org/docs/ref/image.html
	- source of pong code -> https://trevorappleton.blogspot.com/2014/04/writing-pong-using-python-and-pygame.html
	- assignment 4 link -> http://slazebni.cs.illinois.edu/fall16/assignment4.html
'''

import pygame, sys, random
import math
import time
from random import randint
from pygame.locals import *
from state import state
from copy import deepcopy

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
game = 0

#Global Variables to be used through our program

WINDOWWIDTH = 400
WINDOWHEIGHT = 400
LINETHICKNESS = 10
PADDLESIZE = WINDOWHEIGHT * .2
PADDLEOFFSET = 0

Q_dict = dict() #stores the Q values
N_dict = dict() #stores the number of times visting state-action

# Set up the colours
BLACK     = (0  ,0  ,0  )
RED       = (255,0  ,0  )
WHITE     = (255,255,255)

# initialization of the game variables
FPSCLOCK = pygame.time.Clock()
DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH,WINDOWHEIGHT)) 
pygame.display.set_caption('Pong')

#Draws the arena the game will be played in. 
def drawArena():
    DISPLAYSURF.fill(WHITE)

#Draws the paddle
def drawPaddle(paddle):
    #Stops paddle moving too low
    if paddle.y + PADDLESIZE >= WINDOWHEIGHT:
        paddle.y = WINDOWHEIGHT - PADDLESIZE
    #Stops paddle moving too high
    elif paddle.y < 0:
        paddle.y = 0
    #Draws paddle
    pygame.draw.rect(DISPLAYSURF, BLACK, paddle)


#draws the ball
def drawBall(ball):
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

#Checks for a collision with a wall, and 'bounces' ball off it.
#Returns new direction
def checkEdgeCollision(ball, ballDirX, ballDirY):
    if ball.top < LINETHICKNESS or ball.bottom > (WINDOWHEIGHT - LINETHICKNESS):
        if ball.top < LINETHICKNESS:
            ball.y = 0
        else: 
            ball.y = (WINDOWHEIGHT - 2 * LINETHICKNESS)
        ballDirY = ballDirY * -1
    if ball.left < (LINETHICKNESS):
        ball.x = LINETHICKNESS
        ballDirX = ballDirX * -1
    return ballDirX, ballDirY

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

#Checks is the ball has hit a paddle, and 'bounces' ball off it.     
def checkPaddleHit(ball, paddle, ballDirX):
    if ballDirX > 0 and ball.right > (WINDOWWIDTH - LINETHICKNESS) and paddle.top < ball.top and paddle.bottom > ball.bottom:
        return True 
    else: 
        return False

# non graphical check
def checkHit(cur_state):
    paddle_bot = cur_state.paddle_y + 0.2
    if cur_state.v_x > 0 and cur_state.ball_x >= 1 and cur_state.ball_y >= cur_state.paddle_y and cur_state.ball_y <= paddle_bot:
        #print 'PADDLE HIT'
        return True 
    else: 
        return False

def getReward(cur_state):
    if checkHit(cur_state):
        return 1
    elif checkGameOver(cur_state):
        return -1
    return 0

def gameOver(ball):
    if ball.x > WINDOWWIDTH:
        return True

def checkGameOver(cur_state):
    return cur_state.ball_x > 1

def movePaddle(paddle, paddleMovement):
    if (paddleMovement < (1.0/3)): # move down
        if (paddle.bottom + 0.04 * WINDOWHEIGHT * (2.0/FPS)) < WINDOWHEIGHT:
            paddle.y += 0.04 * WINDOWHEIGHT * (2.0/FPS)
    elif(paddleMovement < (2.0/3)): # move up
        if (paddle.top - 0.04 * WINDOWHEIGHT * (2.0/FPS)) > 0:
            paddle.y -= 0.04 * WINDOWHEIGHT * (2.0/FPS)


##### Helper functions for state detection #####
def getBallXState(ballDirX):
    if ballDirX < 0:
        return -1
    else:
        return 1

def getBallYState(ballDirY):
    if abs(ballDirY) < 0.015:
        return 0
    elif ballDirY < 0:
        return -1
    else:
        return 1

def getPaddleLocation(paddle_y_coord):
    paddle_y = float(paddle_y_coord)/WINDOWHEIGHT
    return int(math.floor((paddle_y * 12)/(0.8)))

def getXCoord(ball):
    return int(math.floor(ball.x/33.333333))

def getYCoord(ball):
    return int(math.floor(ball.y/33.333333))

def getStateCoords(ball):
    gridX = math.floor(ball.x/33.333333)
    gridY = math.floor(ball.y/33.333333)
    return gridX + 12 * gridY

def getXYLines():
    sizeOfState = WINDOWWIDTH / 12.0
    curr_line = 0
    lines = []
    for i in range(0,11):
        curr_line = curr_line + sizeOfState
        lines.append(curr_line)
    return lines


##### Exploration Function #####
NUMBER_EXPLORED_THRESHOLD = 5  #Ne in the lectures
R_PLUS = 10 #R+ -> arbitrary value (modified utility)

"""
Return what action to take next
Arguments: cur_state - tuple representing the current state
"""
def exploration_function(cur_state):
    #Go up
    go_up_state = cur_state + (GO_UP,) #Equivalent to (s, a')
    num_visited_up = 0
    up_utility = R_PLUS

    try:
        num_visited_up = N_dict[go_up_state]
    except Exception as e:
        num_visited_up = 0

    if num_visited_up >= NUMBER_EXPLORED_THRESHOLD:
        try:
            up_utility = Q_dict[go_up_state] 
        except Exception as e:
            up_utility = R_PLUS

    #Go down
    go_down_state = cur_state + (GO_DOWN,)
    num_visited_down = 0
    down_utility = R_PLUS

    try:
        num_visited_down = N_dict[go_down_state]
    except Exception as e:
        num_visited_down = 0

    if num_visited_down >= NUMBER_EXPLORED_THRESHOLD:
        try:
            down_utility = Q_dict[go_down_state] 
        except Exception as e:
            down_utility = R_PLUS

    #Do nothing
    go_nowhere_state = cur_state + (GO_NOWHERE,)
    num_visited_nowhere = 0
    nowhere_utility = R_PLUS

    try:
        num_visited_nowhere = N_dict[go_nowhere_state]
    except Exception as e:
        num_visited_nowhere = 0

    if num_visited_nowhere >= NUMBER_EXPLORED_THRESHOLD:
        try:
            nowhere_utility = Q_dict[go_nowhere_state] 
        except Exception as e:
            nowhere_utility = R_PLUS

    # Choose random direction when all the utilities are the same
    if up_utility == down_utility and down_utility == nowhere_utility:
        rand_index = randint(0,2)
        return ACTIONS[rand_index]
    best_utility = max(up_utility, down_utility, nowhere_utility)
    if best_utility == up_utility:
        return GO_UP
    elif best_utility == down_utility:
        return GO_DOWN
    elif best_utility == nowhere_utility:
        return GO_NOWHERE

# pass cur_state w/out action attached to it
def updateQVal(prev_state, reward):
    if not prev_state is None:
        try:
            N_dict[prev_state] += 1
        except Exception:
            N_dict[prev_state] = 1

        #Go up
        go_up_state = prev_state + (GO_UP,) #Equivalent to (s, a')
        up_utility = 0

        try:
            up_utility = Q_dict[go_up_state] 
        except Exception:
            up_utility = 0

        #Go down
        go_down_state = prev_state + (GO_DOWN,)
        down_utility = 0

        try:
            down_utility = Q_dict[go_down_state] 
        except Exception:
            down_utility = 0

        #Do nothing
        go_nowhere_state = prev_state + (GO_NOWHERE,)
        nowhere_utility = 0

        try:
            nowhere_utility = Q_dict[go_nowhere_state] 
        except Exception:
            nowhere_utility = 0

        max_utility = max(up_utility, down_utility, nowhere_utility)

        discount_factor = 0.5
        lr_const = 0.5
        learning_rate = lr_const/(lr_const + N_dict[prev_state])

        first_term = learning_rate * N_dict[prev_state]
        second_term = 0
        try:
            second_term = reward + discount_factor * max_utility - Q_dict[prev_state]
        except Exception:
            Q_dict[prev_state] = 0
            second_term = reward + discount_factor * max_utility - Q_dict[prev_state]
        Q_dict[prev_state] += first_term * second_term

# change this later
def isTerminal(cur_state):
    return False

def playGraphicGame():
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
    ballDirX = 0.03 * WINDOWWIDTH * (2.0/FPS)
    ballDirY = 0.01 * WINDOWHEIGHT * (2.0/FPS)

    #Creates Rectangles for ball and paddles.
    leftWall = pygame.Rect(PADDLEOFFSET, leftWallPosition, LINETHICKNESS, WINDOWHEIGHT)
    paddle = pygame.Rect(WINDOWWIDTH - PADDLEOFFSET - LINETHICKNESS, paddlePosition, LINETHICKNESS, PADDLESIZE)
    ball = pygame.Rect(ballX, ballY, LINETHICKNESS, LINETHICKNESS)

    lines = getXYLines()

    #Draws the starting position of the Arena
    drawArena()
    drawPaddle(paddle)
    drawBall(ball)
    drawLines(lines)

    while True: #main game loop
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        drawArena()
        pygame.draw.rect(DISPLAYSURF, BLACK, leftWall)
        drawPaddle(paddle)
        drawBall(ball)
        drawLines(lines)

        # if the paddle is hit, set the new ball velocities based on randomness
        paddleHit = checkPaddleHit(ball, paddle, ballDirX)
        if paddleHit:
            V = ((random.random() * 0.06 * WINDOWHEIGHT) - 0.03 * WINDOWHEIGHT) * (2.0/FPS)
            ballDirY = ballDirY + V
            U = ((random.random() * 0.03 * WINDOWWIDTH) - 0.15 * WINDOWWIDTH) * (2.0/FPS)
            while abs(ballDirX * -1 + U) < 0.03:
                U = ((random.random() * 0.03 * WINDOWWIDTH) - 0.15 * WINDOWWIDTH) * (2.0/FPS)
            ballDirX = ballDirX * -1 + U
        else:
            if (gameOver(ball)):
                playGame()
            ballDirX, ballDirY = checkEdgeCollision(ball, ballDirX, ballDirY)
        ballX = ballX + ballDirX
        ballY = ballY + ballDirY
        ball = moveBall(ball, ballX, ballY)

        state = getState(ball, ballDirX, ballDirY, paddle)
        next_action = exploration_function(state)
        
        # randomly move the paddle for now
        paddleMovement = random.random()
        movePaddle(paddle, paddleMovement)

        pygame.display.update()
        FPSCLOCK.tick(FPS)

def playGame():
    #Initiate variable and set starting positions
    #any future changes made within rectangles
    paddle_height = 0.2 
    global disc_cur_state
    global disc_prev_state
    global prev_reward
    global game

    cont_cur_state = state(0.5, 0.5, 0.03, 0.01, 0.5 - paddle_height/2)
    disc_cur_state = cont_cur_state.getState()
    disc_prev_state = None

    paddleHitList.append(0)

    while True: #main game loop

        disc_prev_state = deepcopy(disc_cur_state) + (0, )
        next_action = exploration_function(cont_cur_state.getState())
        disc_cur_state = cont_cur_state.getState() + (next_action, )
        paddle_move = 0
        if next_action == 1:
            paddle_move = 0.04
        elif next_action == 2:
            paddle_move = -0.04

        cont_cur_state.ball_x = cont_cur_state.ball_x + cont_cur_state.v_x
        cont_cur_state.ball_y = cont_cur_state.ball_y + cont_cur_state.v_y

        if(cont_cur_state.paddle_y + paddle_move < 0.8 and cont_cur_state.paddle_y + paddle_move > 0):
            cont_cur_state.paddle_y = cont_cur_state.paddle_y + paddle_move   

        # if the paddle is hit, set the new ball velocities based on randomness
        paddleHit = checkHit(cont_cur_state)
        #print Q_dict

        if paddleHit:
            paddleHitList[game] += 1
            cont_cur_state.ball_x = 2 - cont_cur_state.ball_x
            V = (random.random() * 0.03) - 0.015
            while abs(cont_cur_state.ball_y + V) > 1: 
                V = (random.random() * 0.03) - 0.015
            cont_cur_state.v_y = cont_cur_state.v_y + V
            U = (random.random() * 0.06) - 0.03
            while abs(cont_cur_state.ball_x * -1 + U) < 0.03 and abs(cont_cur_state.ball_x * -1 + U) > 1:
                U = (random.random() * 0.03 ) - 0.03
            cont_cur_state.v_x = cont_cur_state.v_x * -1 + U
            updateQVal(disc_prev_state, 1)
        else:
            if getReward(cont_cur_state) == -1:
                updateQVal(disc_prev_state, -1)
                game += 1
                break
            else:
                updateQVal(disc_prev_state, 0)
            cont_cur_state = checkWallCollision(cont_cur_state)

        #prev_reward = getReward(cont_cur_state)
        #print prev_reward
        
        #updateQVal(disc_prev_state, prev_reward)

#Main function
def main():
    #pygame.init()
    #playGraphicGame()
    for game in range(0,1000):
        playGame()
    bestPaddleHits = 0
    for paddleHits in paddleHitList:
        #print paddleHits
        bestPaddleHits = max(bestPaddleHits, paddleHits)
    print N_dict
    print 'best paddle hits: ' + str(bestPaddleHits)

if __name__=='__main__':
    main()