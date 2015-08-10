import math
import eye_effect


import controls_model as controls
from color import clamp
import config

EYE_DMX_PAN         = 1
EYE_DMX_PAN_FINE    = 2
EYE_DMX_TILT        = 3
EYE_DMX_TILT_FINE   = 4
EYE_DMX_COLOR       = 5
EYE_DMX_STROBE      = 6
EYE_DMX_DIMMER      = 7
EYE_DMX_GOBO        = 8
EYE_DMX_EFFECT      = 9
EYE_DMX_LADDER_ROTATE   = 10
EYE_DMX_8_ROTATE        = 11
EYE_DMX_3_ROTATE        = 12
EYE_DMX_FOCUS           = 13
EYE_DMX_FROST           = 14
EYE_DMX_PNT_SPEED       = 15
EYE_DMX_LAMP            = 16

class Eye(object):

    def __init__(self, model, side):
        self.model = model
        self.cm = None
        self.side = side

        # These are the values that the show has set. If in override
        # mode we will be ignoring them and will be using the values from
        # the control model. These might still get changed while overridden,
        # in which case they will be used when the override is over.
        
        # Pan has a range of -270 to +270 
        self._pan = 0.0

        # Tilt is -135 to +135
        self._tilt = 0.0

        self.last_x_pos = 0
        self.last_y_pos = 0

        # Color wheel position ranges from 0 to 127. See comments in
        # controls_model.py
        self.color_pos = 0

        # Range of 0 to 1.0
        self.dimmer = 1.0

        self.effect = None

        self._brightness = 1.0

    def __repr__(self):
        return "Eye side=%s" % self.side

    @property
    def tilt(self):
        return self._tilt

    @tilt.setter
    def tilt(self, val):
        self._tilt = clamp(float(val), -270.0, 270.0)

    @property
    def pan(self):
        return self._pan

    @pan.setter
    def pan(self, val):
        self._pan = clamp(float(val), -135.0, 135.0)

    def set_brightness(self, val):
        self._brightness = val

    def go(self):
        """
        Copy our data into the model, translating to DMX and
        using the proper source based on override mode.
        """

        pan = self._pan
        tilt = self._tilt
        color_pos = self.color_pos
        dimmer = self.dimmer

        s = self.side=="p"

        effect = self.effect
        ext_speed = 0.0

        if self.cm:
            if self.cm.eyes_mode == controls.EYES_MODE_HEADLIGHTS:
                color_pos = 0
                effect = None
                dimmer = 1.0
                if s:
                    pan = float(self.cm.p_eye_pos[controls.PAN])
                    tilt = float(self.cm.p_eye_pos[controls.TILT])
                #     color_pos = self.cm.pColorPos
                #     dimmer = self.cm.pDimmer
                else:
                    pan = float(self.cm.b_eye_pos[controls.PAN])
                    tilt = float(self.cm.b_eye_pos[controls.TILT])
                    # color_pos = self.cm.bColorPos
                    # dimmer = self.cm.bDimmer
            elif self.cm.eyes_mode == controls.EYES_MODE_DISCO and s:
                pan = float(self.cm.p_eye_pos[controls.PAN])
                tilt = float(self.cm.p_eye_pos[controls.TILT])
                dimmer = self.cm.disco_brightness
                color_pos = self.cm.disco_color_pos

                # Add in the mix value here
                if self.cm.disco_mix:
                    color_pos += 6

                effect = None
                if self.cm.disco_effect > 0 and self.cm.disco_effect <= len(self.cm.effects):
                    ix = self.cm.disco_effect - 1
                    # print "Using effect %d" % ix
                    effect = self.cm.effects[ix]
                    ext_speed = self.cm.disco_effect_speed
        

        # Translate these into proper DMX ranged values
        dPan = int(((pan+270.0) / 540.0) * 0x0000ffff)
        self.model.set_eye_dmx(s, EYE_DMX_PAN, ((dPan >> 8) & 0x00ff))
        self.model.set_eye_dmx(s, EYE_DMX_PAN_FINE, (dPan & 0x00ff))

        dTilt = int(((tilt+135.0) / 270.0) * 0x0000ffff)
        self.model.set_eye_dmx(s, EYE_DMX_TILT, ((dTilt >> 8) & 0x00ff))
        self.model.set_eye_dmx(s, EYE_DMX_TILT_FINE, (dTilt & 0x00ff))

        self.model.set_eye_dmx(s, EYE_DMX_COLOR, int(color_pos))

        # Add in the brightness at the last moment
        self.model.set_eye_dmx(s, EYE_DMX_DIMMER, int(math.floor(255 * dimmer * self._brightness)))

        #print "pan=%d dPan = %d  dTilt = %d" % (pan, dPan, dTilt)
        if effect is None:
            # Clear all effect settings
            eye_effect.clear_all(self)
        else:
            effect.go(self, speed=ext_speed)


    def set_xy_pos(self, x, y, sky):
        """
        Set the XY position of the light on the ground. The left eyet
        is at 0,0. Negative X is to the left and negative Y is towards
        the tail. The height of the lights is 1 unit. (i.e. if the lights
        are 20ft. in the air, then 1,0 is 20 feet along the ground from
        a point directly under the left eye)
        """

        self.last_x_pos = x
        self.last_y_pos = y

        if self.side == "b":
            # Adjust for parallax
            x -= 0.25

        pan_rads = math.atan2(x,1)
        tilt_rads = math.atan2( y * math.sin(math.fabs(pan_rads)), x)
        self._pan = math.degrees(pan_rads)
        self._tilt = math.degrees(tilt_rads) - 90
        if self._tilt < 0:
            self._tilt += 360.0
        if self._tilt > 180:
            self._tilt = 360-self._tilt

        if self._tilt > 135:
            self._tilt = 135

        if self.skyPos:
            self._pan = 360-self._pan

    def set_eye_dmx(self, channel, value):
        # if self.side == "p" and value != 0 and value != 255:
        #     print "dmx ch=%d  val=%d" % (channel, int(value))
        self.model.set_eye_dmx(self.side == "p", channel, int(value))


class MutableEye(Eye):

    def __init__(self, parent):
        Eye.__init__(self, parent.model, parent.side)
        self.muted = False
        self.parent = parent

    def __repr__(self):
        return "Mutable Eye side=%s" % self.side

    def go(self):
        if self.muted:
            return

        self.parent.pan = self._pan
        self.parent.tilt = self._tilt
        self.parent.color_pos = self.color_pos
        self.parent.dimmer = self.dimmer

        self.parent.go()



def xy_to_pnt(xy_pos, is_party, is_sky):
    """
    Takes an XY position on a standard plane and converts that to a pan and tilt
    position. This has to be done seperately for each eye, but the results will
    compensate for the parallax between the eye positions.

    The reference plane can be on the ground or in the sky.
    """

    x = float(xy_pos[0])
    y = float(xy_pos[1])

    # x=0.5

    # First we position the point, given in global coords, to a coordinate system
    # rooted on the eye itself.
    if is_party:
        x += config.get("parallax_distance")
        rot = math.radians(config.get("eye_rotation")["p"])
    else:
        x -= config.get("parallax_distance")
        rot = math.radians(config.get("eye_rotation")["b"])

    # Now we rotate that eye coordinate system
    c = math.cos(rot)
    s = math.sin(rot)

    # print "c=%f  s=%f" % (c,s)
    print "xy before  = %f, %f" % (x,y)
    x = x * c + y * s
    y = y * c - x * s 
    print "xy rotated = %f, %f" % (x,y)

    # x and y are now in a coordinate system rooted on the eye in the proper
    # direction. Thus all we have to do is convert to spherical coordinates (which
    # are effectivley pan and tilt), doing some appropriate skulldiggery along
    # the way for sky or not

    # http://mathworld.wolfram.com/SphericalCoordinates.html
    # Note that what we've been calling xy is xz in the reference of the eye

    r = math.sqrt(x*x + 1.0 + y*y)

    pan_rads = math.atan2(1, x)
    tilt_rads = math.acos(y / r)

    # pan_rads = math.atan2(x,1)
    # print "pan_rads=%f  sin(fabs(pr))=%f" % (pan_rads, math.sin(math.fabs(pan_rads)))

    # tilt_rads = math.atan2( y * math.sin(math.fabs(pan_rads)), x)    

    pan = 90 - math.degrees(pan_rads)
    tilt = math.degrees(tilt_rads)
    print "raw pan=%f tilt=%f" % (pan, tilt)
    if tilt < 0:
        tilt += 360.0
    if tilt > 180:
        tilt = 360-tilt

    # Because we know this is for eyes, we cap our tilt value
    if tilt > 135:
        tilt = 135.0

    # You want it in the sky you say?, well then we just swing the pan around
    if is_sky:
        pan = 360-pan

    print "final pan=%f tilt=%f" % (pan, tilt)
    return [pan, tilt]
