import color
import sheep

import looping_show
import eye_effect


class EgOverlay(looping_show.LoopingShow):
    # The full list of attributes that are honored during show loading in
    # some way is:
    #
    #   is_show = <True> | False  
    #       identifies that the class should be loaded as a show or more 
    #       importantly shouldn't even though it looks like it is a show.
    #
    #   ok_for_random = <True> | False
    #       Include or exclude this show when picking an random one. This
    #       should be set for test shows that should only be triggered
    #       manually
    #
    #   name = "Something"
    #       Name that shows up in the interface (and that can be given on
    #       on the command line)
    #
    #   show_type = "overlay" | <"master"> | "eyes_only"
    #       Overlay shows are only active when you tap & hold on them from
    #       the UI. They can't be started in any other way.
    #       
    #       Normally shows are master shows. This means they modify the panels
    #       and they might also modify the eyes (whether or not they set the
    #       controls_eyes attribute below).
    #
    #       Setting this to eyes_only will prevent the show from being listed
    #       as one of the master shows.
    #
    #   controls_eyes = <False> | True
    #       If this is set, the show will be added to the "eyes only" list
    #       and can be invoked from there even if it also can be invoked
    #       as a master show. Any panel modifications it does when running as
    #       the eyes only show are ignored and only changes to the eye
    #       parameters are used. This lets you layer a base show with an
    #       eye show, even if they are both "master" shows
    #
    #   handles_colorized = <False> | True
    #       Declares that the show will take care of changing it's saturation
    #       or "colorization" level on it's own. If not set, the saturation
    #       of colors are changed right before they are written out to the
    #       panels, which is effective, but might not deliver the best 
    #       results in all situations.
    #
    #       A more clever, but show specific, technique would be to map the
    #       lower portion of the colorization range to a single color with
    #       an increasingly low saturation, and map the upper portion of the
    #       range to an increased number of colors.
    #

    # Because we extend LoopingShow we must explicitly override is_show to be True
    is_show = True
    
    name = "Eg Overlay"
    show_type = "overlay"
    controls_eyes = False

    def __init__(self, sheep_sides):
        looping_show.LoopingShow.__init__(self, sheep_sides)

        # Blink at a high rate
        # 20 loops per second
        self.hertz = 20

        # These are the effect objects we will use to flash the eyes
        self.open = eye_effect.EyeEffect(shutter_type=eye_effect.SHUTTER_OPEN)
        self.close = eye_effect.EyeEffect(shutter_type=eye_effect.SHUTTER_OPEN)


    def update_at_progress(self, progress, new_loop, loop_instance):

        if progress < 0.5:
            # The first half of a cycle is bright white
            self.ss.both.set_all_cells(color.WHITE)

            # Open the eye shutter
            self.pe.effect = self.open
            self.be.effect = self.open

        else:
            # The second half of a cycle is all dark
            self.ss.both.set_all_cells(color.BLACK)

            # including using the shutter on the eyes
            self.pe.effect = self.close
            self.pe.effect = self.close
