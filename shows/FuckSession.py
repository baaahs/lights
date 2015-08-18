import sheep, time
from color import HSV, RGB


fullShaftRotation = [[39], [39, 32], [39, 32, 35], [39, 32, 35, 36],
                    [39, 32, 35, 36, 33], [39, 32, 35, 36, 33, 26],
                    [39, 32, 35, 36, 33, 26, 27, 28],
                    [39, 32, 35, 36, 33, 26, 27, 28, 29],
                    [39, 32, 35, 36, 33, 26, 27, 28],
                    [39, 32, 35, 36, 33, 26], [39, 32, 35, 36, 33],
                    [39, 32, 35, 36], [39, 32, 35], [39, 32], [39]]

poundShaftRotation = [[39, 32],
                      [39, 32, 35, 36, 33, 26],
                      [39, 32, 35, 36, 33, 26, 27, 28, 29],
                      [39, 32, 35, 36, 33, 26],
                      [39, 32]]

class FuckSession(object):
    def __init__(self, sheep_sides):
        
        self.name = "FuckSession"
        self.createdAt = time.time()
        self.sheep = sheep_sides.both
        self.partyCells = sheep_sides.party
        self.businessCells = sheep_sides.business
        
        self.butt = [51, 52, 53, 54, 55]
        self.tipCellRotation = [[39], [39, 32], [39, 32, 35], [39, 32, 35, 36],
                                [39, 32, 35, 36], [39, 32, 35], [39, 32], [39]]
        self.moneyShotRotation = [[17], [17, 8], [17]]
        
        self.headTone = RGB(255, 200, 201)
        self.chocolateStarfish = RGB(148, 10, 0)
        self.shaftTone = RGB(239, 214, 189)

        self.speed = 1
        self.mode = "start"
        self.count = 0

    def rubTheHole(self):
        self.speed = 0.4
        aDelta = int(time.time() / self.speed) % 5
        lastCell = None
        self.sheep.set_cells(self.butt, self.chocolateStarfish)
        for i in range(len(self.butt)):
            if lastCell:
                self.sheep.set_cell(lastCell, self.chocolateStarfish)
            lastCell = self.butt[i]
            self.sheep.set_cell(self.butt[aDelta], self.shaftTone)

    def justTheTip(self):
        self.speed = 0.7
        aDelta = int(time.time() / self.speed) % 8
        # color the asshole
        self.sheep.set_cells(self.butt, self.chocolateStarfish)

        lastCells = None
        for i in range(len(self.tipCellRotation)):
            if lastCells:
                self.sheep.set_cells(lastCells, RGB(0, 0, 0))
            lastCells = self.tipCellRotation[i]
            self.sheep.set_cells(self.tipCellRotation[aDelta], self.headTone)

    def fullShaftFuck(self, fuckSpeed, fullShaftRotation):
        self.speed = fuckSpeed
        shaftRotation = fullShaftRotation
        aDelta = int(time.time() / self.speed) % (len(shaftRotation))
        # color the asshole
        self.sheep.set_cells(self.butt, self.chocolateStarfish)
        lastCells = None
        for i in range(len(shaftRotation)):
            if lastCells:
                self.sheep.set_cells(lastCells, RGB(0, 0, 0))
            lastCells = shaftRotation[i]
            self.sheep.set_cells(shaftRotation[aDelta], self.headTone)

    def moneyShot(self, ejaculateSpeed, fullShaftRotation):
        self.speed = ejaculateSpeed
        shaft = fullShaftRotation[2]
        aDelta = int(time.time() / self.speed) % (len(self.moneyShotRotation))
        # color the asshole
        self.sheep.set_cells(self.butt, self.chocolateStarfish)
        # color the shaft
        self.sheep.set_cells(shaft, self.headTone)
        lastCells = None
        for i in range(len(self.moneyShotRotation)):
            if lastCells:
                self.sheep.set_cells(lastCells, RGB(0, 0, 0))
            lastCells = self.moneyShotRotation[i]
            self.sheep.set_cells(self.moneyShotRotation[aDelta], RGB(255, 255, 255))

    def next_frame(self):
        last_cell = None
        while True:

            self.sheep.set_cells(sheep.HEAD, RGB(255, 255, 255))
            self.sheep.set_cells(sheep.EARS, RGB(255, 255, 255))
            self.sheep.set_cells(sheep.NOSE, RGB(255, 255, 255))
            self.sheep.set_cells(sheep.FACE, RGB(255, 255, 255))
            self.sheep.set_cells(sheep.THROAT, RGB(255, 255, 255))
            self.sheep.set_cells(sheep.TAIL, RGB(255, 255, 255))

            if self.mode == "start":
                self.rubTheHole()
                self.count += 1
                if self.count == 20:
                    self.count = 0
                    self.mode = "insertTip"

            elif self.mode == "insertTip":
                self.justTheTip()
                self.count += 1
                if self.count == 10:
                    self.count = 0
                    self.mode = "lightFuck"

            elif self.mode == "lightFuck":
                self.fullShaftFuck(0.08, fullShaftRotation)
                self.count += 1
                if self.count == 40:
                    self.count = 0
                    self.mode = "heavyFuck"

            elif self.mode == "heavyFuck":
                self.fullShaftFuck(0.08, poundShaftRotation)
                self.count += 1
                if self.count == 60:
                    self.count = 0
                    self.mode = "cum"

            elif self.mode == "cum":
                self.moneyShot(0.3, poundShaftRotation)
                self.count += 1
                if self.count == 4:
                    self.sheep.set_all_cells(RGB(0, 0, 0))
                    self.count = 0
                    self.mode = "start"

            yield self.speed
