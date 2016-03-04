#
# Happy Mom color theme Equalizer
#
# 3-Horizontal bands pulse
#
# Touch OSC controls the amount of each band
#

import sheep
import time
from math import sin
from random import randint, choice
from color import RGB, HSV

# Converts a 0-1536 color into rgb on a wheel by keeping one of the rgb channels off

MaxColor = 1536

def Wheel(color):
	color = color % 1536  # just in case color is out of bounds
	channel = color / 255
	value = color % 255

	if channel == 0:
		r = 255
		g = value
		b = 0
	elif channel == 1:
		r = 255 - value
		g = 255
		b = 0
	elif channel == 2:
		r = 0
		g = 255
		b = value
	elif channel == 3:
		r = 0
		g = 255 - value
		b = 255
	elif channel == 4:
		r = value
		g = 0
		b = 255
	else:
		r = 255
		g = 0
		b = 255 - value

	return RGB(r,g,b)

class HappyMom_EQ(object):
	def __init__(self, sheep_sides):
		self.name = "HappyMom_EQ"
		self.sheep = sheep_sides.both
		self.eq_max = 17
		self.black = RGB(0,0,0)
		self.rate_min = 1
		self.rate_max = 10

		self.cell_map = sheep.VSTRIPES

		self.rates = []
		for i in range(len(self.cell_map)):
			self.rates.append(randint(self.rate_min,self.rate_max))

		# self.rates = [
		# 	,
		# 	randint(self.rate_min,self.rate_max),
		# 				randint(self.rate_min,self.rate_max)]

		self.eqlizer = [0] * len(self.cell_map)	# Random initial values
		self.eq_colors = (RGB(63,184,175),	#1
							RGB(127,199,175),	#2
							RGB(255,158,157),	#3
							RGB(255,61,127),	#4
							RGB(63,184,175),	#5
							RGB(218,216,167),	#6
							RGB(255,158,157),	#7
							RGB(255,61,127),	#8
							RGB(63,184,175),	#9
							RGB(218,216,167),	#10
							RGB(127,199,175),	#11
							RGB(255,158,157),	#12
							RGB(255,61,127),	#13
							RGB(255,158,157),	#14
							RGB(127,199,175),	#15
							RGB(63,184,175),	#16
							RGB(255,61,127))	#17

		self.speed = 0.1

		# self.cell_map = (sheep.LOW, sheep.MEDIUM, sheep.HIGH)
	# 	self.last_osc = time.time()
	# 	self.OSC = False	# Is Touch OSC working?

	# def set_param(self, name, val):
	# 	# name will be 'colorR', 'colorG', 'colorB'
	# 	rgb255 = int(val * 0xff)
	# 	if name == 'colorR':
	# 		self.eqlizer[0] = rgb255 * self.eq_max / 255
	# 		self.last_osc = time.time()
	# 		self.OSC = True
	# 	if name == 'colorG':
	# 		self.eqlizer[1] = rgb255 * self.eq_max / 255
	# 		self.last_osc = time.time()
	# 		self.OSC = True
	# 	if name == 'colorB':
	# 		self.eqlizer[2] = rgb255 * self.eq_max / 255
	# 		self.last_osc = time.time()
	# 		self.OSC = True

	def next_frame(self):
		while (True):

			self.poll_time()
			self.draw_equalizer()

			for y in range (len(self.cell_map)):
				if randint(0,20) == 1:
					self.rates[y] = randint(self.rate_min, self.rate_max)

			yield self.speed

	def poll_time(self):
		t = time.time()
		for y in range(len(self.cell_map)):
			self.eqlizer[y] = ((sin(t * self.rates[y])) + 1) * len(self.cell_map[y]) / 2

	def draw_equalizer(self):
		for y in range (len(self.cell_map)):
			stripe_len = len(self.cell_map[y])
			for x in range(stripe_len):
				#x = stripe_len - 1 - r
				if x >= self.eqlizer[y]:
					color = self.black
				else:
					c_ix = int((float(x)/stripe_len) * len(self.eq_colors))
					color = self.eq_colors[c_ix]
				self.sheep.set_cell(self.cell_map[y][x], color)
