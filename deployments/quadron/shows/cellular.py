import geom

import color
import time

import random
import math

import looping_show
from randomcolor import random_color
import tween

import threading
import traceback


class CellularState(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.time_to_die = threading.Event()
        self.next_state_ready = threading.Event()
        self.next_state_used = threading.Event()
        self.next_state_used.set()

        self.current_state = {}
        for cid in geom.all_edges.cell_ids:
            self.current_state[cid] = (random.randrange(10) > 6)

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
                            if self.current_state[n]:
                                count += 1

                        # Decide if this cell lives or dies
                        new_cell_state = False
                        if self.current_state[cell_id]:
                            # It is currently alive, does it stay alive?
                            if count > 2 and count < 8:
                                new_cell_state = True
                        else:
                            # It is dead, does it come to life
                            if count > 3:
                                new_cell_state = True

                        self.next_state[cell_id] = new_cell_state
                        if new_cell_state:
                            total_alive += 1

                if total_alive < 80:
                    print "Aaack. Need more cells"
                    # Aack! Need some random new stuff
                    ids = self.next_state.keys()
                    while total_alive < 100:
                        maybe = random.choice(ids)
                        if not self.next_state[maybe]:
                            self.next_state[maybe] = True
                            total_alive += 1

                total_time = time.time() - started_at
                self.next_state_ready.set()

                print "cellular frame time = {0:.0f}ms".format(total_time * 1000.0)


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
            0: "Use HSY",
            1: "Reverse",
        },
        "step": {
            0: "Long Planes",
            1: "Short Planes",
            2: "Edges",
            3: "Faces",
        }
    }

    num_steps = len(modifier_usage["step"])

    def __init__(self, sheep_sides):
        looping_show.LoopingShow.__init__(self, sheep_sides)

        # Our duration is a single automata step, so fairly short
        self.duration = 0.5

        # Create an initial state

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
        # self.cm.reset_step_modifiers(self.num_steps)

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
        mode = self.step_mode(self.num_steps)
        if mode in self.modifier_usage["step"]:
            self.cm.set_message(self.modifier_usage["step"][mode])
        else:
            self.cm.set_message("Mode %d" % mode)


    def update_at_progress(self, progress, new_loop, loop_instance):
        # One loop is a single cellular change. Thus the progress in the loop
        # is really about transitioning from one state to another.
        if new_loop:
            self.state.activate_next_state()

        # Just show the current state
        for cid, state in self.state.current_state.iteritems():
            if state:
                clr = color.WHITE
            else:
                clr = color.BLACK

            self.ss.party.set_cell(cid, clr)
    
