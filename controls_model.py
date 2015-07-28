import sys
import color
import math

EYE_COLOR_WHITE         = 5
EYE_COLOR_RED           = 13
EYE_COLOR_ORANGE        = 21
EYE_COLOR_AQUAMARINE    = 29
EYE_COLOR_DEEP_GREEN    = 37
EYE_COLOR_LIGHT_GREEN   = 45
EYE_COLOR_LAVENDER      = 53
EYE_COLOR_PINK          = 62
EYE_COLOR_YELLOW        = 70
EYE_COLOR_MAGENTA       = 79
EYE_COLOR_CYAN          = 88
EYE_COLOR_CTO2          = 97
EYE_COLOR_CTO1          = 106
EYE_COLOR_CTB           = 115
EYE_COLOR_BLUE          = 124

class ControlsModel(object):
    """
    Models a set of controls & states that serves as a meeting place for
    both shows, who want to know what the values of various controls are,
    OSC clients that will change those controls, TouchOSC clients that
    are able to modify their behavior based on some of those states, and
    (potentially) web pages or other clients that are similar.

    Every control that shows up in a TouchOSC layout should be represented
    here so that we can save the state when it is modified and broadcast
    that state to all other TouchOSC instances. This also lets us restore
    the control to it's proper value when you leave the TouchOSC app and
    return.
    """

    

    def __init__(self):
        self.listeners = set()

        # Start with a muddy yellow because starting with black goes badly/is silly
        self.color = color.RGB(255,255,0)

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

    def addListener(self, listener):
        self.listeners.add(listener)

    def delListener(self, listener):
        self.listeners.discard(listener)

    def incomingOSC(self, addr, tags, data, source):
        print "incomingOSC %s: %s [%s] %s" % (source, addr, tags, str(data))

        aSplit = addr.split("/")
        print aSplit

        if aSplit[1] == "color":
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
