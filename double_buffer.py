
import color
import tween

class DoubleBuffer(object):
    """
    A class to be used by shows that want to maintain a double buffer
    of color values and then slowly fade between them. LoopingShow
    descendents may wish this if they want to avoid the way the 
    fadecandy does color transitions in favor of our own methods.

    Call set_next(cell_id, color) a bunch of times to establish a
    frame. Then call morph_at(progress, output_fn) multiple times 
    to write the frame out to the passed in output function. That
    function is expected to be a sheep side set_cell(cell_id, color)
    function. Finally, call advance() to move on to the next frame
    and start it all again.
    """
    def __init__(self):
        # Start with empty buffers, but start with buffers
        self.last = {}
        self.next = {}

    def set_next(self, cell_id, color):
        """
        Set a color into the 'next' frame
        """
        self.next[cell_id] = color

    def tween_hsv_at(self, progress, output):
        """
        Go through all cells that we have in next and morph them
        towards their next color at the given progress value
        """
        for cell_id in self.next.keys():
            next_color = self.next[cell_id]

            if cell_id in self.last:
                last_color = self.last[cell_id]
            else:
                last_color = color.BLACK

            cell_color = color.Color(tween.hsvLinear(last_color, next_color, progress))
            output(cell_id, cell_color)

    def tween_rgb_at(self, progress, output):
        """
        Go through all cells that we have in next and morph them
        towards their next color at the given progress value
        """
        for cell_id in self.next.keys():
            next_color = self.next[cell_id]

            if cell_id in self.last:
                last_color = self.last[cell_id]
            else:
                last_color = color.BLACK

            r = tween.linear(last_color.r, next_color.r, progress)
            g = tween.linear(last_color.g, next_color.g, progress)
            b = tween.linear(last_color.b, next_color.b, progress)
            cell_color = color.RGB(r,g,b)
            output(cell_id, cell_color)

    def advance(self):
        """
        Advance next to last, establishing an empty next
        """
        self.last = self.next
        self.next = {}