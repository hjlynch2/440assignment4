'''
	NOTES
	------
	- Use pygame.image.save() to save the image of the gamestate, http://www.pygame.org/docs/ref/image.html
	- source of pong code -> https://trevorappleton.blogspot.com/2014/04/writing-pong-using-python-and-pygame.html
	- assignment 4 link -> http://slazebni.cs.illinois.edu/fall16/assignment4.html
'''

import pygame, sys, random
import math
from random import randint
from pygame.locals import *

# Number of frames per second
# Change this value to speed up or slow down your game
FPS = 20

#Action Constants
GO_NOWHERE = 0
GO_UP = 1
GO_DOWN = 2
ACTIONS = (GO_NOWHERE, GO_UP, GO_DOWN)

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

#moves the ball returns new position
def moveBall(ball, ballDirX, ballDirY):
    ball.x += ballDirX
    ball.y += ballDirY
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

#Checks is the ball has hit a paddle, and 'bounces' ball off it.     
def checkPaddleHit(ball, paddle, ballDirX):
    if ballDirX > 0 and ball.right > (WINDOWWIDTH - LINETHICKNESS) and paddle.top < ball.top and paddle.bottom > ball.bottom:
        return True 
    else: 
        return False

def gameOver(ball):
    if ball.x > WINDOWWIDTH:
        return True

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
    paddle_y = float(paddle_y_coord)/400
    return int(math.floor((paddle_y * 12)/(0.8)))

def getXCoord(ball):
    return int(math.floor(ball.x/33.333333))

def getYCoord(ball):
    return int(math.floor(ball.y/33.333333))

def getStateCoords(ball):
    gridX = math.floor(ball.x/33.333333)
    gridY = math.floor(ball.y/33.333333)
    return gridX + 12 * gridY

def getState(ball, ballDirX, ballDirY, paddle):
    ball_x = getXCoord(ball)
    ball_y = getYCoord(ball)
    velocity_x = getBallXState(ballDirX)
    velocity_y = getBallYState(ballDirY)
    paddle_y = getPaddleLocation(paddle.y)
    return (ball_x, ball_y, velocity_x, velocity_y, paddle_y)


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


#Main function
def main():
    pygame.init()
    global DISPLAYSURF

    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH,WINDOWHEIGHT)) 
    pygame.display.set_caption('Pong')

    #Initiate variable and set starting positions
    #any future changes made within rectangles
    ballX = WINDOWWIDTH/2 - LINETHICKNESS/2
    ballY = WINDOWHEIGHT/2 - LINETHICKNESS/2
    leftWallPosition = 0
    paddlePosition = (WINDOWHEIGHT - PADDLESIZE) /2

    # Keeps track of ball direction
    # 1/FPS scalar to account for the FPS
    ballDirX = 0.03 * WINDOWWIDTH * (2.0/FPS)
    ballDirY = 0.01 * WINDOWHEIGHT * (2.0/FPS)

    #Creates Rectangles for ball and paddles.
    leftWall = pygame.Rect(PADDLEOFFSET, leftWallPosition, LINETHICKNESS, WINDOWHEIGHT)
    paddle = pygame.Rect(WINDOWWIDTH - PADDLEOFFSET - LINETHICKNESS, paddlePosition, LINETHICKNESS, PADDLESIZE)
    ball = pygame.Rect(ballX, ballY, LINETHICKNESS, LINETHICKNESS)

    #Draws the starting position of the Arena
    drawArena()
    drawPaddle(paddle)
    drawBall(ball)

    while True: #main game loop
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        drawArena()
        pygame.draw.rect(DISPLAYSURF, BLACK, leftWall)
        drawPaddle(paddle)
        drawBall(ball)

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
                break
            ballDirX, ballDirY = checkEdgeCollision(ball, ballDirX, ballDirY)
        ball = moveBall(ball, ballDirX, ballDirY)



        state = getState(ball, ballDirX, ballDirY, paddle)
        next_action = exploration_function(state)
        

        # randomly move the paddle for now
        paddleMovement = random.random()
        movePaddle(paddle, paddleMovement)





        pygame.display.update()
        FPSCLOCK.tick(FPS)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        drawArena()
        pygame.display.update()

if __name__=='__main__':
    main()