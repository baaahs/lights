import time

from . import geom
import palette
import color

class BouncingSphere(object):

    name = "Sphere"

    is_show = True
    ok_for_random = True

    boundaries = ( (-0.6, 0.6), (0, 2.0), (0, 0.3) )

    def __init__(self, sheep_sides):
        self.ss = sheep_sides

        self.pos = [0.0, 1.0, 0.0]
        self.base_velocity = [0.5, 0.4, 0.1]
        # self.velocity = [0.5, 0.4, 0.1]



    def set_controls_model(self, cm):
        self.cm = cm
        # self.cm.randomize_color_selections()

    def was_selected_randomly(self):
        self.cm.set_modifier(0, (random.randrange(10) > 7))
        self.cm.set_modifier(1, (random.randrange(10) > 4))
        self.cm.set_modifier(2, (random.randrange(10) > 3))
        self.cm.set_modifier(3, (random.randrange(10) > 4))
        self.cm.set_modifier(4, (random.randrange(10) > 3))

        self.cm.randomize_color_selections()
        #print "MODE = %d" % (self.step_mode(3))
        #self.cm.reset_step_modifiers()

    def control_modifiers_changed(self):

        if self.cm.modifiers[3]:
            self.duration = 16
        else:
            self.duration = 32

    def color_at_distance(self, distance, palette):
        if distance < 0.5:
            return palette.first

        return palette.last

    def next_frame(self):
        self._last_frame_at = time.time() - .001

        while True:

            now = time.time()
            elapsed_time = now - self._last_frame_at

            self._last_frame_at = now

            # 1. Update our model

            velocity = [v * self.cm.speed_multi for v in self.base_velocity]

            # Move our position based on our velocity
            displacement = [elapsed_time * v for v in velocity]
            self.pos = list(map(sum, list(zip(self.pos, displacement))))

            # Check for boundary excess and fix velocity if we have reflected
            for i in range(3):
                bounds = self.boundaries[i]
                pos = self.pos[i]
                vel = velocity[i]

                if pos < bounds[0]:
                    #print "  ** Bounce on < in {}".format(i)
                    self.pos[i] = bounds[0] + (bounds[0] - pos)
                    self.base_velocity[i] *= -1
                elif pos > bounds[1]:
                    #print "  ** Bounce on > in {}".format(i)
                    self.pos[i] = bounds[1] - (pos - bounds[1])
                    self.base_velocity[i] *= -1
                #else it's all fine..

            #print "{0:.3f} pos={1} vel={2}".format(now, self.pos, velocity)
            # 2. Render the state

            # Collect things we need to render state, like the color palette

            p = palette.chosen

            # Shade every pixel
            for id, xyz in geom.cells_in_space.items():
                distance = geom.distance_to(self.pos, xyz)

                # Color is based on distance
                clr = self.color_at_distance(distance, p)

                # Debugging
                # if xyz[1] > 1.8:
                #     clr = color.RED
                # if xyz[1] < 0.4:
                #     clr = color.PURPLE
                # if xyz[0] > 0.5:
                #     clr = color.GREEN

                self.ss.party.set_cell(id, clr)

            #self.ss.party.set_cells(geom.faces["TOP_FRONT_ALL"].cell_ids, color.RED)

            yield 0.05

