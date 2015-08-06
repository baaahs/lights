import sys
import color
import math
import time

EYE_COLOR_WHITE         = 0
EYE_COLOR_RED           = 9
EYE_COLOR_ORANGE        = 17
EYE_COLOR_AQUAMARINE    = 25
EYE_COLOR_DEEP_GREEN    = 33
EYE_COLOR_LIGHT_GREEN   = 41
EYE_COLOR_LAVENDER      = 49
EYE_COLOR_PINK          = 57
EYE_COLOR_YELLOW        = 66
EYE_COLOR_MAGENTA       = 74
EYE_COLOR_CYAN          = 83
EYE_COLOR_CTO2          = 92
EYE_COLOR_CTO1          = 101
EYE_COLOR_CTB           = 110
EYE_COLOR_BLUE          = 119

PREDEFINED_COLORS = [
    color.Hex("#000000"),   # Black, but not really used
    color.Hex("#FF0000"),   # Red
    color.Hex("#f97306"),   # Orage
    color.Hex("#ffff00"),   # Yellow
    color.Hex("#00ff00"),   # Green
    color.Hex("#0000ff"),   # Blue
    color.Hex("#7e1e9c"),   # Purple
    color.Hex("#ffffff"),   # White
]

PREDEFINED_COLOR_POS = [
    EYE_COLOR_WHITE,
    EYE_COLOR_RED,
    EYE_COLOR_ORANGE,
    EYE_COLOR_YELLOW,
    EYE_COLOR_DEEP_GREEN,
    EYE_COLOR_BLUE,
    EYE_COLOR_MAGENTA,
    EYE_COLOR_WHITE
]



class ControlsModel(object):
    """
    Holds the state of the user interface for the overall show server. This
    is useful both for re-establishing state in clients that come and go, like
    the TouchOSC client, but also as THE place that shows come to in order
    to understand how they should modify their behavior.

    From the show side, there are a lot of un-encapsulated properties/attributes
    of a ControlsModel instance that can be read. Some key ones are:

        chosenColors[]
        speedMulti
        intensified
        colorized
        modifiers[]

    Shows should try to change what they are doing based on these values. See
    the individual documentation below for more detail about each of them.

    This class understands OSC messages and will update it's internal
    state based on received messages. What happens based on which message
    can be see in incomingOSC()

    The normal MVC interaction is that an OSC message comes in, modifying the
    state stored here. This class then notifies all of it's listeners about
    the state change (via some form of control_XXX method call). One of those
    listeners is probably an instance of the TouchOSC class, which then
    broadcasts a whole bunch of messages to TouchOSC clients so that their
    UIs all stay in sync based on whatever the state modification was.

    Presumably state modifications could come from other UIs like a web
    interface, although nothing like that is currently implemented.

    In general, a show implementation should read from here, but almost
    certainly shouldn't be writing to this object. If anything DOES want
    to write to this guy, then it should be using the setters to ensure that
    appropriate notifications are sent to interested listeners.
    
    """

    

    def __init__(self):
        # Pan and tilt are stored in degrees from the central
        # position. Pan has a range of +/- 270 and tilt has a 
        # range of +/- 135
        self.pEyePan  = 0
        self.pEyeTilt = 0
        self.bEyePan  = 0
        self.bEyeTilt = 0

        # Range 0.0 to 1.0
        self.pDimmer = 1.0
        self.bDimmer = 1.0

        self.eyeMovementLocked = False

        self._lastEyeTouchedWasParty = True

        self.pEyeXYEnable = True
        self.bEyeXYEnable = True
        self.eyeSkyPos = False # If true, XY position is in sky, otherwise on ground
        self.lastYPos = 0
        self.lastXPos = 0

        # The color pos values range from 0 to 127 and refer to
        # a position of the color wheel. Each color occupies an 8
        # value range with the "full" position of that color being
        # in the center of the range. The edge of the ranges are positions
        # where both colors are visible in the output at one time.
        self.pColorPos = 0
        self.bColorPos = 0

        self.pColorEnable = True
        self.bColorEnable = True
        self.colorMix = False
        self.colorCycleSpeed = 0

        # The RGB values of the chosen colors
        self.chosenColors = [ color.RGB(255, 255, 0), color.RGB(0,255,255) ]
        # Color wheel positions
        self.chosenColorsPos = [ EYE_COLOR_WHITE, EYE_COLOR_WHITE ]

        # Chosen indexes. Could be -1
        self.chosenColorsIx = [7, 7]


        # Color presets. Mapped to 100+ix for choices above
        self.colorPresets = [ 
            color.Hex("#000000"),   # 0 isn't used in the UI
            color.Hex("#ff8080"),   # carnation pink
            color.Hex("#ff964f"),   # pastel orange
            color.Hex("#feff7f"),   # faded yellow
            color.Hex("#cffdbc"),   # very pale green
            color.Hex("#d6fffe"),   # very pale blue
            color.Hex("#eecffe"),   # pale lavender
            color.Hex("#808080"),   # mid gray
        ]

        # Since pos calculations from RGB are complex we try to cache this for the
        # presets at least
        self.colorPresetsToPos = []
        for ix in range(0, len(self.colorPresets)):
            self.colorPresetsToPos.append(self.colorPresets[ix].pos)


        ## Speed setting. This is multiplied against the "rate", so that
        # means if you're calculating delays, 2.0 here should result in 
        # calculating a delay half as long. This will be done automatically
        # by the show runner if you are yielding something more than about 0.001,
        # but if you are doing proper time based "as fast as we can" calculations
        # yourself, you will need to respect this value.
        self.speedMulti = 1.0

        # A value that ranges from -1.0 (maximum calm) to 1.0 (maximum intensity).
        # It should be interpretted by each show in a show appropriate manner
        self.intensified = 0.0

        # A value that ranges from -1.0 (totally monochrome) to 1.0 (max color).
        # If the currently running show does not set handles_colorized to True this
        # will be handled by the system, otherwise it is left to the show to modify
        # it's colors appropriately
        self.colorized = 0.0

        # There are 7 modifiers that a show can interpret as it wishes.
        # Conventions may be established around general concepts that these toggles
        # represent, but until that happens it's a free for all.
        self.modifiers = [False,False,False,False,False,False,False]

        self.listeners = set()

        self._tapTimes = []

        # Start with a muddy yellow because starting with black goes badly/is silly
        self.color = color.RGB(255,255,0)


    def addListener(self, listener):
        self.listeners.add(listener)

    def delListener(self, listener):
        self.listeners.discard(listener)

    def incomingOSC(self, addr, tags, data, source):
        print "incomingOSC %s: %s [%s] %s" % (source, addr, tags, str(data))

        aSplit = addr.split("/")
        print aSplit

        if aSplit[1] == "main":
            if aSplit[2] == "color":
                try:
                    self.setColorIx(int(aSplit[3]), int(aSplit[4]))
                except:
                    pass

            elif aSplit[2] == "speed":
                if aSplit[3] == "reset":
                    self.speedReset()
                elif aSplit[3] == "changeRel":
                    self.speedChangeRel(data[0])
                elif aSplit[3] == "tap":
                    if int(data[0]) == 1:
                        self.speedTap()


            elif aSplit[2] == "intensified":
                self.setIntensified(data[0])
            elif aSplit[2] == "colorized":
                self.setColorized(data[0])
            elif aSplit[2] == "modifier":
                self.toggleModifier(int(aSplit[3]))


        elif aSplit[1] == "color":
            if aSplit[2] == "red":
                self.setColorR(data[0])
            elif aSplit[2] == "green":
                self.setColorG(data[0])
            elif aSplit[2] == "blue":
                self.setColorB(data[0])
            elif aSplit[2] == "hue":
                self.setColorH(data[0])
            elif aSplit[2] == "sat":
                self.setColorS(data[0])
            elif aSplit[2] == "val":
                self.setColorV(data[0])

        elif aSplit[1] == "eyes":
            if aSplit[2] == "pPan":
                self.setEyePan(True, data[0])
            elif aSplit[2] == "bPan":
                self.setEyePan(False, data[0])
            elif aSplit[2] == "pTilt":
                self.setEyeTilt(True, data[0])
            elif aSplit[2] == "bTilt":
                self.setEyeTilt(False, data[0])
            elif aSplit[2] == "movementLock":
                self.setEyeMovementLock(data[0] == 1.0)

            elif aSplit[2] == "xyPos":
                self.setEyeXYPos(data[0], data[1])
            elif aSplit[2] == "xPos":
                self.setEyeXYPos(data[0],self.lastYPos)
            elif aSplit[2] == "yPos":
                self.setEyeXYPos(self.lastXPos,data[0])

            elif aSplit[2] == "pXYEnable":
                self.toggleEyeXYEnable(True)
            elif aSplit[2] == "bXYEnable":
                self.toggleEyeXYEnable(False)
            elif aSplit[2] == "skyPos":
                self.toggleEyeSkyPos()

            elif aSplit[2] == "dimmer":
                self.setDimmer(aSplit[3]=="1", data[0])

            elif aSplit[2] == "pColorEnable":
                self.toggleEyeColorEnabled(True)
            elif aSplit[2] == "bColorEnable":
                self.toggleEyeColorEnabled(False)
            elif aSplit[2] == "colorMix":
                self.toggleEyeColorMix()
            elif aSplit[2] == "colorCycle":
                self.toggleEyeColorCycle(data[0])

            # The colors, all the colors
            # These are pushbuttons, so we will get a 1.0 and a 0.0 event. Thus
            # we only bother setting it on the 1.0 event, although technically it
            # wouldn't hurt to set it twice. It would just be wasteful.
            elif aSplit[2] == "colorWhite":
                if data[0] == 1.0:
                    self.setEyeColor(EYE_COLOR_WHITE)
            elif aSplit[2] == "colorRed":
                if data[0] == 1.0:
                    self.setEyeColor(EYE_COLOR_RED)
            elif aSplit[2] == "colorOrange":
                if data[0] == 1.0:
                    self.setEyeColor(EYE_COLOR_ORANGE)
            elif aSplit[2] == "colorAquamarine":
                if data[0] == 1.0:
                    self.setEyeColor(EYE_COLOR_AQUAMARINE)
            elif aSplit[2] == "colorDeepGreen":
                if data[0] == 1.0:
                    self.setEyeColor(EYE_COLOR_DEEP_GREEN)
            elif aSplit[2] == "colorLightGreen":
                if data[0] == 1.0:
                    self.setEyeColor(EYE_COLOR_LIGHT_GREEN)
            elif aSplit[2] == "colorLavender":
                if data[0] == 1.0:
                    self.setEyeColor(EYE_COLOR_LAVENDER)
            elif aSplit[2] == "colorPink":
                if data[0] == 1.0:
                    self.setEyeColor(EYE_COLOR_PINK)
            elif aSplit[2] == "colorYellow":
                if data[0] == 1.0:
                    self.setEyeColor(EYE_COLOR_YELLOW)
            elif aSplit[2] == "colorMagenta":
                if data[0] == 1.0:
                    self.setEyeColor(EYE_COLOR_MAGENTA)
            elif aSplit[2] == "colorCyan":
                if data[0] == 1.0:
                    self.setEyeColor(EYE_COLOR_CYAN)
            elif aSplit[2] == "colorCTO2":
                if data[0] == 1.0:
                    self.setEyeColor(EYE_COLOR_CTO2)
            elif aSplit[2] == "colorCTO1":
                if data[0] == 1.0:
                    self.setEyeColor(EYE_COLOR_CTO1)
            elif aSplit[2] == "colorCTB":
                if data[0] == 1.0:
                    self.setEyeColor(EYE_COLOR_CTB)
            elif aSplit[2] == "colorBlue":
                if data[0] == 1.0:
                    self.setEyeColor(EYE_COLOR_BLUE)


        elif aSplit[1] == "global":
            if aSplit[2] == "refresh":
                self._notifyRefresh()




    def setColorR(self, r):
        # Convert from float to byte
        rNew = round(255 * r)
        if rNew == self.color.r:
            return

        self.color.r = rNew
        self._notifyColor()

    def setColorG(self, v):
        # Convert from float to byte
        vNew = round(255 * v)
        if vNew == self.color.g:
            return

        self.color.g = vNew
        self._notifyColor()

    def setColorB(self, v):
        # Convert from float to byte
        vNew = round(255 * v)
        if vNew == self.color.b:
            return

        self.color.b = vNew
        self._notifyColor()

    def setColorH(self, v):
        if v == self.color.h:
            return

        self.color.h = v
        self._notifyColor()

    def setColorS(self, v):
        if v == self.color.s:
            return

        self.color.s = v
        self._notifyColor()

    def setColorV(self, v):
        if v == self.color.v:
            return

        self.color.v = v
        self._notifyColor()

    def _notifyColor(self):
        print "_notifyColor"
        for listener in self.listeners:
            if listener.control_colorChanged:
                listener.control_colorChanged()
    
    def setEyeMovementLock(self, locked):
        print "setEyeMovementLock %s" % str(locked)
        # if locked == self.eyeMovementLocked:
        #     return

        self.eyeMovementLocked = locked
        if self.eyeMovementLocked:
            if self._lastEyeTouchedWasParty:
                # Make the business eye match the party eye
                self.bEyeTilt = self.pEyeTilt
                self.bEyePan = self.pEyePan
                self._notifyEyeChanged(False)
            else:
                # Make the party eye follow the business eye
                self.pEyeTilt = self.bEyeTilt
                self.pEyePan = self.bEyePan
                self._notifyEyeChanged(True)

        self._notifyEyeMovementLockChanged()

    def setEyeTilt(self, isParty, tiltValue):
        tiltValue = math.floor(tiltValue)
        if tiltValue < -135:
            tiltValue = -135
        if tiltValue > 135:
            tiltValue = 135

        self._lastEyeTouchedWasParty = isParty

        if self.pEyeTilt != tiltValue and (isParty or self.eyeMovementLocked):
            self.pEyeTilt = tiltValue
            self.pEyeXYEnable = False
            self._notifyEyeChanged(True)

        if self.bEyeTilt != tiltValue and (not isParty or self.eyeMovementLocked):
            self.bEyeTilt = tiltValue
            self.bEyeXYEnable = False
            self._notifyEyeChanged(False)

    def setEyePan(self, isParty, panValue):
        panValue = math.floor(panValue)
        if panValue < -270:
            panValue = -270
        if panValue > 270:
            panValue = 270

        self._lastEyeTouchedWasParty = isParty

        if self.pEyePan != panValue and (isParty or self.eyeMovementLocked):
            self.pEyePan = panValue
            self.pEyeXYEnable = False
            self._notifyEyeChanged(True)

        if self.bEyePan != panValue and (not isParty or self.eyeMovementLocked):
            self.bEyePan = panValue
            self.bEyeXYEnable = False
            self._notifyEyeChanged(False)

    def setDimmer(self, isParty, dimVal):
        "Sets dimmer for one eye to dimVal. Range of 0.0 to 1.0"
        if dimVal < 0:
            dimVal = 0
        elif dimVal > 1.0:
            dimVal = 1.0

        if self.pDimmer != dimVal and (isParty or self.eyeMovementLocked):
            self.pDimmer = dimVal
            self._notifyEyeChanged(True)

        if self.bDimmer != dimVal and (not isParty or self.eyeMovementLocked):
            self.bDimmer = dimVal
            self._notifyEyeChanged(False)

    def setEyeXYPos(self, x, y):
        #
        # Basic formula is pan = atan(x), tilt = atan( (y * sin(pan)) / x )
        #

        if y < -0.5:
            y = -0.5

        self.lastXPos = x
        self.lastYPos = y

        # Units for X and Y real are "height of the eye" = 1. Scaling out so
        # that we can tweak it more here than in touch and can define a reasonable
        # addressable area
        xr = 3 * x
        yr = 3 * y

        if self.pEyeXYEnable:
            panRads = math.atan2(xr,1)
            tiltRads = math.atan2( yr * math.sin(math.fabs(panRads)), xr)
            self.pEyePan = math.degrees(panRads)
            self.pEyeTilt = math.degrees(tiltRads) - 90
            if self.pEyeTilt < 0:
                self.pEyeTilt += 360
            if self.pEyeTilt > 180:
                self.pEyeTilt = 360-self.pEyeTilt

            print "P x=%f y=%f pan=%f tilt=%f" % (xr,yr, self.pEyePan, self.pEyeTilt)
            if self.pEyeTilt > 135:
                self.pEyeTilt = 135

            if self.eyeSkyPos:
                self.pEyePan = 360-self.pEyePan

            self._notifyEyeChanged(True)

        if self.bEyeXYEnable:
            xr -= 0.25 # This is (roughly) the distance between the lights in light_to_ground units
            panRads = math.atan2(xr,1)
            tiltRads = math.atan2( yr * math.sin(math.fabs(panRads)), xr)
            self.bEyePan = math.degrees(panRads)
            self.bEyeTilt = math.degrees(tiltRads) - 90
            if self.bEyeTilt < 0:
                self.bEyeTilt += 360
            if self.bEyeTilt > 180:
                self.bEyeTilt = 360-self.bEyeTilt

            print "B x=%f y=%f pan=%f tilt=%f" % (xr,yr, self.bEyePan, self.bEyeTilt)
            if self.bEyeTilt > 135:
                self.bEyeTilt = 135

            if self.eyeSkyPos:
                self.bEyePan = 360-self.bEyePan

            self._notifyEyeChanged(False)



    def toggleEyeXYEnable(self, isParty):
        if isParty:
            self.pEyeXYEnable = not self.pEyeXYEnable
        else:
            self.bEyeXYEnable = not self.bEyeXYEnable

        self._notifyEyeChanged(isParty)

    def toggleEyeSkyPos(self):
        self.eyeSkyPos = not self.eyeSkyPos
        self.setEyeXYPos(self.lastXPos, self.lastYPos)

        # Do a fake one here just in case it didn't happen already
        if not self.pEyeXYEnable and not self.bEyeXYEnable:
            self._notifyEyeChanged(True)



    def _notifyEyeChanged(self, isParty):
        print "_notifyEyeChanged isParty=%s" % isParty
        for listener in self.listeners:
            try:
                listener.control_eyeChanged(isParty)
            except AttributeError:
                pass # whatever...

    def _notifyEyeMovementLockChanged(self):
        for listener in self.listeners:
            try:
                listener.control_eyeMovementLockChanged()
            except AttributeError:
                pass # whatever...



    def setEyeColor(self, val):
        val = math.floor(val)
        if self.colorMix:
            val += 4

        if self.pColorEnable:
            self.pColorPos = val
        if self.bColorEnable:
            self.bColorPos = val

        self.colorCycleSpeed = 0

        self._notifyEyeColorChanged()

    def toggleEyeColorEnabled(self, isParty):
        if isParty:
            self.pColorEnable = not self.pColorEnable
        else:
            self.bColorEnable = not self.bColorEnable

        # While this isn't strictly true, it will cause the toggle state
        # of the UI button to change, which we want
        self._notifyEyeColorChanged()

    def toggleEyeColorMix(self):
        self.colorMix = not self.colorMix
        self._notifyEyeColorChanged()

    def toggleEyeColorCycle(self, speed):
        self.colorCycleSpeed = math.floor(speed)
        self._notifyEyeColorChanged()

    def _notifyEyeColorChanged(self):
        for listener in self.listeners:
            try:
                listener.control_eyeColorChanged()
            except AttributeError:
                pass # whatever...

    ############
    def _notifyRefresh(self):
        for listener in self.listeners:
            try:
                listener.control_refreshAll()
            except AttributeError:
                pass # whatever...


    ############
    # Main interface

    def setColorIx(self, cIx, vIx):
        """
        Set the color at index cIx to the value at index vIx. For vIx < 100
        this is a predefined color. For vIx > 100 it is a macro color that
        can be changed using the tech interface.
        """
        if cIx < 0 or cIx > 1:
            print "Don't understand color ix %d" % cIx
            return

        self.chosenColorsIx[cIx] = vIx

        if vIx < 100:
            self.chosenColors[cIx] = PREDEFINED_COLORS[vIx]
            self.chosenColorsPos[cIx] = PREDEFINED_COLOR_POS[vIx]
        else:
            self.chosenColors[cIx] = self.colorPresets[vIx-100]
            self.chosenColorsPos[cIx] = self.colorPresetsToPos[vIx-100]

        self._notifyChosenColorChanged(cIx)

    def _notifyChosenColorChanged(self, cIx):
        for listener in self.listeners:
            try:
                listener.control_chosenColorChanged(cIx)
            except AttributeError:
                pass # ignore


    def speedReset(self):
        self.speedMulti = 1.0

        self._notifySpeedChanged()

    def speedChangeRel(self, amt):
        # Scale this value some so it's a log scale or similar?
        self.speedMulti = 1.0 + amt
        if self.speedMulti <= 0.0:
            self.speedMulti = 0.01

        self._notifySpeedChanged()

    def speedTap(self):
        now = time.time()
        if len(self._tapTimes) == 0:
            # It is the first tap so record it and move on
            self._tapTimes.append(now)
            print "First tap"
            return

        # There is at least one previous time.

        # How long has it been? There is a maximum amount of time between taps
        # that corresponds to some low bpm after which we start over
        elapsed = now - self._tapTimes[len(self._tapTimes) - 1] 

        if elapsed > 2.0:
            # OMG! So long ago! It's totally time to reset
            self._tapTimes = [now]
            print "Elapsed was %f, resettting" % elapsed
            return

        # Hmm, okay, not all that old, so let's add it and then process
        # all of them if we can
        self._tapTimes.append(now)

        while len(self._tapTimes) > 16:
            self._tapTimes.pop(0)

        # There are now 1 to 8 elements in the list
        if len(self._tapTimes) < 4:
            # Not enough
            print "Only have %d taps, not enough" % len(self._tapTimes)
            return

        # I'm not sure if this is the "right" way to find intervals, but it makes sense to me.
        # Rather than just average from the begining time to the end time, we convert the times
        # into intervals and then average the intervals
        intTotal = 0.0
        numInts = 0
        last = 0.0
        for ix, v in enumerate(self._tapTimes):            
            if ix == 0:
                last = v
                continue
            intTotal += v - last
            last = v
            numInts += 1

        avgInterval = intTotal / numInts

        # Reference time is 120bpm, which is 0.5s between quarter notes (i.e. taps)
        print "avgInterval=%f  intTotal=%f numInts=%d" % (avgInterval, intTotal, numInts)
        self.speedMulti = 0.5 / avgInterval

        self._notifySpeedChanged()





    def _notifySpeedChanged(self):
        print "_notifySpeedChanged"
        for listener in self.listeners:
            try:
                listener.control_speedChanged()
            except AttributeError:
                pass # ignore



    def setIntensified(self, val):
        self.intensified = val

        self._notifyIntensifiedChanged()


    def _notifyIntensifiedChanged(self):
        print "_notifyIntensifiedChanged"
        for listener in self.listeners:
            try:
                listener.control_intensifiedChanged()
            except AttributeError:
                pass # ignore

    def setColorized(self, val):
        self.colorized = val

        self._notifyColorizedChanged()


    def _notifyColorizedChanged(self):
        print "_notifyColorizedChanged"
        for listener in self.listeners:
            try:
                listener.control_colorizedChanged()
            except AttributeError:
                pass # ignore

    def toggleModifier(self, mIx):
        mIx = color.clamp(mIx, 0, len(self.modifiers))

        self.modifiers[mIx] = not self.modifiers[mIx]

        self._notifyModifiersChanged()

    def _notifyModifiersChanged(self):
        print "_notifyModifiersChanged"
        for listener in self.listeners:
            try:
                listener.control_modifiersChanged()
            except AttributeError:
                pass # ignore



