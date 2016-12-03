class state:

	def __init__(self, ball_x, ball_y, v_x, v_y, paddle_y):
		self.ball_x = ball_x
		self.ball_y = ball_y
		self.v_x = v_x
		self.v_y = v_y
		self.paddle_y = paddle_y

	def printState(self):
		print '(' + str(self.ball_x) + ', ' + str(self.ball_y) + ', ' + str(self.v_x) + ', ' + str(self.v_y) + ', ' + str(self.paddle_y) + ')'