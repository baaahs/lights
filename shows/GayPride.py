import time
from math import sin, cos
from random import randint, choice
import sheep, controls_model
from color import RGB, HSV

class GayPride(object):
    """
    GAY PRIDE FLAG COLORS:
      PRIDE_RED = RGB(228, 3, 3)
      PRIDE_ORANGE = RGB(255, 140, 0)
      PRIDE_YELLOW = RGB(255, 237, 0)
      PRIDE_GREEN = RGB(0, 128, 38)
      PRIDE_BLUE = RGB(0, 77, 255)
      PRIDE_PURPLE = RGB(117, 7, 135)
      """
    def __init__(self, sheep_sides):
        self.name = "GayPride"
        self.createdAt = time.time()
        self.BUTT = sheep.BUTT
        self.p = sheep_sides.partyEye
        self.b = sheep_sides.businessEye
        self.eq_max = 17
        self.black = RGB(0,0,0)
        self.rate_min = 1
        self.rate_max = 10
        self.rates = [randint(self.rate_min,self.rate_max),
						randint(self.rate_min,self.rate_max),
						randint(self.rate_min,self.rate_max)]

        # Mirror drawing to both sides of the bus. Can also
        # treat the two sides separately.
        # choices: [both, party, business]
        self.cells = sheep_sides.both
        self.partyCells = sheep_sides.party
        self.businessCells = sheep_sides.business

        # color to draw
        self.eqlizer = [0,0,0]	# Random initial values

        self.eq_colors = (RGB(228, 3, 3),	#1
							RGB(228, 3, 3),	#2
							RGB(255, 140, 0),	#3
							RGB(255, 140, 0),	#4
							RGB(255, 237, 0),	#5
							RGB(255, 237, 0),	#6
							RGB(0, 128, 38),	#7
							RGB(0, 128, 38),	#8
							RGB(0, 77, 255),	#9
							RGB(0, 77, 255),	#10
							RGB(0, 77, 255),	#11
							RGB(117, 7, 135),	#12
							RGB(117, 7, 135),	#13
							RGB(117, 7, 135),	#14
							RGB(117, 7, 135),	#15
							RGB(117, 7, 135),	#16
							RGB(117, 7, 135))	#17
        self.cell_map = (sheep.LOW, sheep.MEDIUM, sheep.HIGH)

        self.face = sheep.FACE
        self.ears = sheep.EARS
        self.head = sheep.HEAD
        self.nose = sheep.NOSE
        self.throat = sheep.THROAT
        self.breast = sheep.BREAST

        self.OSC = False

        # number of seconds to wait between frames
        self.frame_delay = 1

    def set_param(self, name, val):
        """
        Receive a command from OSC or other external controller
        'name' is the name of the value being set
        'val' is a floating point number between 0.0 and 1.0
        See 'doc/OSC.md' for details on the named parameters

        This example responds to three color sliders (corresponding
        to R, G and B) in the OSC controller to set the primary
        color of the show.  RGB color values range from 0-255, so
        we must convert the input value.
        """
        # name will be 'colorR', 'colorG', 'colorB'
        rgb255 = int(val * 255)
        if name == 'colorR':
            self.color.r = rgb255
        elif name == 'colorG':
            self.color.g = rgb255
        elif name == 'colorB':
            self.color.b = rgb255

    def drawFrontAndButt(self):
        buttCells = [[51], [50], [52], [53, 56], [54, 55], [57, 58]]
        gayPrideColors = [RGB(228, 3, 3),
                          RGB(255, 140, 0),
                          RGB(255, 237, 0),
                          RGB(0, 128, 38),
                          RGB(0, 77, 255),
                          RGB(117, 7, 135)]
        colorVolume = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]

        aDelta = int(time.time() - self.createdAt) % 6

        for i in range(len(buttCells)):
            self.cells.set_cells(buttCells[i], gayPrideColors[i])
            gayPrideColors[i].v -= colorVolume[aDelta]
            if gayPrideColors[i].v <= .1:
                gayPrideColors[i].v += colorVolume[5]
        self.cells.set_cells(self.face, gayPrideColors[0])
        self.cells.set_cells(self.ears, gayPrideColors[1])
        self.cells.set_cells(self.head, gayPrideColors[2])
        self.cells.set_cells(self.nose, gayPrideColors[3])
        self.cells.set_cells(self.throat, gayPrideColors[4])
        self.cells.set_cells(self.breast, gayPrideColors[5])


    def poll_time(self):
        t = time.time()
        for y in range (3):
            self.eqlizer[y] = ((sin(t * self.rates[y])) + 1) * len(self.cell_map[y]) / 2

    def draw_equalizer(self):
        for y in range (3):
    	       for x in range (len(self.cell_map[y])):
                   if x >= self.eqlizer[y]:
                       color = self.black
                   else:
                       color = self.eq_colors[x]
                   self.cells.set_cell(self.cell_map[y][x], color)

    def rotateEyeColor(self):
        # create a list of eyecolors that represent the pride flag
        prideEyeColors = [ controls_model.EYE_COLOR_RED,
                           controls_model.EYE_COLOR_ORANGE,
                           controls_model.EYE_COLOR_YELLOW,
                           controls_model.EYE_COLOR_DEEP_GREEN,
                           controls_model.EYE_COLOR_MAGENTA,
                           controls_model.EYE_COLOR_BLUE ]
        # Use time to loop through the list of prideEyeColors
        # mod 6 because there are 6 colors in the list
        aDelta = int((time.time() - self.createdAt)) % 6

        # Set business eye:
        self.b.colorPos = prideEyeColors[aDelta]
        # Set party eye:
        self.p.colorPos = prideEyeColors[aDelta]

    def next_frame(self):

        while True:
            # clear whatever was drawn last frame
            self.cells.clear()

            self.poll_time()
            self.draw_equalizer()
            self.drawFrontAndButt()
            self.rotateEyeColor()

            # then wait to draw the next frame
            yield self.frame_delay
