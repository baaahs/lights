import sys
import color
import math
import time

import json

import traceback

import eyes
import eye_effect
import config



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
    eyes.EYE_COLOR_WHITE,
    eyes.EYE_COLOR_RED,
    eyes.EYE_COLOR_ORANGE,
    eyes.EYE_COLOR_YELLOW,
    eyes.EYE_COLOR_DEEP_GREEN,
    eyes.EYE_COLOR_BLUE,
    eyes.EYE_COLOR_MAGENTA,
    eyes.EYE_COLOR_WHITE
]

EYES_MODE_DISCO = "disco"
EYES_MODE_HEADLIGHTS = "headlights"
EYES_MODE_SHOW = "show"

HEADLIGHTS_MODE_NORMAL = "normal"
HEADLIGHTS_MODE_LEFT = "left"
HEADLIGHTS_MODE_BOTH = "both"
HEADLIGHTS_MODE_RIGHT = "right"

SHOW_TARGET_MODE_NONE = "none"
SHOW_TARGET_MODE_PNT = "pnt"
SHOW_TARGET_MODE_UP = "up"
SHOW_TARGET_MODE_DOWN = "down"
SHOW_TARGET_MODE_FRONT = "front"

PAN = 0
TILT = 1

class ControlsModel(object):
    """
    Holds the state of the user interface for the overall show server. This
    is useful both for re-establishing state in clients that come and go, like
    the TouchOSC client, but also as THE place that shows come to in order
    to understand how they should modify their behavior.

    From the show side, there are a lot of un-encapsulated properties/attributes
    of a ControlsModel instance that can be read. Some key ones are:

        chosen_colors[]
        speed_multi
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
        self.p_eye_pos  = [0,0]
        self.b_eye_pos = [0,0]

        # Range 0.0 to 1.0
        self.p_brightness = 1.0
        self.b_brightness = 1.0

        # self.eye_positions = {}
        # self.eye_positions["disco"] = [[-75, 115], [0,0]]  # Really only the left is used
        # self.eye_positions["headlights"] = [[0,5], [0,5]]  # Probably want this slightly down

        self.eye_movement_locked = False

        self._last_eye_touched_was_party = True

        self.p_eye_xy_enable = True
        self.b_eye_xy_enable = True
        self.eye_sky_pos = False # If true, XY position is in sky, otherwise on ground
        # self.lastYPos = 0.0
        # self.lastXPos = 0.0

        # # The color pos values range from 0 to 127 and refer to
        # # a position of the color wheel. Each color occupies an 8
        # # value range with the "full" position of that color being
        # # in the center of the range. The edge of the ranges are positions
        # # where both colors are visible in the output at one time.
        # self.pColorPos = 0
        # self.bColorPos = 0

        # self.pColorEnable = True
        # self.bColorEnable = True
        # self.colorMix = False
        # self.colorCycleSpeed = 0

        ########
        self.disco_mix = False
        self.disco_cycle_speed = 0.0
        self.disco_color_pos = eyes.EYE_COLOR_WHITE
        self.disco_brightness = 1.0
        self.disco_effect = 0
        self.disco_effect_speed = 0.0
        ###

        ########
        self.headlights_target = [0.0, 0.0]
        self.headlights_mode = HEADLIGHTS_MODE_NORMAL

        ###

        ########        
        self.show_target = [0.0, 0.0]
        self.show_target_mode = SHOW_TARGET_MODE_NONE
        ###

        self.focus = 0.5

        # The RGB values of the chosen colors
        self.chosen_colors = [ color.RGB(255, 255, 0), color.RGB(0,255,255) ]
        # Color wheel positions
        self.chosen_colors_pos = [ eyes.EYE_COLOR_WHITE, eyes.EYE_COLOR_WHITE ]

        # Chosen indexes. Could be -1
        self.chosen_colors_ix = [7, 7]


        # Color presets. Mapped to 100+ix for choices above
        self.color_presets = [ 
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
        self.color_presets_to_pos = []
        for ix in range(0, len(self.color_presets)):
            self.color_presets_to_pos.append(self.color_presets[ix].pos)


        ## Speed setting. This is multiplied against the "rate", so that
        # means if you're calculating delays, 2.0 here should result in 
        # calculating a delay half as long. This will be done automatically
        # by the show runner if you are yielding something more than about 0.001,
        # but if you are doing proper time based "as fast as we can" calculations
        # yourself, you will need to respect this value.
        self.speed_multi = 1.0

        # A value that ranges from -1.0 (maximum calm) to 1.0 (maximum intensity).
        # It should be interpretted by each show in a show appropriate manner
        self.intensified = 0.0

        # A value that ranges from -1.0 (totally monochrome) to 1.0 (max color).
        # If the currently running show does not set handles_colorized to True this
        # will be handled by the system, otherwise it is left to the show to modify
        # it's colors appropriately
        self.colorized = 0.0

        # These are modifiers that a show can interpret as it wishes.
        # The first step is a set of binary on/off ones. Only the first 5
        # are exposed on the iPhone UI.
        self.modifiers = [False,False,False,False,False,False,False]
        # The second set is incremented each time a user taps the corresponding
        # button. They can be reset to 0 by an app using reset_steps()
        self.step_modifiers = [0,0,0,0]

        self.listeners = set()

        self._tap_times = []

        # Start with a muddy yellow because starting with black goes badly/is silly
        self.color = color.RGB(255,255,0)

        self.set_eyes_mode(EYES_MODE_SHOW)

        # A message that is shown in the UI
        self.message = ""


        self.master_names = []
        self.eo_names = []
        self.overlay_names = []

        self.master_name = ""
        self.eo_name = ""

        self.time_limits = [30, 20 * 60]
        self.max_time = 42.0

        self.brightness = 0.5

        self.set_default_effects()
        self.load_effects()



    def add_listener(self, listener):
        self.listeners.add(listener)

    def del_listener(self, listener):
        self.listeners.discard(listener)

    def incoming_osc(self, addr, tags, data, source):
        # print "incoming_osc %s: %s [%s] %s" % (source, addr, tags, str(data))

        parts = addr.split("/")
        # print parts

        if parts[1] == "main":
            if parts[2] == "color":
                if parts[4] == "rgb":
                    self.set_color_rgb(int(parts[3]), data)
                else:
                    self.set_color_ix(int(parts[3]), int(parts[4]))

            elif parts[2] == "speed":
                if parts[3] == "reset":
                    self.speed_reset()
                elif parts[3] == "changeRel":
                    self.speed_change_rel(data[0])
                elif parts[3] == "tap":
                    if int(data[0]) == 1:
                        self.speed_tap()


            elif parts[2] == "intensified":
                self.set_intensified(data[0])
            elif parts[2] == "colorized":
                self.set_colorized(data[0])
            elif parts[2] == "modifier":
                self.toggle_modifier(int(parts[3]))

            elif parts[2] == "stepModifier":
                if data[0] == 1.0:
                    self.increment_step_modifier(int(parts[3]))

            elif parts[2] == "brightness":
                self.set_brightness(data[0])

        elif parts[1] == "color":
            if parts[2] == "red":
                self.set_color_r(data[0])
            elif parts[2] == "green":
                self.set_color_g(data[0])
            elif parts[2] == "blue":
                self.set_color_b(data[0])
            elif parts[2] == "hue":
                self.set_color_h(data[0])
            elif parts[2] == "sat":
                self.set_color_s(data[0])
            elif parts[2] == "val":
                self.set_color_v(data[0])

        elif parts[1] == "shows":
            if parts[2] == "master":

                # Button presses
                if parts[3] == "maxTime":
                    self.set_max_time_scaled(data[0])
                elif data[0] >= 1.0:
                    if parts[3] == "up":
                        self.show_runner.move_master_cursor(-1 * int(data[0]))
                    elif parts[3] == "down":
                        self.show_runner.move_master_cursor(1 * int(data[0]))
                    elif parts[3] == "random":
                        self.show_runner.select_master_random()
                    elif parts[3] == "choice":
                        self.show_runner.select_master(int(parts[4]))

            elif parts[2] == "eo":

                # Button presses
                if data[0] >= 1.0:
                    if parts[3] == "up":
                        self.show_runner.move_eo_cursor(-1 * int(data[0]))
                    elif parts[3] == "down":
                        self.show_runner.move_eo_cursor(1 * int(data[0]))
                    elif parts[3] == "off":
                        self.show_runner.eo_off()
                    elif parts[3] == "choice":
                        self.show_runner.select_eo(int(parts[4]))

            elif parts[2] == "overlay":

                # Button presses
                if data[0] >= 1.0:
                    if parts[3] == "up":
                        self.show_runner.move_overlay_cursor(-1 * int(data[0]))
                    elif parts[3] == "down":
                        self.show_runner.move_overlay_cursor(1 * int(data[0]))
                    elif parts[3] == "choice":
                        self.show_runner.start_overlay(int(parts[4]))
                elif parts[3] == "choice":
                    self.show_runner.stop_overlay(int(parts[4]))


        elif parts[1] == "eyes":

            # if parts[2] == "pPan":
            #     self.set_eye_pan(True, data[0])
            # elif parts[2] == "bPan":
            #     self.set_eye_pan(False, data[0])
            # elif parts[2] == "pTilt":
            #     self.set_eye_tilt(True, data[0])
            # elif parts[2] == "bTilt":
            #     self.set_eye_tilt(False, data[0])
            # elif parts[2] == "movementLock":
            #     self.set_eye_movement_lock(data[0] == 1.0)

            # elif parts[2] == "xyPos":
            #     self.setEyeXYPos(data[0], data[1])
            # elif parts[2] == "xPos":
            #     self.setEyeXYPos(data[0],self.lastYPos)
            # elif parts[2] == "yPos":
            #     self.setEyeXYPos(self.lastXPos,data[0])

            # elif parts[2] == "pXYEnable":
            #     self.toggleEyeXYEnable(True)
            # elif parts[2] == "bXYEnable":
            #     self.toggleEyeXYEnable(False)
            # elif parts[2] == "skyPos":
            #     self.toggleEyeSkyPos()

            # elif parts[2] == "dimmer":
            #     self.setDimmer(parts[3]=="1", data[0])

            # elif parts[2] == "pColorEnable":
            #     self.toggleEyeColorEnabled(True)
            # elif parts[2] == "bColorEnable":
            #     self.toggleEyeColorEnabled(False)
            # elif parts[2] == "colorMix":
            #     self.toggleEyeColorMix()
            # elif parts[2] == "colorCycle":
            #     self.toggleEyeColorCycle(data[0])

            # The colors, all the colors
            # These are pushbuttons, so we will get a 1.0 and a 0.0 event. Thus
            # we only bother setting it on the 1.0 event, although technically it
            # wouldn't hurt to set it twice. It would just be wasteful.
            # elif parts[2] == "colorWhite":
            #     if data[0] == 1.0:
            #         self.setEyeColor(EYE_COLOR_WHITE)
            # elif parts[2] == "colorRed":
            #     if data[0] == 1.0:
            #         self.setEyeColor(EYE_COLOR_RED)
            # elif parts[2] == "colorOrange":
            #     if data[0] == 1.0:
            #         self.setEyeColor(EYE_COLOR_ORANGE)
            # elif parts[2] == "colorAquamarine":
            #     if data[0] == 1.0:
            #         self.setEyeColor(EYE_COLOR_AQUAMARINE)
            # elif parts[2] == "colorDeepGreen":
            #     if data[0] == 1.0:
            #         self.setEyeColor(EYE_COLOR_DEEP_GREEN)
            # elif parts[2] == "colorLightGreen":
            #     if data[0] == 1.0:
            #         self.setEyeColor(EYE_COLOR_LIGHT_GREEN)
            # elif parts[2] == "colorLavender":
            #     if data[0] == 1.0:
            #         self.setEyeColor(EYE_COLOR_LAVENDER)
            # elif parts[2] == "colorPink":
            #     if data[0] == 1.0:
            #         self.setEyeColor(EYE_COLOR_PINK)
            # elif parts[2] == "colorYellow":
            #     if data[0] == 1.0:
            #         self.setEyeColor(EYE_COLOR_YELLOW)
            # elif parts[2] == "colorMagenta":
            #     if data[0] == 1.0:
            #         self.setEyeColor(EYE_COLOR_MAGENTA)
            # elif parts[2] == "colorCyan":
            #     if data[0] == 1.0:
            #         self.setEyeColor(EYE_COLOR_CYAN)
            # elif parts[2] == "colorCTO2":
            #     if data[0] == 1.0:
            #         self.setEyeColor(EYE_COLOR_CTO2)
            # elif parts[2] == "colorCTO1":
            #     if data[0] == 1.0:
            #         self.setEyeColor(EYE_COLOR_CTO1)
            # elif parts[2] == "colorCTB":
            #     if data[0] == 1.0:
            #         self.setEyeColor(EYE_COLOR_CTB)
            # elif parts[2] == "colorBlue":
            #     if data[0] == 1.0:
            #         self.setEyeColor(EYE_COLOR_BLUE)

            if parts[2] == "mode":                
                if data[0] == 1.0:
                    self.set_eyes_mode(parts[3])
                elif data[0] == 0.0:
                    # They turned off the mode, which we don't care for,
                    # so do a full refresh
                    self._notify_eyes_mode_changed()

            elif parts[2] == "disco":
                if parts[3] == "mix":
                    self.set_disco_mix(data[0])
                elif parts[3] == "cycleSpeed":
                    self.set_disco_cycle_speed(data[0])
                elif parts[3] == "brightness":
                    self.set_disco_brightness(data[0])

                elif parts[3] == "noEffect":
                    self.set_disco_no_effect()
                elif parts[3] == "effectSpeed":
                    self.set_disco_effect_speed(data[0])
                elif parts[3] == "effect":
                    if data[0] == 1.0:
                        self.set_disco_effect(int(parts[4]), int(parts[5]))
                    else:
                        self.maybe_unset_disco_effect(int(parts[4]), int(parts[5]))

                elif data[0] == 1.0:

                    if parts[3] == "colorWhite":
                        self.set_disco_color_pos(eyes.EYE_COLOR_WHITE)
                    elif parts[3] == "colorRed":
                        self.set_disco_color_pos(eyes.EYE_COLOR_RED)
                    elif parts[3] == "colorOrange":
                        self.set_disco_color_pos(eyes.EYE_COLOR_ORANGE)
                    elif parts[3] == "colorAquamarine":
                        self.set_disco_color_pos(eyes.EYE_COLOR_AQUAMARINE)
                    elif parts[3] == "colorDeepGreen":
                        self.set_disco_color_pos(eyes.EYE_COLOR_DEEP_GREEN)
                    elif parts[3] == "colorLightGreen":
                        self.set_disco_color_pos(eyes.EYE_COLOR_LIGHT_GREEN)
                    elif parts[3] == "colorLavender":
                        self.set_disco_color_pos(eyes.EYE_COLOR_LAVENDER)
                    elif parts[3] == "colorPink":
                        self.set_disco_color_pos(eyes.EYE_COLOR_PINK)
                    elif parts[3] == "colorYellow":
                        self.set_disco_color_pos(eyes.EYE_COLOR_YELLOW)
                    elif parts[3] == "colorMagenta":
                        self.set_disco_color_pos(eyes.EYE_COLOR_MAGENTA)
                    elif parts[3] == "colorCyan":
                        self.set_disco_color_pos(eyes.EYE_COLOR_CYAN)
                    elif parts[3] == "colorCTO2":
                        self.set_disco_color_pos(eyes.EYE_COLOR_CTO2)
                    elif parts[3] == "colorCTO1":
                        self.set_disco_color_pos(eyes.EYE_COLOR_CTO1)
                    elif parts[3] == "colorCTB":
                        self.set_disco_color_pos(eyes.EYE_COLOR_CTB)
                    elif parts[3] == "colorBlue":
                        self.set_disco_color_pos(eyes.EYE_COLOR_BLUE)                

            elif parts[2] == "hmode":
                self.set_headlights_mode(parts[3])

            elif parts[2] == "target":
                if parts[3] == "xy":
                    self.set_eyes_target(data[0], data[1])
                elif parts[3] == "focus":
                    self.set_eyes_focus(data[0])
                else:
                    self.set_show_target_mode(parts[3])



        elif parts[1] == "global":
            if parts[2] == "refresh":
                if data[0] == 1.0:
                    self._notify_refresh()

        # Separate from global because this one gets hidden on a refresh
        # whereas the global one doesn't
        elif parts[1] == "onetime":
            if parts[2] == "refresh":
                if data[0] == 1.0:
                    self._notify_refresh()



    def set_color_r(self, r):
        # Convert from float to byte
        n = round(255 * r)
        if n == self.color.r:
            return

        self.color.r = n
        self._notify_color()

    def set_color_g(self, v):
        # Convert from float to byte
        n = round(255 * v)
        if n == self.color.g:
            return

        self.color.g = n
        self._notify_color()

    def set_color_b(self, v):
        # Convert from float to byte
        n = round(255 * v)
        if n == self.color.b:
            return

        self.color.b = n
        self._notify_color()

    def set_color_h(self, v):
        if v == self.color.h:
            return

        self.color.h = v
        self._notify_color()

    def set_color_s(self, v):
        if v == self.color.s:
            return

        self.color.s = v
        self._notify_color()

    def set_color_v(self, v):
        if v == self.color.v:
            return

        self.color.v = v
        self._notify_color()

    def _notify_color(self):
        print "_notify_color"
        for listener in self.listeners:
            if listener.control_color_changed:
                listener.control_color_changed()
    
    # def set_eye_movement_lock(self, locked):
    #     print "set_eye_movement_lock %s" % str(locked)
    #     # if locked == self.eye_movement_locked:
    #     #     return

    #     self.eye_movement_locked = locked
    #     if self.eye_movement_locked:
    #         if self._last_eye_touched_was_party:
    #             # Make the business eye match the party eye
    #             self.bEyeTilt = self.pEyeTilt
    #             self.bEyePan = self.pEyePan
    #             self._notify_eye_changed(False)
    #         else:
    #             # Make the party eye follow the business eye
    #             self.pEyeTilt = self.bEyeTilt
    #             self.pEyePan = self.bEyePan
    #             self._notify_eye_changed(True)

    #     self._notifyEyeMovementLockChanged()

    # def set_eye_tilt(self, isParty, tiltValue):
    #     tiltValue = math.floor(tiltValue)
    #     if tiltValue < -135:
    #         tiltValue = -135
    #     if tiltValue > 135:
    #         tiltValue = 135

    #     self._last_eye_touched_was_party = isParty

    #     if self.pEyeTilt != tiltValue and (isParty or self.eye_movement_locked):
    #         self.pEyeTilt = tiltValue
    #         self.p_eye_xy_enable = False
    #         self._notify_eye_changed(True)

    #     if self.bEyeTilt != tiltValue and (not isParty or self.eye_movement_locked):
    #         self.bEyeTilt = tiltValue
    #         self.b_eye_xy_enable = False
    #         self._notify_eye_changed(False)

    # def set_eye_pan(self, isParty, panValue):
    #     panValue = math.floor(panValue)
    #     if panValue < -270:
    #         panValue = -270
    #     if panValue > 270:
    #         panValue = 270

    #     self._last_eye_touched_was_party = isParty

    #     if self.pEyePan != panValue and (isParty or self.eye_movement_locked):
    #         self.pEyePan = panValue
    #         self.p_eye_xy_enable = False
    #         self._notify_eye_changed(True)

    #     if self.bEyePan != panValue and (not isParty or self.eye_movement_locked):
    #         self.bEyePan = panValue
    #         self.b_eye_xy_enable = False
    #         self._notify_eye_changed(False)

    # def setDimmer(self, isParty, dimVal):
    #     "Sets dimmer for one eye to dimVal. Range of 0.0 to 1.0"
    #     if dimVal < 0:
    #         dimVal = 0
    #     elif dimVal > 1.0:
    #         dimVal = 1.0

    #     if self.p_brightness != dimVal and (isParty or self.eye_movement_locked):
    #         self.p_brightness = dimVal
    #         self._notify_eye_changed(True)

    #     if self.b_brightness != dimVal and (not isParty or self.eye_movement_locked):
    #         self.b_brightness = dimVal
    #         self._notify_eye_changed(False)

    def _set_eye_xy_flat_pos(self, x, y, do_party, do_business, in_sky):
        #
        # Basic formula is pan = atan(x), tilt = atan( (y * sin(pan)) / x )
        #

        # if y < -0.5:
        #     y = -0.5

        # self.lastXPos = x
        # self.lastYPos = y

        #y = .125

        # Units for X and Y real are "height of the eye" = 1. Scaling out so
        # that we can tweak it more here than in touch and can define a reasonable
        # addressable area
        xr = config.get("xy_scale")["x"] * x
        yr = config.get("xy_scale")["y"] * (y + 0.5)

        if do_party:
            self.p_eye_pos = eyes.xy_to_pnt([xr, yr], True, in_sky)

            # pan_rads = math.atan2(xr,1)
            # tilt_rads = math.atan2( yr * math.sin(math.fabs(pan_rads)), xr)
            # self.p_eye_pos[PAN] = math.degrees(pan_rads)
            # self.p_eye_pos[TILT] = math.degrees(tilt_rads) - 90
            # if self.p_eye_pos[TILT]  < 0:
            #     self.p_eye_pos[TILT]  += 360
            # if self.p_eye_pos[TILT]  > 180:
            #     self.p_eye_pos[TILT]  = 360-self.p_eye_pos[TILT] 

            # print "P x=%f y=%f pan=%f tilt=%f" % (xr,yr, self.p_eye_pos[PAN] , self.p_eye_pos[TILT] )
            # if self.p_eye_pos[TILT]  > 135:
            #     self.p_eye_pos[TILT]  = 135

            # if in_sky:
            #     self.p_eye_pos[PAN]  = 360-self.p_eye_pos[PAN] 

            self._notify_eye_changed(True)

        if do_business:
            # xr -= 0.25 # This is (roughly) the distance between the lights in light_to_ground units
            # pan_rads = math.atan2(xr,1)
            # tilt_rads = math.atan2( yr * math.sin(math.fabs(pan_rads)), xr)
            # self.b_eye_pos[PAN] = math.degrees(pan_rads)
            # self.b_eye_pos[TILT] = math.degrees(tilt_rads) - 90
            # if self.b_eye_pos[TILT] < 0:
            #     self.b_eye_pos[TILT] += 360
            # if self.b_eye_pos[TILT] > 180:
            #     self.b_eye_pos[TILT] = 360-self.b_eye_pos[TILT]

            # print "B x=%f y=%f pan=%f tilt=%f" % (xr,yr, self.b_eye_pos[PAN], self.b_eye_pos[TILT])
            # if self.b_eye_pos[TILT] > 135:
            #     self.b_eye_pos[TILT] = 135

            # if in_sky:
            #     self.b_eye_pos[PAN] = 360-self.b_eye_pos[PAN]

            self.b_eye_pos = eyes.xy_to_pnt([xr, yr], False, in_sky)
            self._notify_eye_changed(False)



    # def toggleEyeXYEnable(self, isParty):
    #     if isParty:
    #         self.p_eye_xy_enable = not self.p_eye_xy_enable
    #     else:
    #         self.b_eye_xy_enable = not self.b_eye_xy_enable

    #     self._notify_eye_changed(isParty)

    # def toggleEyeSkyPos(self):
    #     self.eye_sky_pos = not self.eye_sky_pos
    #     self.setEyeXYPos(self.lastXPos, self.lastYPos)

    #     # Do a fake one here just in case it didn't happen already
    #     if not self.p_eye_xy_enable and not self.b_eye_xy_enable:
    #         self._notify_eye_changed(True)



    def _notify_eye_changed(self, isParty):
        print "_notify_eye_changed isParty=%s" % isParty
        for listener in self.listeners:
            try:
                listener.control_eye_changed(isParty)
            except AttributeError:
                pass # whatever...

    # def _notifyEyeMovementLockChanged(self):
    #     for listener in self.listeners:
    #         try:
    #             listener.control_eyeMovementLockChanged()
    #         except AttributeError:
    #             pass # whatever...



    # def setEyeColor(self, val):
    #     val = math.floor(val)
    #     if self.colorMix:
    #         val += 4

    #     if self.pColorEnable:
    #         self.pColorPos = val
    #     if self.bColorEnable:
    #         self.bColorPos = val

    #     self.colorCycleSpeed = 0

    #     self._notifyEyeColorChanged()

    # def toggleEyeColorEnabled(self, isParty):
    #     if isParty:
    #         self.pColorEnable = not self.pColorEnable
    #     else:
    #         self.bColorEnable = not self.bColorEnable

    #     # While this isn't strictly true, it will cause the toggle state
    #     # of the UI button to change, which we want
    #     self._notifyEyeColorChanged()

    # def toggleEyeColorMix(self):
    #     self.colorMix = not self.colorMix
    #     self._notifyEyeColorChanged()

    # def toggleEyeColorCycle(self, speed):
    #     self.colorCycleSpeed = math.floor(speed)
    #     self._notifyEyeColorChanged()

    # def _notifyEyeColorChanged(self):
    #     for listener in self.listeners:
    #         try:
    #             listener.control_eyeColorChanged()
    #         except AttributeError:
    #             pass # whatever...

    ############
    def _notify_refresh(self):
        for listener in self.listeners:
            try:
                listener.control_refresh_all()
            except AttributeError:
                pass # whatever...


    ############
    # Main interface

    def set_color_ix(self, c_ix, v_ix):
        """
        Set the color at index cIx to the value at index vIx. For vIx < 100
        this is a predefined color. For vIx > 100 it is a macro color that
        can be changed using the tech interface.
        """
        if c_ix < 0 or c_ix > 1:
            print "Don't understand color ix %d" % c_ix
            return

        self.chosen_colors_ix[c_ix] = v_ix

        if v_ix < 100:
            self.chosen_colors[c_ix] = PREDEFINED_COLORS[v_ix]
            self.chosen_colors_pos[c_ix] = PREDEFINED_COLOR_POS[v_ix]
        else:
            self.chosen_colors[c_ix] = self.color_presets[v_ix-100]
            self.chosen_colors_pos[c_ix] = self.color_presets_to_pos[v_ix-100]

        self._notify_chosen_color_changed(c_ix)

    def set_color_rgb(self, c_ix, data):
        """
        Sets the color at index c_ix to the value given by rgb data in 
        either string, int, or float data formats. Strings and ints
        are interpreted as 0-255, floats are interpreted as 0.0-1.0
        """
        if c_ix < 0 or c_ix > 1:
            print "Don't understand color ix %d" % c_ix
            return

        if len(data) < 3:
            print "Not enough data values to set rgb color: %s" % (str(data))
            return

        if isinstance(data[0], float):
            # Scale the floats to 255
            r = int(data[0] * 255)
            g = int(data[1] * 255)
            b = int(data[2] * 255)
        else:
            r = int(data[0])
            g = int(data[1])
            b = int(data[2])

        self.chosen_colors_ix[c_ix] = -1
        self.chosen_colors[c_ix] = color.RGB(r,g,b)
        self.chosen_colors_pos[c_ix] = self.chosen_colors[c_ix].pos

        self._notify_chosen_color_changed(c_ix)
   

    def _notify_chosen_color_changed(self, c_ix):
        print "_notify_chosen_color_changed"
        for listener in self.listeners:
            try:
                listener.control_chosen_color_changed(c_ix)
            except AttributeError:
                pass # ignore


    def speed_reset(self):
        self.speed_multi = 1.0

        self._notify_speed_changed()

    def speed_change_rel(self, amt):
        # Scale this value some so it's a log scale or similar?
        self.speed_multi = 1.0 + amt
        if self.speed_multi <= 0.0:
            self.speed_multi = 0.01

        self._notify_speed_changed()

    def speed_tap(self):
        now = time.time()
        if len(self._tap_times) == 0:
            # It is the first tap so record it and move on
            self._tap_times.append(now)
            print "First tap"
            return

        # There is at least one previous time.

        # How long has it been? There is a maximum amount of time between taps
        # that corresponds to some low bpm after which we start over
        elapsed = now - self._tap_times[len(self._tap_times) - 1] 

        if elapsed > 2.0:
            # OMG! So long ago! It's totally time to reset
            self._tap_times = [now]
            print "Elapsed was %f, resettting" % elapsed
            return

        # Hmm, okay, not all that old, so let's add it and then process
        # all of them if we can
        self._tap_times.append(now)

        while len(self._tap_times) > 16:
            self._tap_times.pop(0)

        # There are now 1 to 8 elements in the list
        if len(self._tap_times) < 4:
            # Not enough
            print "Only have %d taps, not enough" % len(self._tap_times)
            return

        # I'm not sure if this is the "right" way to find intervals, but it makes sense to me.
        # Rather than just average from the begining time to the end time, we convert the times
        # into intervals and then average the intervals
        int_total = 0.0
        num_ints = 0
        last = 0.0
        for ix, v in enumerate(self._tap_times):            
            if ix == 0:
                last = v
                continue
            int_total += v - last
            last = v
            num_ints += 1

        avg_interval = int_total / num_ints

        # Reference time is 120bpm, which is 0.5s between quarter notes (i.e. taps)
        print "avgInterval=%f  intTotal=%f numInts=%d" % (avg_interval, int_total, num_ints)
        self.speed_multi = 0.5 / avg_interval

        self._notify_speed_changed()





    def _notify_speed_changed(self):
        print "_notify_speed_changed"
        for listener in self.listeners:
            try:
                listener.control_speed_changed()
            except AttributeError:
                pass # ignore



    def set_intensified(self, val):
        self.intensified = val

        self._notify_intensified_changed()


    def _notify_intensified_changed(self):
        print "_notify_intensified_changed"
        for listener in self.listeners:
            try:
                listener.control_intensified_changed()
            except AttributeError:
                pass # ignore

    def set_colorized(self, val):
        self.colorized = val

        self._notify_colorized_changed()


    def _notify_colorized_changed(self):
        print "_notify_colorized_changed"
        for listener in self.listeners:
            try:
                listener.control_colorized_changed()
            except AttributeError:
                pass # ignore

    def set_brightness(self, val):
        self.brightness = val

        self._notify_brightness_changed()


    def _notify_brightness_changed(self):
        print "_notify_brightness_changed"
        for listener in self.listeners:
            try:
                listener.control_brightness_changed(self.brightness)
            except AttributeError:
                pass # ignore

    def set_modifier(self, mIx, new_val):
        mIx = color.clamp(mIx, 0, len(self.modifiers))

        if self.modifiers[mIx] == new_val:
            return

        self.modifiers[mIx] = new_val
        self._notify_modifiers_changed()

    def toggle_modifier(self, mIx):
        mIx = color.clamp(mIx, 0, len(self.modifiers))

        self.modifiers[mIx] = not self.modifiers[mIx]

        self._notify_modifiers_changed()

    def _notify_modifiers_changed(self):
        print "_notify_modifiers_changed"
        for listener in self.listeners:
            try:
                listener.control_modifiers_changed()
            except AttributeError:
                pass # ignore


    def increment_step_modifier(self, mIx):
        mIx = color.clamp(mIx, 0, len(self.step_modifiers))

        self.step_modifiers[mIx] += 1

        self._notify_step_modifiers_changed()

    def reset_step_modifiers(self, reset_to=0):
        if reset_to == 0:
            for ix in range(0, len(self.step_modifiers)):          
                self.step_modifiers[ix] = 0
        else:
            self.step_modifiers[0] = 0
            for ix in range(1, len(self.step_modifiers)):            
                self.step_modifiers[ix] = reset_to

        self._notify_step_modifiers_changed()

    def _notify_step_modifiers_changed(self):
        print "_notify_step_modifiers_changed"
        for listener in self.listeners:
            try:
                listener.control_step_modifiers_changed()
            except AttributeError:
                pass # ignore

    def set_eyes_mode(self, mode):
        # We always allow resetting the mode because that might help
        # when TouchOSC clients are out of sync. However, only allow
        # known modes to get set.
        if mode != EYES_MODE_DISCO and mode != EYES_MODE_HEADLIGHTS and mode != EYES_MODE_SHOW:
            print "Unknown eyes mode %s" % mode
            return

        self.eyes_mode = mode
        self._notify_eyes_mode_changed()

        if mode == EYES_MODE_DISCO:
            self.p_eye_pos = list(config.get("eye_positions")["disco"][0])
            self._notify_eye_changed(True)
        elif mode == EYES_MODE_HEADLIGHTS:
            self._update_headlights()
        elif mode == EYES_MODE_SHOW:
            self._update_show_target()
        

    def _notify_eyes_mode_changed(self):
        print "_notify_eyes_mode_changed"
        for listener in self.listeners:
            try:
                listener.control_eyes_mode_changed()
            except AttributeError:
                pass # ignore


    def set_disco_mix(self, v):
        self.disco_mix =  v != 0.0
        self._notify_disco_color_changed()

    def set_disco_cycle_speed(self, v):        
        self.disco_cycle_speed = v
        if v < 0:
            self.disco_color_pos = 189 + int(v * 61.0)
        elif v > 0:
            self.disco_color_pos = 194 + int(v * 61.0)

        self._notify_disco_color_changed()

    def set_disco_color_pos(self, v):
        self.disco_color_pos = v

        # instead of mixing in the disco_mix here, we do it
        # when we set the color in the eye so that we can tap mix
        # on and off

        self.disco_cycle_speed = 0.0
        self._notify_disco_color_changed()

    def _notify_disco_color_changed(self):
        print "_notify_disco_color_changed"
        for listener in self.listeners:
            try:
                listener.control_disco_color_changed()
            except AttributeError:
                pass # ignore        

    def set_disco_brightness(self, v):
        self.disco_brightness = v
        self._notify_disco_brightness_changed()

    def _notify_disco_brightness_changed(self):
        print "_notify_disco_brightness_changed"
        for listener in self.listeners:
            try:
                listener.control_disco_brightness_changed()
            except AttributeError:
                pass # ignore        


    def set_disco_no_effect(self):
        self.disco_effect = 0
        self.disco_effect_speed = 0.0
        self._notify_disco_effect_changed()


    def set_disco_effect_speed(self, v):
        self.disco_effect_speed = v
        self._notify_disco_effect_changed()

    def set_disco_effect(self, x, y):
        self.disco_effect = x + ((y-1) * 8)
        self._notify_disco_effect_changed()

    def maybe_unset_disco_effect(self, x, y):
        effect = x + ((y-1) * 8)
        if effect == self.disco_effect:
            self.disco_effect = 0
            self._notify_disco_effect_changed()

    def _notify_disco_effect_changed(self):
        print "_notify_disco_effect_changed"
        for listener in self.listeners:
            try:
                listener.control_disco_effect_changed()
            except AttributeError:
                pass # ignore        


    def set_headlights_mode(self, mode):
        if mode != HEADLIGHTS_MODE_NORMAL and mode != HEADLIGHTS_MODE_LEFT and mode != HEADLIGHTS_MODE_BOTH and mode != HEADLIGHTS_MODE_RIGHT:
            print "Unknown headlights mode %s" % mode
            return

        self.headlights_mode = mode
        self._notify_headlights_mode_changed()

        self._update_headlights()


    def _notify_headlights_mode_changed(self):
        print "_notify_headlights_mode_changed"
        for listener in self.listeners:
            try:
                listener.control_headlights_mode_changed()
            except AttributeError:
                pass # ignore      



    def set_eyes_target(self, x, y):
        if self.eyes_mode == EYES_MODE_HEADLIGHTS:
            self.headlights_target[0] = x
            self.headlights_target[1] = y

            self._update_headlights()

        else:
            self.show_target[0] = x
            self.show_target[1] = y

            self._update_show_target()

    def set_eyes_focus(self, focus):
        self.focus = focus

        self._notify_focus_changed(self)


    def _notify_focus_changed(self):
        print "_notify_focus_changed"
        for listener in self.listeners:
            try:
                listener.control_focus_changed()
            except AttributeError:
                pass # ignore              

    def _set_eye_xy_front_pos(self, x, y):
        # Units for X and Y real are "height of the eye" = 1. Scaling out so
        # that we can tweak it more here than in touch and can define a reasonable
        # addressable area
        xr = config.get("xy_scale")["x"] * x
        yr = config.get("xy_scale")["y"] * (y + 0.5)

        # y gets weird because +y is down
        yr = 1.0 - yr

        xyz_pos = [xr, 10.0, yr]

        print "in=(%f,%f) xyz = %s" % (x,y, str(xyz_pos))

        self.p_eye_pos = eyes.xyz_to_pnt(xyz_pos, True)
        self._notify_eye_changed(True)

        self.b_eye_pos = eyes.xyz_to_pnt(xyz_pos, False)
        self._notify_eye_changed(False)




    def _update_headlights(self):
        left = False
        right = False
        if self.headlights_mode == HEADLIGHTS_MODE_LEFT:
            left = True
        elif self.headlights_mode == HEADLIGHTS_MODE_BOTH:
            left = True
            right = True
        elif self.headlights_mode == HEADLIGHTS_MODE_RIGHT:
            right = True

        if left or right:
            self._set_eye_xy_flat_pos(self.headlights_target[0], self.headlights_target[1], left, right, False)

        if not left:
            self.p_eye_pos = list(config.get("eye_positions")["headlights"][0])
            self._notify_eye_changed(True)

        if not right:
            self.b_eye_pos = list(config.get("eye_positions")["headlights"][1])
            self._notify_eye_changed(False)

    def _update_show_target(self):
        if self.show_target_mode == SHOW_TARGET_MODE_NONE:
            # We set _something_ here because some shows don't know to respect
            # the mode and stop using the target if the mode is different
            self.p_eye_pos = list(config.get("eye_positions")["headlights"][0])
            self.b_eye_pos = list(config.get("eye_positions")["headlights"][1])
            self._notify_eye_changed(True)
            self._notify_eye_changed(False)

        elif self.show_target_mode == SHOW_TARGET_MODE_UP:
            self._set_eye_xy_flat_pos(self.show_target[0], self.show_target[1], True, True, True)

        elif self.show_target_mode == SHOW_TARGET_MODE_DOWN:
            self._set_eye_xy_flat_pos(self.show_target[0], self.show_target[1], True, True, False)

        elif self.show_target_mode == SHOW_TARGET_MODE_FRONT:
            self._set_eye_xy_front_pos(self.show_target[0], self.show_target[1])

        else:
            # Is P & T mode, so set scaled version of max value
            pan = self.show_target[0] * 90.0  # Don't bother with full range
            tilt = self.show_target[1] * -135.0

            self.p_eye_pos[PAN] = self.b_eye_pos[PAN] = pan
            self.p_eye_pos[TILT] = self.b_eye_pos[TILT] = tilt

            self._notify_eye_changed(True)
            self._notify_eye_changed(False)

    def set_show_target_mode(self, mode):

        if mode != SHOW_TARGET_MODE_NONE and mode != SHOW_TARGET_MODE_UP and mode != SHOW_TARGET_MODE_DOWN and mode != SHOW_TARGET_MODE_PNT and mode != SHOW_TARGET_MODE_FRONT:
            print "Unrecognized show target mode %s" % mode
            return

        self.show_target_mode = mode
        self._notify_show_target_mode_changed()
        self._update_show_target()


    def _notify_show_target_mode_changed(self):
        print "_notify_show_target_mode_changed"
        for listener in self.listeners:
            try:
                listener.control_show_target_mode_changed()
            except AttributeError:
                pass # ignore      


    def set_master_names(self, names):
        self.master_names = names
        self._notify_master_names_changed()

    def _notify_master_names_changed(self):
        print "_notify_master_names_changed"
        for listener in self.listeners:
            try:
                listener.control_master_names_changed()
            except AttributeError:
                pass # ignore      

    def set_eo_names(self, names):
        self.eo_names = names
        self._notify_eo_names_changed()

    def _notify_eo_names_changed(self):
        print "_notify_eo_names_changed"
        for listener in self.listeners:
            try:
                listener.control_eo_names_changed()
            except AttributeError:
                pass # ignore      


    def set_overlay_names(self, names):
        self.overlay_names = names
        self._notify_overlay_names_changed()

    def _notify_overlay_names_changed(self):
        print "_notify_overlay_names_changed"
        for listener in self.listeners:
            try:
                listener.control_overlay_names_changed()
            except AttributeError:
                pass # ignore      


    def set_master_name(self, name):
        self.master_name = name
        self._notify_master_name_changed()

    def _notify_master_name_changed(self):
        print "_notify_master_name_changed"
        for listener in self.listeners:
            try:
                listener.control_master_name_changed()
            except AttributeError:
                pass # ignore      

    def set_eo_name(self, name):
        self.eo_name = name
        self._notify_eo_name_changed()

    def _notify_eo_name_changed(self):
        print "_notify_eo_name_changed"
        for listener in self.listeners:
            try:
                listener.control_eo_name_changed()
            except AttributeError:
                pass # ignore      


    def set_max_time(self, secs):
        self.max_time = float(secs)
        self._notify_max_time_changed()

    def set_max_time_scaled(self, scaled):
        _range = self.time_limits[1] - self.time_limits[0]
        self.max_time = self.time_limits[0] + (scaled * _range)
        self._notify_max_time_changed()

    def _notify_max_time_changed(self):
        print "_notify_max_time_changed"
        for listener in self.listeners:
            try:
                listener.control_max_time_changed()
            except AttributeError:
                pass # ignore      


    def set_message(self, msg):
        self.message = msg
        self._notify_message_changed()

    def _notify_message_changed(self):
        print "_notify_message_changed"
        for listener in self.listeners:
            try:
                listener.control_message_changed()
            except AttributeError:
                pass # ignore      


    def set_effect_preset(self, ix, effect):
        if ix < 0 or ix > len(self.effects)-1:
            print "Invalid index %d" % ix
            return False

        self.effects[ix] = effect

        self.save_effects()

        return True

    def save_effects(self):
        try:
            out = []
            for e in self.effects:
                out.append(e.as_json())

            with open("data/effects.json", "w") as f:
                json.dump(out,f,indent=2)

        except Exception:
            traceback.print_exc()

    def load_effects(self):
        try:
            with open("data/effects.json", "r") as f:
                _json = json.load(f)

            for ix in range(0, len(_json)):
                e = eye_effect.EyeEffect(json=_json[ix])

                if ix < len(self.effects):
                    self.effects[ix] = e
                else:
                    self.effects.append(e)

        except Exception:
            traceback.print_exc()

    def set_default_effects(self):
        self.effects = [
            eye_effect.EyeEffect(gobo=1, 
                external_speed_modifies=eye_effect.SPEED_MODIFIES_GOBO_SHAKE),
            eye_effect.EyeEffect(gobo=2, 
                external_speed_modifies=eye_effect.SPEED_MODIFIES_GOBO_SHAKE),
            eye_effect.EyeEffect(gobo=3, 
                external_speed_modifies=eye_effect.SPEED_MODIFIES_GOBO_SHAKE),
            eye_effect.EyeEffect(gobo=4, 
                external_speed_modifies=eye_effect.SPEED_MODIFIES_GOBO_SHAKE),
            eye_effect.EyeEffect(gobo=5, 
                external_speed_modifies=eye_effect.SPEED_MODIFIES_GOBO_SHAKE),
            eye_effect.EyeEffect(gobo=6, 
                external_speed_modifies=eye_effect.SPEED_MODIFIES_GOBO_SHAKE),
            eye_effect.EyeEffect(gobo=7, 
                external_speed_modifies=eye_effect.SPEED_MODIFIES_GOBO_SHAKE),
            eye_effect.EyeEffect(gobo=8, 
                external_speed_modifies=eye_effect.SPEED_MODIFIES_GOBO_SHAKE),


            eye_effect.EyeEffect(gobo=9, 
                external_speed_modifies=eye_effect.SPEED_MODIFIES_GOBO_SHAKE),
            eye_effect.EyeEffect(gobo=10, 
                external_speed_modifies=eye_effect.SPEED_MODIFIES_GOBO_SHAKE),
            eye_effect.EyeEffect(gobo=11, 
                external_speed_modifies=eye_effect.SPEED_MODIFIES_GOBO_SHAKE),
            eye_effect.EyeEffect(gobo=12, 
                external_speed_modifies=eye_effect.SPEED_MODIFIES_GOBO_SHAKE),
            eye_effect.EyeEffect(gobo=13, 
                external_speed_modifies=eye_effect.SPEED_MODIFIES_GOBO_SHAKE),
            eye_effect.EyeEffect(gobo=14, 
                external_speed_modifies=eye_effect.SPEED_MODIFIES_GOBO_SHAKE),
            eye_effect.EyeEffect(gobo=15, 
                external_speed_modifies=eye_effect.SPEED_MODIFIES_GOBO_SHAKE),
            eye_effect.EyeEffect(gobo=16, 
                external_speed_modifies=eye_effect.SPEED_MODIFIES_GOBO_SHAKE),


            eye_effect.EyeEffect(gobo=0,
                external_speed_modifies=eye_effect.SPEED_MODIFIES_GOBO_ROTATION),
            eye_effect.EyeEffect(shutter_type=eye_effect.SHUTTER_STROBE,
                external_speed_modifies=eye_effect.SPEED_MODIFIES_SHUTTER),
            eye_effect.EyeEffect(shutter_type=eye_effect.SHUTTER_PULSE,
                external_speed_modifies=eye_effect.SPEED_MODIFIES_SHUTTER),
            eye_effect.EyeEffect(shutter_type=eye_effect.SHUTTER_RANDOM,
                external_speed_modifies=eye_effect.SPEED_MODIFIES_SHUTTER),

            eye_effect.EyeEffect(effect_mode=eye_effect.EFFECT_LADDER,
                external_speed_modifies=eye_effect.SPEED_MODIFIES_EFFECT_ROTATION),
            eye_effect.EyeEffect(effect_mode=eye_effect.EFFECT_8_FACET,
                external_speed_modifies=eye_effect.SPEED_MODIFIES_EFFECT_ROTATION),
            eye_effect.EyeEffect(effect_mode=eye_effect.EFFECT_3_FACET,
                external_speed_modifies=eye_effect.SPEED_MODIFIES_EFFECT_ROTATION),

            eye_effect.EyeEffect(gobo=eye_effect.GOBOS["five_stars"],
                external_speed_modifies=eye_effect.SPEED_MODIFIES_FOCUS),

        ]        