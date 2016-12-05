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

lr_const = 0
discount_factor = 0
NUMBER_EXPLORED_THRESHOLD = 0  #Ne in the lectures
R_PLUS = 5 #R+ -> arbitrary value (modified utility)

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
    except Exception:
        num_visited_up = 0

    if num_visited_up >= NUMBER_EXPLORED_THRESHOLD:
        up_utility = Q_dict[go_up_state] 

    #Go down
    go_down_state = cur_state + (GO_DOWN,)
    num_visited_down = 0
    down_utility = R_PLUS

    try:
        num_visited_down = N_dict[go_down_state]
    except Exception:
        num_visited_down = 0

    if num_visited_down >= NUMBER_EXPLORED_THRESHOLD:
        down_utility = Q_dict[go_down_state] 

    #Do nothing
    go_nowhere_state = cur_state + (GO_NOWHERE,)
    num_visited_nowhere = 0
    nowhere_utility = R_PLUS

    try:
        num_visited_nowhere = N_dict[go_nowhere_state]
    except Exception:
        num_visited_nowhere = 0

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
            reward  = -1
        elif checkHit(cont_cur_state):
            reward = 1
        updateQ(cur_state)
    prev_reward = reward
    return action

def updateQ(disc_cur_state):
    global disc_prev_state
    global Q_dict
    global N_dict
    global prev_reward

    try:
        N_dict[disc_prev_state] += 1
    except Exception:
        N_dict[disc_prev_state] = 1

    #Go up
    go_up_state = disc_cur_state + (GO_UP,) #Equivalent to (s, a')
    up_utility = 0

    try:
        up_utility = Q_dict[go_up_state] 
    except Exception:
        up_utility = 0

    #Go down
    go_down_state = disc_cur_state + (GO_DOWN,)
    down_utility = 0

    try:
        down_utility = Q_dict[go_down_state] 
    except Exception:
        down_utility = 0

    #Do nothing
    go_nowhere_state = disc_cur_state + (GO_NOWHERE,)
    nowhere_utility = 0

    try:
        nowhere_utility = Q_dict[go_nowhere_state] 
    except Exception:
        nowhere_utility = 0

    max_utility = max(up_utility, down_utility, nowhere_utility)

    discount_factor = 0.5
    lr_const = 12
    learning_rate = float(lr_const)/(lr_const + N_dict[disc_prev_state])

    second_term = 1
    try:
        second_term = prev_reward + (discount_factor * max_utility) - Q_dict[disc_prev_state]
        Q_dict[disc_prev_state] += learning_rate * second_term
    except Exception:
        second_term = prev_reward + discount_factor * max_utility
        Q_dict[disc_prev_state] = learning_rate * second_term

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
    disc_cur_state = cont_cur_state.getState()
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
    iterations = 100000
    avgPaddleHits = 0

    # training
    lr = 18
    discount = 0.7 
    threshold = 10
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

    # testing
    avgPaddleHits = 0
    paddleHitList = []
    testRuns = 2000
    game = 0
    for test in range(0,testRuns):
        playGame(lr, discount, threshold)
    for paddleHits in paddleHitList:
        avgPaddleHits += paddleHits
    print 'Test avg paddle hits: ' + str(float(avgPaddleHits)/testRuns) 

if __name__=='__main__':
    main()