from random import randint

class Color:
	white = (255, 255, 255)
	black = (0, 0, 0)
	red = (240, 20, 20)
	green = (20, 240, 20)
	blue = (20, 20, 240)
	orange = (220, 220, 20)
	gray = (125, 125, 125)

	@staticmethod
	def random(minc=0, maxc=255):
		return (randint(minc, maxc), randint(minc, maxc), randint(minc, maxc))