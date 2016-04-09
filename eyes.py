import math
import time

import eye_effect
import controls_model as controls
from color import clamp
import config

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

EYE_RESET_NONE  = "none"
EYE_RESET_ON    = "on"
EYE_RESET_OFF   = "off"
EYE_RESET_RESET = "reset"

HEADLIGHT_FROST = eye_effect.EyeEffect(frost=eye_effect.FROST_STEADY, frost_speed=0.8)

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

        self._reset_mode = EYE_RESET_NONE
        self._reset_changed_at = time.time()


    def __repr__(self):
        return "Eye side=%s" % self.side

    @property
    def tilt(self):
        return self._tilt

    @tilt.setter
    def tilt(self, val):
        if val is None:
            return
        self._tilt = clamp(float(val), -135.0, 135.0)

    @property
    def pan(self):
        return self._pan

    @pan.setter
    def pan(self, val):
        if val is None:
            return
        self._pan = clamp(float(val), -270.0, 270.0)

    @property
    def pos(self):
        return [self._pan, self,_tilt]

    @pos.setter
    def pos(self, val):
        if len(val) < 2:
            return

        self.pan = val[0]
        self.tilt = val[1]


    @property
    def reset_mode(self):
        return self._reset_mode

    @reset_mode.setter
    def reset_mode(self, val):
        if val == self._reset_mode:
            return

        if val != EYE_RESET_NONE and val != EYE_RESET_ON and val != EYE_RESET_OFF and val != EYE_RESET_RESET:
            print "Unknown eye reset mode %s" % val
            return

        self._reset_mode = val
        self._reset_changed_at = time.time()

    @property
    def reset_changed_at(self):
        return self._reset_changed_at

    def set_brightness(self, val):
        self._brightness = val

    def clear(self):
        self._pan = 0.0
        self._title = 0.0
        self.color_pos = 0
        self.dimmer = 1.0
        self.effect = None

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
            # The effect _might_ override focus, but usually it won't
            v = int(math.floor(self.cm.focus * 255.0))            
            self.model.set_eye_dmx(s, EYE_DMX_FOCUS, v)


            if self.cm.eyes_mode == controls.EYES_MODE_HEADLIGHTS:
                color_pos = 0
                dimmer = 1.0
                effect = HEADLIGHT_FROST

                if s:
                    pan = float(self.cm.p_eye_pos[controls.PAN])
                    tilt = float(self.cm.p_eye_pos[controls.TILT])
                    if self.cm.headlights_mode == controls.HEADLIGHTS_MODE_LEFT or self.cm.headlights_mode == controls.HEADLIGHTS_MODE_BOTH:
                        effect = None
                else:
                    pan = float(self.cm.b_eye_pos[controls.PAN])
                    tilt = float(self.cm.b_eye_pos[controls.TILT])

                    if self.cm.headlights_mode == controls.HEADLIGHTS_MODE_RIGHT or self.cm.headlights_mode == controls.HEADLIGHTS_MODE_BOTH:
                        effect = None


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

        self.model.set_eye_dmx(s, EYE_DMX_PNT_SPEED, 254)

        # The reset mode
        if self._reset_mode == EYE_RESET_NONE:
            self.model.set_eye_dmx(s, EYE_DMX_LAMP, 0)
        elif self._reset_mode == EYE_RESET_ON:
            self.model.set_eye_dmx(s, EYE_DMX_LAMP, 40)
        elif self._reset_mode == EYE_RESET_OFF:
            self.model.set_eye_dmx(s, EYE_DMX_LAMP, 60)
        elif self._reset_mode == EYE_RESET_RESET:
            self.model.set_eye_dmx(s, EYE_DMX_LAMP, 80)


    def set_xy_pos(self, xy_pos, sky):
        """
        Set the XY position of the light on the ground. The left eyet
        is at 0,0. Negative X is to the left and negative Y is towards
        the tail. The height of the lights is 1 unit. (i.e. if the lights
        are 20ft. in the air, then 1,0 is 20 feet along the ground from
        a point directly under the left eye)
        """

        pos = xy_to_pnt(xy_pos, self.side == "p", sky)
        self.pan = pos[0]
        self.tilt = pos[1]

        # if self.side == "b":
        #     # Adjust for parallax
        #     x -= 0.25

        # pan_rads = math.atan2(x,1)
        # tilt_rads = math.atan2( y * math.sin(math.fabs(pan_rads)), x)
        # self._pan = math.degrees(pan_rads)
        # self._tilt = math.degrees(tilt_rads) - 90
        # if self._tilt < 0:
        #     self._tilt += 360.0
        # if self._tilt > 180:
        #     self._tilt = 360-self._tilt

        # if self._tilt > 135:
        #     self._tilt = 135

        # if self.skyPos:
        #     self._pan = 360-self._pan

    def set_xyz_pos(self, xyz_pos, cap_pan=True):
            pos = xyz_to_pnt(xyz_pos, self.side == "p", cap_pan)
            self.pan = pos[0]
            self.tilt = pos[1]


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

        self.parent.effect = self.effect

        self.parent.go()


def xy_to_pnt(xy_pos, is_party, is_sky=False):
    """
    Takes an XY position on a standard plane and converts that to a pan and tilt
    position. This has to be done seperately for each eye, but the results will
    compensate for the parallax between the eye positions.

    The reference plane can be on the ground or in the sky.
    """
    xyz_pos = [xy_pos[0], xy_pos[1], 1.0]
    if is_sky:
        xyz_pos[2] = -1.0

    return xyz_to_pnt(xyz_pos, is_party)

def xyz_to_pnt(xyz_pos, is_party, cap_pan=True):
    """
    The more better uber function which takes a fully 3 dimensional position
    in cartesian coordinates and returns a pan and tilt aim set for one eye
    or the other which will hit that position, compensated for parallax
    between the eyes as well as the offset angle for each of them.

    The origin of the xyz system is at a point level with, and equidistant
    between, the center of rotation of the two eyes. An assumption is made
    that the eyes are reasonably level with each other and that the line
    between them is reasonably square with the centerline of the bus. If
    that doesn't hold, we will have to upgrade to full position and direction
    vector specifications for each eye, which isn't the end of the world, it's
    just going to be more work...

    Units for the coordinate system are "height of the eyes". So a position
    of 1 on the Z axis is the ground, a position of 0 is dead ahead, and
    a position of -1 is above the bus by the same distance as to the ground.
    """

    x0 = float(xyz_pos[0])
    y0 = float(xyz_pos[1])
    z0 = float(xyz_pos[2])

    # x0 = 0.125

    side = "b"
    if is_party:
        side = "p"

    # First we position the point, given in global coords, to a coordinate system
    # rooted on the eye itself.
    if is_party:
        x0 += config.get("parallax_distance")
        rot = math.radians(config.get("eye_rotation")["p"])
    else:
        x0 -= config.get("parallax_distance")
        rot = math.radians(config.get("eye_rotation")["b"])

    # Now we rotate that eye coordinate system
    c = math.cos(rot)
    s = math.sin(rot)

    # print "c=%f  s=%f" % (c,s)
    #print "xyz0 before  = %f, %f, %f" % (x0,y0, z0)
    x = (x0 * c) + (y0 * s)
    y = (y0 * c) - (x0 * s)

    # c = math.cos(-rot)
    # s = math.sin(-rot)
    # x3 = (x * c) + (y * s)
    # y3 = (y * c) - (x * s)
    # print "xy rotated = %f, %f   unrotated= %f, %f " % (x,y, x3,y3)

    # x and y are now in a coordinate system rooted on the eye in the proper
    # direction. Thus all we have to do is convert to spherical coordinates (which
    # are effectivley pan and tilt), doing some appropriate skulldiggery along
    # the way for sky or not

    # http://mathworld.wolfram.com/SphericalCoordinates.html
    # Note that what we've been calling xy is xz in the reference of the eye

    r = math.sqrt(x*x + z0*z0 + y*y)

    pan_rads = math.atan2(z0, x)
    tilt_rads = math.acos(y / r)

    # pan_rads = math.atan2(x,1)
    # print "pan_rads=%f  sin(fabs(pr))=%f" % (pan_rads, math.sin(math.fabs(pan_rads)))

    # tilt_rads = math.atan2( y * math.sin(math.fabs(pan_rads)), x)    

    pan = 90 - math.degrees(pan_rads)
    tilt = math.degrees(tilt_rads)
    #print "%s pan=%f tilt=%f" % (side, pan, tilt)

    # Keep pan away from lock by only using the lower half
    # and just reversing tilt. This should be a tad safer, but
    # more important should mean a faster transition to the same end point
    if cap_pan:
        if pan < -90:
            #print "%s swap < -90" % side
            pan += 180
            tilt = -tilt
        elif pan > 90:
            #print "%s swap > 90" % side
            pan -= 180
            tilt = -tilt

    #if tilt > 135 or tilt < -135:
        #print "%s TILT MAX" % side

    # if tilt < 0:
    #     tilt += 360.0
    # if tilt > 180:
    #     tilt = 360-tilt

    # Because we know this is for eyes, we cap our tilt value
    # tilt = color.clamp(tilt,-135.0)
    # if tilt > 135:
    #     tilt = 135.0

    # # You want it in the sky you say?, well then we just swing the pan around
    # if is_sky:
    #     pan = 360-pan



    # # As a check, let's map from these polar coordinates back to cartesian
    # # coordinates, which we will then unrotate and stuff
    # x2 = r * math.cos(pan_rads) * math.sin(tilt_rads)
    # z2 = r * math.sin(pan_rads) * math.sin(tilt_rads)
    # y2 = r * math.cos(tilt_rads)

    # c = math.cos(-rot)
    # s = math.sin(-rot)
    # x3 = x2 * c + y2 * s
    # y3 = y2 * c - x2 * s

    # print "2=(%f,%f,%f)  3=(%f,%f)" % (x2,y2,z2, x3,y3)



    #print "%s final pan=%f tilt=%f" % (side, pan, tilt)
    return [pan, tilt]
