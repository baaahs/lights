import sheep
from color import RGB
import time

import random
import math

from . import looping_show
from randomcolor import random_color
import morph

from model.ola_model import PANEL_MAP

class BlinkOne(looping_show.LoopingShow):
    is_show = True
    name = "_Blink 1"
    ok_for_random = False

    def __init__(self, sheep_sides):
        looping_show.LoopingShow.__init__(self, sheep_sides)
        self.black = RGB(0,0,0)
        self.white = RGB(255,255,255)

        # Load a bunch of things from the panels in the ola model
        self.party_panels = []
        self.business_panels = []
        self.dmx_to_panel = {}
        self.dmx_addrs = []
        for key in PANEL_MAP:
            dmx = PANEL_MAP[key]
            if key[-1:] == "p":
                try:
                    self.party_panels.append(int(key[:-1]))
                except ValueError:
                    continue
            elif key[-1:] == "b":
                try:
                    self.business_panels.append(int(key[:-1]))
                except ValueError:
                    continue
            else:
                continue

            if type(dmx) is int:
                self.dmx_to_panel[dmx] = key
                self.dmx_addrs.append(dmx)
            else:
                for x in dmx:
                    self.dmx_to_panel[x] = key
                    self.dmx_addrs.append(x)

        self.party_panels = sorted(self.party_panels)
        self.business_panels = sorted(self.business_panels)
        self.dmx_addrs = sorted(self.dmx_addrs)

        print("party_panels = %s" % str(self.party_panels))
        print("business_panels = %s" % str(self.business_panels))
        print("dmx_addrs = %s" % str(self.dmx_addrs))

        self.hertz = 3.0


    def set_controls_model(self, cm):
        super(BlinkOne, self).set_controls_model(cm)

        self._update_message()
        # self.cm.reset_step_modifiers()

    def clear(self):
        c = self.black

        self.ss.both.set_all_cells(c)

    def control_modifiers_changed(self):
        self._update_message()

    def control_step_modifiers_changed(self):
        self._update_message()

    def _update_message(self):
        if self.cm.modifiers[1]:
            # Select via DMX
            ix = self.step_mode(len(self.dmx_addrs))
            dmx_addr = self.dmx_addrs[ix]
            panel_name = self.dmx_to_panel[dmx_addr]

        elif self.cm.modifiers[0]:
            # Select something from the business side
            ix = self.step_mode(len(self.business_panels))
            
            panel_num = self.business_panels[ix]
            panel_name = "%db" % panel_num
            dmx_addr = PANEL_MAP[panel_name]
        else:
            # Something from the party side
            ix = self.step_mode(len(self.party_panels))
            panel_num = self.party_panels[ix]
            panel_name = "%dp" % panel_num
            dmx_addr = PANEL_MAP[panel_name]

        self.cm.set_message("%s dmx=%s" % (panel_name, str(dmx_addr)))

    def update_at_progress(self, progress, new_loop, loop_instance):

        self.clear()

        # If at the beginning of the loop, we don't need to do anything
        if progress < 0.4:
            return

        # At the end of the loop we light up a panel

        # but which one?
        if self.cm.modifiers[1]:
            # Select via DMX
            ix = self.step_mode(len(self.dmx_addrs))
            addr = self.dmx_addrs[ix]

            panel_key = self.dmx_to_panel[addr]

            side = self.ss.business
            if panel_key[-1:]=="p":
                side = self.ss.party
            panel_num = int(panel_key[:-1])

            self.panel_name = panel_key

        elif self.cm.modifiers[0]:
            # Select something from the business side
            ix = self.step_mode(len(self.business_panels))
            panel_num = self.business_panels[ix]
            side = self.ss.business
        else:
            # Something from the party side
            ix = self.step_mode(len(self.party_panels))
            panel_num = self.party_panels[ix]
            side = self.ss.party

        side.set_cell(panel_num, self.white)
