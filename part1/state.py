import math

class state:

	def __init__(self, ball_x, ball_y, v_x, v_y, paddle_y):
		self.ball_x = ball_x
		self.ball_y = ball_y
		self.v_x = v_x
		self.v_y = v_y
		self.paddle_y = paddle_y

	def printState(self):
		print '(' + str(self.ball_x) + ', ' + str(self.ball_y) + ', ' + str(self.v_x) + ', ' + str(self.v_y) + ', ' + str(self.paddle_y) + ')'

	def getState(self):
		b_x = self.getXState()
		b_y = self.getYState()
		v_x = self.getVXState()
		v_y = self.getVYState()
		p_y = self.getPaddleState()
		return (b_x, b_y, v_x, v_y, p_y)

	def getVXState(self):
	    if self.v_x < 0:
	        return -1
	    else:
	        return 1

	def getVYState(self):
	    if abs(self.v_y) < 0.015:
	        return 0
	    elif self.v_y < 0:
	        return -1
	    else:
	        return 1

	def getPaddleState(self):
	    return int(math.floor((self.paddle_y * 12)/(0.8)))

	def getXState(self):
		if self.ball_x >= 1:
			return 11
		if self.ball_x < 0:
			return 0
		return int(self.ball_x * 12)

	def getYState(self):
		if self.ball_y >= 1:
			return 11
		if self.ball_y < 0:
			return 0
		return int(self.ball_y * 12)