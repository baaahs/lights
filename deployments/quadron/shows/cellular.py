import geom

import color
import palette
import time

import random
import math

import looping_show
from randomcolor import random_color
import tween

import threading
import traceback

import double_buffer


class CellularState(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.time_to_die = threading.Event()
        self.next_state_ready = threading.Event()
        self.next_state_used = threading.Event()
        self.next_state_used.set()

        # The rate at which cells decay from 1.0 (alive) towards 0.0
        # The reciprocal of this number is the number of "steps" of death
        # that a cell will experience when it is not alive
        self.decay_rate = 0.1

        self.current_state = {}
        for cid in geom.all_edges.cell_ids:
            self.current_state[cid] = random.random() * 1.5
            if self.current_state[cid] >= 1.0:
                self.current_state[cid] = 1.0

        self.next_state = {}

        # self.daemon = True


    def run(self):
        print "Cellular state generation thread started"
        try:
            while not self.time_to_die.is_set():
                self.next_state_used.wait()

                if self.time_to_die.is_set():
                    continue

                self.next_state_used.clear()

                # Calculate a new state
                # Calculate the new condition of all cells
                started_at = time.time()

                self.next_state = {}
                total_alive = 0
                for name, edge in geom.base_edges.iteritems():
                    for cell_id in edge.cell_ids:
                        neighbors = edge.cells_that_neighbor(cell_id, 0.10)

                        # Count how many of those neighbors are activated
                        count = 0
                        for n in neighbors:
                            if self.current_state[n] == 1.0:
                                count += 1

                        # Decide if this cell lives or dies

                        # Start with the assumption that we are going to be dead,
                        # which means one more step towards 0.0
                        new_cell_state = self.current_state[cell_id] - self.decay_rate

                        if self.current_state[cell_id] == 1.0:
                            # This cell is currently alive, does it stay alive?
                            if count > 3 and count < 7:
                                new_cell_state = 1.0
                        else:
                            # It is dead, does it come to life
                            if count > 3:
                                new_cell_state = 1.0

                        # Clamp at 0
                        if new_cell_state < 0.0:
                            new_cell_state = 0.0

                        self.next_state[cell_id] = new_cell_state
                        if new_cell_state == 1.0:
                            total_alive += 1

                ids = self.next_state.keys()
                if total_alive < 80:
                    print "Aaack. Need more cells"
                    # Aack! Need some random new stuff
                    while total_alive < 100:
                        maybe = random.choice(ids)
                        if self.next_state[maybe] != 1.0:
                            self.next_state[maybe] = 1.0
                            total_alive += 1

                # To ensure that the world is never perfectly stable, always randomly
                # flip some cells which hopefully introduces just enough chaos to keep things flowing
                for x in range(2):
                    id = random.choice(ids)
                    if self.next_state[id] == 1.0:
                        self.next_state[id] -= self.decay_rate
                    else:
                        self.next_state[id] = 1.0


                total_time = time.time() - started_at
                self.next_state_ready.set()

                print "cellular frame time = {0:.0f}ms  total_alive={1}".format(total_time * 1000.0, total_alive)


        except Exception as e:
            traceback.print_exc()

        # Always make sure this is set once we exit
        self.time_to_die.set()
        print "Cellular state generation thread finished! :)"



    def activate_next_state(self):
        """
        Called by the client to move next_state to current_state, blocking on
        the creation of next_state if necessary.
        """

        if self.time_to_die.is_set():
            return

        self.next_state_ready.wait()
        self.current_state = self.next_state

        self.next_state_ready.clear()
        self.next_state_used.set();




class Cellular(looping_show.LoopingShow):

    # Because we extend LoopingShow we must explicitly override is_show to be True
    is_show = True
    
    name = "Cellular"

    modifier_usage = {
        "toggles": {
            0: "Hard On/Off",
            1: "!Blended",
        }
    }
    modifier_usage["step"] = palette.common_names_as_step_modes()

    num_step_modes = len(modifier_usage["step"])

    def __init__(self, sheep_sides):
        looping_show.LoopingShow.__init__(self, sheep_sides)

        # Our duration is a single automata step, so fairly short
        self.duration = 2.0
        self.core_duration = 2.0

        self.buffer = double_buffer.DoubleBuffer()

        # Then make a worker thread that will create new states
        self.state = CellularState()
        self.state.daemon = True
        self.state.start()

    def finished(self):
        self.state.time_to_die.set()

    # def set_controls_model(self, cm):
    #     super(Rainbow, self).set_controls_model(cm)

    #     self.cm.reset_step_modifiers()

    def was_selected_randomly(self):
        # self.cm.reset_step_modifiers(self.num_step_modes)

        # self.cm.set_modifier(0, (random.randrange(10) > 6))
        # self.cm.set_modifier(1, (random.randrange(10) > 4))
        # self.cm.set_modifier(2, (random.randrange(10) > 3))
        # self.cm.set_modifier(3, (random.randrange(10) > 4))
        # self.cm.set_modifier(4, (random.randrange(10) > 3))

        #print "MODE = %d" % (self.step_mode(3))
        #self.cm.reset_step_modifiers()
        pass

    # def control_modifiers_changed(self):
    #     if self.cm.modifiers[3]:
    #         self.duration = 16
    #     else:
    #         self.duration = 32
    def control_step_modifiers_changed(self):
        mode = self.step_mode(-1)
        if mode in self.modifier_usage["step"]:
            self.cm.set_message(self.modifier_usage["step"][mode])
        else:
            self.cm.set_message("Mode %d" % mode)


    def update_at_progress(self, progress, new_loop, loop_instance):

        self.duration = self.core_duration - (self.cm.intensified * (self.core_duration-0.2))
        if self.cm.modifiers[0]:
            self.duration += 2.0

        mode = self.step_mode(-1)
        p = palette.palette_for_step_mode(mode)

        if self.cm.modifiers[0]:
            clr_on = self.cm.chosen_colors[0]
            clr_off = self.cm.chosen_colors[1]

        # One loop is a single cellular change. Thus the progress in the loop
        # is really about transitioning from one state to another.
        if new_loop:
            self.state.activate_next_state()
            self.buffer.advance()

            # Just show the current state
            for cid, state in self.state.current_state.iteritems():

                if self.cm.modifiers[0]:
                    # Hard on/off. No color gradiation
                    if state == 1.0:
                        clr = p.color_in_ramp(1.0)
                    else:
                        clr = p.color_in_ramp(0.0)
                else:
                    # Use a blended value from the current palette
                    clr = p.color_in_ramp(state, not self.cm.modifiers[0])


                self.buffer.set_next(cid, clr)
    
        self.buffer.tween_rgb_at(progress, lambda cell_id, clr: self.ss.both.set_cell(cell_id, clr) )