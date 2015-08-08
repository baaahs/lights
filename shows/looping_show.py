import sheep
from color import RGB
import time

import random
import math

class LoopingShow(object):
    """
    Rather than being an interesting show on it's own, this show is
    a base class that can be extended by shows that want to run in
    a continous loop (which is most shows).

    It records the start time, and performs per-frame calculations to

    """

    name = "Looping Show"

    # Setting this to False prevents the auto-loader from loading this
    # class itself as a show. The things that extend this class will want
    # to set this to True
    is_show = False

    def __init__(self, sheep_sides):
        # Some convenience variables
        self.ss = sheep_sides

        self.pe = sheep_sides.party_eye
        self.be = sheep_sides.business_eye

        self._hertz = 0.5

    def clear(self):
        pass

    def set_controls_model(self, cm):
        self.cm = cm

    def control_refreshAll(self):
        # Whatever - we just get the data when we refresh the frame
        pass

    def update_at_progress(self, progress, new_loop, loop_instance):
        """
        This is the main method that should be overridden by a subclass. This
        method needs to update all panels and eye positions for the given
        progress through the whole show. 

        The progress will range between 0.0 and 1.0. Say a show moves a color
        from the front of the sheep to the back of the sheep. When this method
        is called with 0.5, then it should update the panels so the color is
        at the halfway point.

        When the show rolls over from one instance of the loop to the next,
        the new_loop argument will be True for one call. After that it will be
        False until the next loop begins.

        loop_instance is an integer which identifies how many times the loop
        has occurred. The first time through the loop this will be 0, and will
        increment by 1 each time new_loop goes to True. This is useful for
        introducing mild state changes on each loop iteration.
        """
        pass

    @property
    def hertz(self):
        """
        The speed the loop is running at in hertz. The default value is 0.5, 
        which corresponds to 120bpm, and a loop_time of 2s. Note that this is
        the 'natural' speed of the loop and it will be adjusted by the speed
        set in the controls model.
        """
        return self._hertz

    @hertz.setter
    def hertz(self, val):
        self._hertz = float(val)

    @property
    def bpm(self):
        """
        The natural bpm for this show.  The default value is 120bpm. This is
        the natural speed which will be affected by the externally set show
        speed.
        """
        return 60.0 / self._hertz

    @bpm.setter
    def bpm(self, val):
        self._hertz = 60.0 / val

    @property
    def duration(self):
        """
        The natural duration of the show in seconds. The default value is 2s,
        and then this is controlled externally so this is almost never going
        to be the true time it takes for a single loop.
        """
        return 1.0 / self._hertz

    @duration.setter
    def duration(self, val):
        self._hertz = 1.0  / val

    def step_mode(self, max=None):
        """
        A convenience method which maps the first two cm step modifers as
        though they were previous and next buttons. If a max value is
        passed, then the returned value will be in [0, max) and will
        properly loop at 0 rather. If no max is given then a negative
        value could be returned.
        """
        v = self.cm.step_modifiers[1] - self.cm.step_modifiers[0]
        if max is not None:
            v = v % max
            while v < 0:
                v += max

        return v

    def next_frame(self):
        """
        This is a generator called by the show runner periodically to get the
        next frame of the show. It should NOT be overriden by sub classes.
        Instead sub classes should implement update_at_progress().
        """

        self._last_frame_at = time.time()
        self._progress = 0.0
        self._loop_instance = 0
        is_first_loop = True

        while True:
            # How fast are we going? This is in "loops per second", which
            # is hertz, but adjusted by the speed set in the controls model
            speed = self._hertz * self.cm.speed_multi

            # How far have we traveled in "loops" during this time?
            # We presume our speed between the last call and this call has
            # been constant at the speed that is currently set.
            now = time.time()            
            elapsed_time = now - self._last_frame_at

            distance_traveled = elapsed_time * speed

            new_location = self._progress + distance_traveled 
            new_prog, loops = math.modf(new_location)

            self._loop_instance += int(loops)
            self._progress = new_prog

            is_new = loops > 0 or is_first_loop
            # print "%f [%f, %f]=%f %f update(%f, %s, %d)" % (elapsed_time, 
            #         self._hertz, self.cm.speed_multi, speed, 
            #         distance_traveled, 
            #         self._progress, str(is_new), self._loop_instance)    
            self.update_at_progress(self._progress, is_new, self._loop_instance)

            self._last_frame_at = now
            is_first_loop = False

            yield 0.001
