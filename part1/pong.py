'''
	NOTES
	------
	- Use pygame.image.save() to save the image of the gamestate, http://www.pygame.org/docs/ref/image.html
	- source of pong code -> https://trevorappleton.blogspot.com/2014/04/writing-pong-using-python-and-pygame.html
	- assignment 4 link -> http://slazebni.cs.illinois.edu/fall16/assignment4.html
'''

import pygame, sys
from pygame.locals import *

# Number of frames per second
# Change this value to speed up or slow down your game
FPS = 200

#Global Variables to be used through our program

WINDOWWIDTH = 400
WINDOWHEIGHT = 400
LINETHICKNESS = 10
PADDLESIZE = WINDOWHEIGHT * .2
PADDLEOFFSET = 0

# Set up the colours
BLACK     = (0  ,0  ,0  )
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
    pygame.draw.rect(DISPLAYSURF, BLACK, ball)

#moves the ball returns new position
def moveBall(ball, ballDirX, ballDirY):
    ball.x += ballDirX
    ball.y += ballDirY
    return ball

#Checks for a collision with a wall, and 'bounces' ball off it.
#Returns new direction
def checkEdgeCollision(ball, ballDirX, ballDirY):
    if ball.top == (LINETHICKNESS) or ball.bottom == (WINDOWHEIGHT - LINETHICKNESS):
        ballDirY = ballDirY * -1
    if ball.left == (LINETHICKNESS) or ball.right == (WINDOWWIDTH - LINETHICKNESS):
        ballDirX = ballDirX * -1
    return ballDirX, ballDirY

#Checks is the ball has hit a paddle, and 'bounces' ball off it.     
def checkHitBall(ball, paddle1, paddle2, ballDirX):
    if ballDirX == -1 and paddle1.right == ball.left and paddle1.top < ball.top and paddle1.bottom > ball.bottom:
        return -1
    elif ballDirX == 1 and paddle2.left == ball.right and paddle2.top < ball.top and paddle2.bottom > ball.bottom:
        return -1
    else: return 1

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

    #Keeps track of ball direction
    ballDirX = -1 ## -1 = left 1 = right
    ballDirY = -1 ## -1 = up 1 = down

    #Creates Rectangles for ball and paddles.
    leftWall = pygame.Rect(PADDLEOFFSET, leftWallPosition, LINETHICKNESS, WINDOWHEIGHT)
    paddle = pygame.Rect(WINDOWWIDTH - PADDLEOFFSET - LINETHICKNESS, paddlePosition, LINETHICKNESS, PADDLESIZE)
    ball = pygame.Rect(ballX, ballY, LINETHICKNESS, LINETHICKNESS)

    #Draws the starting position of the Arena
    drawArena()
    drawPaddle(paddle)
    drawBall(ball)

    pygame.mouse.set_visible(0) # make cursor invisible

    while True: #main game loop
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            # mouse movement commands
            elif event.type == MOUSEMOTION:
                mousex, mousey = event.pos
                paddle.y = mousey

        drawArena()
        pygame.draw.rect(DISPLAYSURF, BLACK, leftWall)
        drawPaddle(paddle)
        drawBall(ball)

        ball = moveBall(ball, ballDirX, ballDirY)
        ballDirX, ballDirY = checkEdgeCollision(ball, ballDirX, ballDirY)
        ballDirX = ballDirX * checkHitBall(ball, leftWall, paddle, ballDirX)

        pygame.display.update()
        FPSCLOCK.tick(FPS)

if __name__=='__main__':
    main()