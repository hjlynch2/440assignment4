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

def movePaddle(paddle, paddleMovement):
    if (paddleMovement < (1.0/3)): # move down
        if (paddle.bottom + 0.04 * WINDOWHEIGHT * (2.0/FPS)) < WINDOWHEIGHT:
            paddle.y += 0.04 * WINDOWHEIGHT * (2.0/FPS)
    elif(paddleMovement < (2.0/3)): # move up
        if (paddle.top - 0.04 * WINDOWHEIGHT * (2.0/FPS)) > 0:
            paddle.y -= 0.04 * WINDOWHEIGHT * (2.0/FPS)

def gameOver(ball):
    if ball.x > WINDOWWIDTH:
        return True

#Checks is the ball has hit a paddle, and 'bounces' ball off it.     
def checkPaddleHit(ball, paddle, ballDirX):
    if ballDirX > 0 and ball.right > (WINDOWWIDTH - LINETHICKNESS) and paddle.top < ball.top and paddle.bottom > ball.bottom:
        return True 
    else: 
        return False

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