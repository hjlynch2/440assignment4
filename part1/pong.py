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

lr_const = 0
discount_factor = 0
NUMBER_EXPLORED_THRESHOLD = 0  #Ne in the lectures
R_PLUS = 5 #R+ -> arbitrary value (modified utility)

Q_dict = dict() #stores the Q values
N_dict = dict() #stores the number of times visting state-action


# Set up the colours
BLACK     = (0  ,0  ,0  )
RED       = (255,0  ,0  )
WHITE     = (255,255,255)

# Number of frames per second
# Change this value to speed up or slow down your game
FPS = 15
WINDOWWIDTH = 400
WINDOWHEIGHT = 400
LINETHICKNESS = 10
PADDLESIZE = WINDOWHEIGHT * .2
PADDLEOFFSET = 0

# initialization of the game variables
FPSCLOCK = pygame.time.Clock()
DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH,WINDOWHEIGHT)) 
pygame.display.set_caption('Pong')

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
    ballDirX = 0.03 * WINDOWWIDTH
    ballDirY = 0.01 * WINDOWHEIGHT

    graph_cur_state = state(ballX, ballY, ballDirX, ballDirY, paddlePosition)

    #Creates Rectangles for ball and paddles.
    leftWall = pygame.Rect(PADDLEOFFSET, leftWallPosition, LINETHICKNESS, WINDOWHEIGHT)
    paddle = pygame.Rect(WINDOWWIDTH - PADDLEOFFSET - LINETHICKNESS, graph_cur_state.paddle_y, LINETHICKNESS, PADDLESIZE)
    ball = pygame.Rect(graph_cur_state.ball_x,graph_cur_state.ball_y, LINETHICKNESS, LINETHICKNESS)

    #lines = getXYLines()

    #Draws the starting position of the Arena
    drawArena()
    drawPaddle(paddle)
    drawBall(ball)
    #drawLines(lines)
    
    i = 0

    while True: #main game loop
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        pygame.image.save(DISPLAYSURF, 'frame' + str(i) + '.jpg')

        graph_cur_state.ball_x = graph_cur_state.ball_x + graph_cur_state.v_x
        graph_cur_state.ball_y = graph_cur_state.ball_y + graph_cur_state.v_y
        ball.x = graph_cur_state.ball_x
        ball.y = graph_cur_state.ball_y

        next_action = get_next_action(graph_cur_state)
        graph_cur_state = movePaddle(graph_cur_state, next_action)
        paddle.y = graph_cur_state.paddle_y

        drawArena()
        pygame.draw.rect(DISPLAYSURF, BLACK, leftWall)
        drawPaddle(paddle)
        drawBall(ball)
        #drawLines(lines)

        # if the paddle is hit, set the new ball velocities based on randomness
        paddleHit = checkPaddleHit(graph_cur_state)
        if paddleHit:
            graph_cur_state.ball_x = 2 * WINDOWWIDTH - graph_cur_state.ball_x

            V = ((random.random() * 0.06 * WINDOWHEIGHT) - 0.03 * WINDOWHEIGHT)
            while abs(graph_cur_state.v_y + V) > LINETHICKNESS: 
                V = ((random.random() * 0.06 * WINDOWHEIGHT) - 0.03 * WINDOWHEIGHT)
            graph_cur_state.v_y += V

            U = ((random.random() * 0.03 * WINDOWWIDTH) - 0.015 * WINDOWWIDTH)
            while abs(graph_cur_state.v_x + U) < 0.03 or abs(graph_cur_state.v_x + U) > LINETHICKNESS:
                U = ((random.random() * 0.03 * WINDOWWIDTH) - 0.015 * WINDOWWIDTH)
            graph_cur_state.v_x = (graph_cur_state.v_x + U) * -1
        else:
            if (gameOver(graph_cur_state)):
                pygame.quit()
                sys.exit()
            graph_cur_state = checkEdgeCollision(graph_cur_state)

        i += 1
        pygame.display.update()
        FPSCLOCK.tick(FPS)

##### Helper functions for state detection #####
def get_VX(graph_cur_state):
    if graph_cur_state.v_x < 0:
        return -1
    else:
        return 1

def get_VY(graph_cur_state):
    if abs(graph_cur_state.v_y) < 0.015 * WINDOWHEIGHT:
        return 0
    elif graph_cur_state.v_y < 0:
        return -1
    else:
        return 1

def get_PY(graph_cur_state):
    return int(math.floor((graph_cur_state.paddle_y * 15)/(WINDOWHEIGHT - PADDLESIZE)))

def get_X(graph_cur_state):
    if graph_cur_state.ball_x >= WINDOWWIDTH:
        return 14
    if graph_cur_state.ball_x < 0:
        return 0
    return int((graph_cur_state.ball_x * 15.0)/WINDOWWIDTH)

def get_Y(graph_cur_state):
    if graph_cur_state.ball_y >= WINDOWHEIGHT:
        return 14
    if graph_cur_state.ball_y < 0:
        return 0
    return int((graph_cur_state.ball_y * 15.0)/WINDOWHEIGHT)

def getXYLines():
    sizeOfState = WINDOWWIDTH / 15.0
    curr_line = 0
    lines = []
    for i in range(0,14):
        curr_line = curr_line + sizeOfState
        lines.append(curr_line)
    return lines

def movePaddle(graph_cur_state, next_action):
    if next_action == GO_DOWN: # move down
        if (graph_cur_state.paddle_y + PADDLESIZE + 0.04 * WINDOWHEIGHT) < WINDOWHEIGHT:
            graph_cur_state.paddle_y += 0.04 * WINDOWHEIGHT
    elif next_action == GO_UP: # move up
        if (graph_cur_state.paddle_y - 0.04 * WINDOWHEIGHT) > 0:
            graph_cur_state.paddle_y -= 0.04 * WINDOWHEIGHT
    return graph_cur_state

def gameOver(graph_cur_state):
    return graph_cur_state.ball_x > WINDOWWIDTH

#Checks is the ball has hit a paddle, and 'bounces' ball off it.     
def checkPaddleHit(graph_cur_state):
    if graph_cur_state.v_x > 0 and graph_cur_state.ball_x > (WINDOWWIDTH - LINETHICKNESS) and graph_cur_state.ball_y > graph_cur_state.paddle_y and graph_cur_state.ball_y < graph_cur_state.paddle_y + PADDLESIZE:
        return True 
    else: 
        return False

#Checks for a collision with a wall, and 'bounces' ball off it.
#Returns new direction
def checkEdgeCollision(graph_cur_state):
    if graph_cur_state.ball_y < LINETHICKNESS or graph_cur_state.ball_y > (WINDOWHEIGHT - LINETHICKNESS):
        if graph_cur_state.ball_y < LINETHICKNESS:
            graph_cur_state.ball_y = LINETHICKNESS
        else: 
            graph_cur_state.ball_y = (WINDOWHEIGHT - 2 * LINETHICKNESS)
        graph_cur_state.v_y = graph_cur_state.v_y * -1
    if graph_cur_state.ball_x < LINETHICKNESS:
        graph_cur_state.ball_x = LINETHICKNESS
        graph_cur_state.v_x = graph_cur_state.v_x * -1
    return graph_cur_state

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

def get_next_action(graph_cur_state):
    disc_x = get_X(graph_cur_state)
    disc_y = get_Y(graph_cur_state)
    disc_vx = get_VX(graph_cur_state)
    disc_vy = get_VY(graph_cur_state)
    disc_py = get_PY(graph_cur_state)
    disc_state = (disc_x, disc_y, disc_vx, disc_vy, disc_py)

    #Go up
    go_up_state = disc_state + (GO_UP,) #Equivalent to (s, a')
    up_utility = Q_dict[go_up_state] 

    #Go down
    go_down_state = disc_state + (GO_DOWN,)
    down_utility = Q_dict[go_down_state] 

    #Do nothing
    go_nowhere_state = disc_state + (GO_NOWHERE,)
    nowhere_utility = Q_dict[go_nowhere_state]

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

# non graphical check
def checkHit(cur_state):
    paddle_bot = cur_state.paddle_y + 0.2
    if cur_state.v_x > 0 and cur_state.ball_x >= 1 and cur_state.ball_y >= cur_state.paddle_y and cur_state.ball_y <= paddle_bot:
        return True 
    else: 
        return False

def getReward(cur_state):
    if checkHit(cur_state):
        return 1
    elif checkGameOver(cur_state):
        return -1
    return 0

def checkGameOver(cur_state):
    return cur_state.ball_x > 1 and not checkHit(cur_state)

def initializeDicts():
    global Q_dict
    global N_dict
    for bx in range(0,15):
        for by in range(0,15):
            for vx in [-1, 1]:
                for vy in [-1, 0, 1]:
                    for py in range(0,15):
                        for action  in range(0,3):
                            cur = (bx, by, vx, vy, py, action)
                            Q_dict[cur] = 0
                            N_dict[cur] = 0


"""
Return what action to take next
Arguments: cur_state - tuple representing the current state
"""
def exploration_function(cur_state):
    
    num_visited_up = 0
    num_visited_down = 0
    num_visited_nowhere = 0
    up_utility = R_PLUS
    down_utility = R_PLUS
    nowhere_utility = R_PLUS

    #Go up
    go_up_state = cur_state + (GO_UP,) #Equivalent to (s, a')
    num_visited_up = N_dict[go_up_state]
    if num_visited_up >= NUMBER_EXPLORED_THRESHOLD:
        up_utility = Q_dict[go_up_state] 

    #Go down
    go_down_state = cur_state + (GO_DOWN,)
    num_visited_down = N_dict[go_down_state]
    if num_visited_down >= NUMBER_EXPLORED_THRESHOLD:
        down_utility = Q_dict[go_down_state] 

    #Do nothing
    go_nowhere_state = cur_state + (GO_NOWHERE,)
    num_visited_nowhere = N_dict[go_nowhere_state]
    if num_visited_nowhere >= NUMBER_EXPLORED_THRESHOLD:
        nowhere_utility = Q_dict[go_nowhere_state]

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
    global N_dict
    cur_state = cont_cur_state.getState()
    action = exploration_function(cur_state)
    reward = 0
    if not disc_prev_state is None:
        if checkGameOver(cont_cur_state):
            reward  = -2
        elif checkHit(cont_cur_state):
            reward = 1
        N_dict[disc_prev_state] += 1
        updateQ(cur_state)
    prev_reward = reward
    return action

def updateQ(disc_cur_state):
    global disc_prev_state
    global Q_dict
    global N_dict
    global prev_reward

    #Go up
    go_up_state = disc_cur_state + (GO_UP,)
    up_utility = Q_dict[go_up_state] 

    #Go down
    go_down_state = disc_cur_state + (GO_DOWN,)
    down_utility = Q_dict[go_down_state] 

    #Do nothing
    go_nowhere_state = disc_cur_state + (GO_NOWHERE,)
    nowhere_utility = Q_dict[go_nowhere_state]

    max_utility = max(up_utility, down_utility, nowhere_utility)
    learning_rate = float(lr_const)/(lr_const + N_dict[disc_prev_state])
    second_term = prev_reward + (discount_factor * max_utility) - Q_dict[disc_prev_state]
    Q_dict[disc_prev_state] += learning_rate * second_term

def playGame(learning_rate_const, discount, threshold):

    global disc_cur_state
    global disc_prev_state 
    global prev_reward
    global game
    global lr_const
    global discount_factor
    global NUMBER_EXPLORED_THRESHOLD

    lr_const = learning_rate_const
    discount_factor = discount
    NUMBER_EXPLORED_THRESHOLD = threshold

    #Initiate variable and set starting positions
    #any future changes made within rectangles
    paddle_height = 0.2 

    cont_cur_state = state(0.5, 0.5, 0.03, 0.01, 0.5 - paddle_height/2)
    disc_cur_state = cont_cur_state.getState() + (GO_NOWHERE,)
    disc_prev_state = None

    paddleHitList.append(0)

    next_action = 0

    while True: #main game loop

        paddle_move = 0
        if next_action == 1:
            paddle_move = -0.04
        elif next_action == 2:
            paddle_move = 0.04

        cont_cur_state.ball_x = cont_cur_state.ball_x + cont_cur_state.v_x
        cont_cur_state.ball_y = cont_cur_state.ball_y + cont_cur_state.v_y

        if(cont_cur_state.paddle_y + paddle_move < 0.8 and cont_cur_state.paddle_y + paddle_move > 0):
            cont_cur_state.paddle_y = cont_cur_state.paddle_y + paddle_move

        # this stuff might be wrong
        next_action = QLearningAgent(cont_cur_state)
        disc_prev_state = deepcopy(disc_cur_state)
        disc_cur_state = cont_cur_state.getState() + (next_action, )   

        # if the paddle is hit, set the new ball velocities based on randomness
        paddleHit = checkHit(cont_cur_state)

        if paddleHit:
            paddleHitList[game] += 1
            cont_cur_state.ball_x = 2 - cont_cur_state.ball_x
            V = (random.random() * 0.06) - 0.03
            while abs(cont_cur_state.v_y + V) > 1: 
                V = (random.random() * 0.03) - 0.015
            U = (random.random() * 0.03) - 0.015
            while abs(cont_cur_state.v_x + U) < 0.03 or abs(cont_cur_state.v_x * -1 + U) > 1:
                U = (random.random() * 0.03 ) - 0.015
            cont_cur_state.v_y = cont_cur_state.v_y + V
            cont_cur_state.v_x = (cont_cur_state.v_x + U) * -1
        else:
            if checkGameOver(cont_cur_state):
                # look at this
                updateQ(cont_cur_state.getState())
                game += 1
                break
            cont_cur_state = checkWallCollision(cont_cur_state)

#Main function
def main():
    global paddleHitList
    global game
    iterations = 50000
    avgPaddleHits = 0
    initializeDicts()

    # training
    lr = 20
    discount = 0.4
    threshold = 20
    print 'learning rate const: ' + str(lr)
    print 'discount factor: ' + str(discount)
    print 'threshold: ' + str(threshold)
    paddleHitList = []
    start = time.time()
    for game in range(0, iterations):
        if game % 1000 == 0:
            print game
        playGame(lr, discount, threshold)
    for paddleHits in paddleHitList:
        avgPaddleHits += paddleHits
    end = time.time()
    print 'avg paddle hits: ' + str(float(avgPaddleHits)/iterations)
    print 'time taken: ' + str(end - start)
    print

    '''
    # testing
    avgPaddleHits = 0
    paddleHitList = []
    testRuns = 2000
    game = 0
    for test in range(0,testRuns):
        playGame(lr, discount, threshold)
    for paddleHits in paddleHitList:
        avgPaddleHits += paddleHits
    print 'Test avg paddle hits: ' + str(float(avgPaddleHits)/testRuns)'''
    pygame.init()
    playGraphicGame()

if __name__=='__main__':
    main()