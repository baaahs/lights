import math
import traceback

import eyes

SHUTTER_OPEN    = "open"
SHUTTER_CLOSED  = "closed"
SHUTTER_STROBE  = "strobe"
SHUTTER_PULSE   = "pulse"
SHUTTER_RANDOM  = "random"

GOBOS = {
    "none": 0,
    "circle_0": 1,
    "circle_1": 2,
    "circle_2": 3,
    "circle_3": 4,
    "circle_4": 5,
    "curve": 6,
    "five_stars": 7,
    "star_curve": 8,
    "circle_swoosh": 9,
    "small_splat": 10,
    "hairy_circle": 11,
    "flower": 12,
    "sperm": 13,
    "ying_yang": 14,
    "lightning": 15,
    "big_splat": 16
}

EFFECT_NONE     = "none"
EFFECT_LADDER   = "ladder"
EFFECT_8_FACET = "8"
EFFECT_3_FACET = "3"

SPEED_MODIFIES_NOTHING          = "nothing"
SPEED_MODIFIES_SHUTTER          = "shutter"
SPEED_MODIFIES_GOBO_ROTATION    = "gobo_rotation"
SPEED_MODIFIES_GOBO_SHAKE       = "gobo_shake"
SPEED_MODIFIES_EFFECT_ROTATION  = "effect_shake"
SPEED_MODIFIES_FOCUS            = "focus"  # Not really speed, but handy to have in externally controllable form
SPEED_MODIFIES_FROST_SPEED      = "frost_speed"

FROST_NONE = "none"
FROST_STEADY = "steady"
FROST_OPENING = "opening"
FROST_CLOSING = "closing"
FROST_MAX = "max"

def clear_all(dmxer):
    dmxer.set_eye_dmx(eyes.EYE_DMX_STROBE, 255)
    dmxer.set_eye_dmx(eyes.EYE_DMX_GOBO, 0)
    dmxer.set_eye_dmx(eyes.EYE_DMX_EFFECT, 0)
    # Don't modify focus
    dmxer.set_eye_dmx(eyes.EYE_DMX_FROST, 0)


class EyeEffect(object):
    def __init__(self, shutter_type=SHUTTER_OPEN, shutter_speed=0.0, 
        gobo_rotation=0.0, gobo=0, gobo_shake_speed=0.0,
        effect_mode = EFFECT_NONE, effect_rotation=0.0,
        focus=None, frost=FROST_NONE, frost_speed=0.0,
        external_speed_modifies=SPEED_MODIFIES_NOTHING, json=None):

        self.shutter_type = shutter_type
        self.shutter_speed = shutter_speed

        self.gobo_rotation = gobo_rotation  # Rotate the gobo wheel in forwards direction. 0=no
        self.gobo = gobo
        self.gobo_shake_speed = gobo_shake_speed # Only 5 shake speeds, 0 = no shake

        self.effect_mode = effect_mode
        self.effect_rotation = effect_rotation # 61 options in forward and reverse

        self.focus = focus

        self.frost = frost
        self.frost_speed = frost_speed

        self.external_speed_modifies = external_speed_modifies

        if json is not None:
            if 'shutter_type' in json:
                self.shutter_type = json["shutter_type"]
            if 'shutter_speed' in json:
                self.shutter_speed = json["shutter_speed"]
            if 'gobo_rotation' in json:
                self.gobo_rotation = json["gobo_rotation"]
            if 'gobo' in json:
                self.gobo = json["gobo"]
            if 'gobo_shake_speed' in json:
                self.gobo_shake_speed = json["gobo_shake_speed"]
            if 'effect_mode' in json:
                self.effect_mode = json["effect_mode"]
            if 'effect_rotation' in json:
                self.effect_rotation = json["effect_rotation"]
            if 'focus' in json:
                self.focus = json["focus"]
            if 'frost' in json:
                self.frost = json["frost"]
            if 'frost_speed' in json:
                self.frost_speed = json["frost_speed"]
            if 'external_speed_modifies' in json:
                self.external_speed_modifies = json["external_speed_modifies"]

    def __repr__(self):
        return str(self.as_json())
        
    def as_json(self):
        out = {
            'shutter_type': self.shutter_type,
            'shutter_speed': self.shutter_speed,
            'gobo_rotation': self.gobo_rotation,
            'gobo': self.gobo,
            'gobo_shake_speed': self.gobo_shake_speed,
            'effect_mode': self.effect_mode,
            'effect_rotation': self.effect_rotation,
            'focus': self.focus,
            'frost': self.frost,
            'frost_speed': self.frost_speed,
            'external_speed_modifies': self.external_speed_modifies
        }

        return out



    def go(self, dmxer, speed=0.0):
        try:
            shutter_speed = self.shutter_speed
            gobo_rotation = self.gobo_rotation
            gobo_shake_speed = self.gobo_shake_speed
            effect_rotation = self.effect_rotation
            frost_speed = self.frost_speed
            focus = self.focus

            if self.external_speed_modifies == SPEED_MODIFIES_SHUTTER:
                shutter_speed = speed
            elif self.external_speed_modifies == SPEED_MODIFIES_GOBO_ROTATION:
                gobo_rotation = speed
            elif self.external_speed_modifies == SPEED_MODIFIES_GOBO_SHAKE:
                gobo_shake_speed = speed
            elif self.external_speed_modifies == SPEED_MODIFIES_EFFECT_ROTATION:
                effect_rotation = speed
            elif self.external_speed_modifies == SPEED_MODIFIES_FROST_SPEED:
                frost_speed = speed
            elif self.external_speed_modifies == SPEED_MODIFIES_FOCUS:
                focus = speed


            # Shutter
            v = 255 # Default for SHUTTER_OPEB
            if self.shutter_type == SHUTTER_CLOSED:
                v = 0
            elif self.shutter_type == SHUTTER_STROBE:
                v = 64 + int(math.floor(shutter_speed * 31.0))
            elif self.shutter_type == SHUTTER_PULSE:
                v = 128 + int(math.floor(shutter_speed * 31.0))
            elif self.shutter_type == SHUTTER_RANDOM:
                v = 192 + int(math.floor(shutter_speed * 31.0))
            dmxer.set_eye_dmx(eyes.EYE_DMX_STROBE, v)


            # GOBO
            if gobo_rotation > 0:
                v = 218 + int(math.floor(gobo_rotation * 37.0))
            else:
                # No gobo rotation, maybe a gobo is inserted?
                if self.gobo == 0:
                    # No gobo
                    v = 0
                else:
                    if gobo_shake_speed > 0:
                        v = 120 + (6*(self.gobo-1)) + int(math.floor(gobo_shake_speed * 5.0))
                    else:
                        v = self.gobo * 7

            dmxer.set_eye_dmx(eyes.EYE_DMX_GOBO, v)


            # Effect
            if self.effect_mode == EFFECT_NONE:
                dmxer.set_eye_dmx(eyes.EYE_DMX_EFFECT, 0)
                dmxer.set_eye_dmx(eyes.EYE_DMX_LADDER_ROTATE, 0)
                dmxer.set_eye_dmx(eyes.EYE_DMX_8_ROTATE, 0)
                dmxer.set_eye_dmx(eyes.EYE_DMX_3_ROTATE, 0)

            elif self.effect_mode == EFFECT_LADDER:
                dmxer.set_eye_dmx(eyes.EYE_DMX_EFFECT, 65)

                v = 190
                if effect_rotation < 0:
                    v = 189 + int(math.floor(effect_rotation * 61.0))
                elif effect_rotation > 0:
                    v = 194 + int(math.floor(effect_rotation * 61.0))
                dmxer.set_eye_dmx(eyes.EYE_DMX_LADDER_ROTATE, v)

            elif self.effect_mode == EFFECT_8_FACET:
                dmxer.set_eye_dmx(eyes.EYE_DMX_EFFECT, 129)

                v = 190
                if effect_rotation < 0:
                    v = 189 + int(math.floor(effect_rotation * 61.0))
                elif effect_rotation > 0:
                    v = 194 + int(math.floor(effect_rotation * 61.0))
                dmxer.set_eye_dmx(eyes.EYE_DMX_8_ROTATE, v)

            elif self.effect_mode == EFFECT_3_FACET:
                dmxer.set_eye_dmx(eyes.EYE_DMX_EFFECT, 192)

                v = 190
                if effect_rotation < 0:
                    v = 189 + int(math.floor(effect_rotation * 61.0))
                elif effect_rotation > 0:
                    v = 194 + int(math.floor(effect_rotation * 61.0))
                dmxer.set_eye_dmx(eyes.EYE_DMX_3_ROTATE, v)


            # Focus (can be None)
            if focus is not None:
                v = int(math.floor(focus * 255.0))
                dmxer.set_eye_dmx(eyes.EYE_DMX_FOCUS, v)

            # Frost
            v = 0 # Default for FROST_NONE
            if self.frost == FROST_MAX:
                v = 255
            elif self.frost == FROST_STEADY:
                v = int(math.floor(frost_speed * 191.0))
            elif self.frost == FROST_OPENING:
                v = 223 - int(math.floor(frost_speed * 31.0))
            elif self.frost == FROST_CLOSING:
                v = 254 - int(math.floor(frost_speed * 30.0))
            dmxer.set_eye_dmx(eyes.EYE_DMX_FROST, v)


        except Exception:
            traceback.print_exc()