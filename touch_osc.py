#!/usr/bin/env python2.7
import sys
import select
import pybonjour

# import time
# import traceback
# import Queue
# import threading
# import signal

# import sheep
# import shows
# import util

import optparse
import threading
import traceback
import controls_model as controls

from collections import defaultdict

from lib.OSC import *
from lib.OSC import _readString, _readFloat, _readInt



class TouchOSC(object):
    """
    This class handles pushing changes in the controls model out to any 
    discovered TouchOSC clients. As such, it is the second half of the roundtrip
    where a human uses a phone to change a value, which updates the internal
    model, which will then update that user's phone.
    """
    resolved = []
    timeout = 5

    svc_name = None
    svc_names_to_addr = {}

    def __init__(self, cm, server):
        self.client = OSCMultiClient(server=server)
        self.cm = cm
        self.cm.add_listener(self)

    def control_color_changed(self):
        print "Color changed in TouchOSC"
        
        # Send 6 update messages for the color labels
        self._send1("/color/lblRed", str(self.cm.color.r))
        self._send1("/color/lblGreen", str(self.cm.color.g))
        self._send1("/color/lblBlue", str(self.cm.color.b))
        self._send1("/color/lblHue", str(self.cm.color.h))
        self._send1("/color/lblSat", str(self.cm.color.s))
        self._send1("/color/lblVal", str(self.cm.color.v))

        self._send1("/color/red", float(self.cm.color.r) / 255.0)
        self._send1("/color/green", float(self.cm.color.g) / 255.0)
        self._send1("/color/blue", float(self.cm.color.b) / 255.0)
        self._send1("/color/hue", self.cm.color.h)
        self._send1("/color/sat", self.cm.color.s)
        self._send1("/color/val", self.cm.color.v)

    def control_eye_changed(self, is_party):
        try:
            pos = self.cm.p_eye_pos
            xy_enable = float(self.cm.p_eye_xy_enable)
            addr_base = "/eyes/p"

            if not is_party:
                pos = self.cm.b_eye_pos
                xyEnable = float(self.cm.b_eye_xy_enable)
                addr_base = "/eyes/b"

            self._send1(addr_base + "Tilt", pos[controls.TILT])
            self._send1(addr_base + "Pan", pos[controls.PAN])
            self._send1(addr_base + "XYEnable", xy_enable)

            if is_party:
                self._send1("/eyes/dimmer/1", self.cm.p_brightness)
            else:
                self._send1("/eyes/dimmer/2", self.cm.b_brightness)

            self._send1("/eyes/skyPos", float(self.cm.eye_sky_pos))
        except Exception, e:
            print e


    # def control_eyeMovementLock_changed(self):
    #     print "control_eyeMovementLock_changed ..."
    #     if self.cm.eyeMovementLocked:
    #         self._send1("/eyes/movementLock", 1.0)
    #     else:
    #         self._send1("/eyes/movementLock", 0.0)

    # def control_eyeColor_changed(self):
    #     if self.cm.colorMix:
    #         self._send1("/eyes/colorMix", 1.0)
    #     else:
    #         self._send1("/eyes/colorMix", 0.0)

    #     self._send1("/eyes/colorCycle", self.cm.colorCycleSpeed)

    #     if self.cm.pColorEnable:
    #         self._send1("/eyes/pColorEnable", 1.0)
    #     else:
    #         self._send1("/eyes/pColorEnable", 0.0)

    #     if self.cm.bColorEnable:
    #         self._send1("/eyes/bColorEnable", 1.0)
    #     else:
    #         self._send1("/eyes/bColorEnable", 0.0)

    def control_chosen_color_changed(self, cIx):

        addr = "/main/color/%d/" % cIx
        for i in range(1,8):
            a = "%s%d" % (addr, i)
            if self.cm.chosen_colors_ix[cIx] == i:
                self._send1(a, 1.0)
            else:
                self._send1(a, 0.0)

        for i in range(101,108):
            a = "%s%d" % (addr, i)
            if self.cm.chosen_colors_ix[cIx] == i:
                self._send1(a, 1.0)
            else:
                self._send1(a, 0.0)

    def control_speed_changed(self):
        pos = self.cm.speed_multi - 1.0
        self._send1("/main/speed/changeRel", pos)
        self._send1("/main/speed/lblMulti", "%.2fx" % self.cm.speed_multi)
        self._send1("/main/speed/lblBPM", "%.1f bpm" % (120.0 * self.cm.speed_multi))


    def control_intensified_changed(self):
        self._send1("/main/intensified", self.cm.intensified)

    def control_colorized_changed(self):
        self._send1("/main/colorized", self.cm.colorized)

    def control_brightness_changed(self, val):
        self._send1("/main/brightness", val)

    def control_modifiers_changed(self):
        for ix,val in enumerate(self.cm.modifiers):
            addr = "/main/modifier/%d" % ix
            if val:
                self._send1(addr, 1.0)
            else:
                self._send1(addr, 0.0)

    def control_eyes_mode_changed(self):
        v = 0
        if self.cm.eyes_mode == controls.EYES_MODE_DISCO:
            v = 1

        self._send1("/eyes/mode/disco", float(v))
        self._send1("/eyes/disco/mix/visible", v)
        self._send1("/eyes/disco/mixLbl/visible", v)
        self._send1("/eyes/disco/cycleSpeed/visible", v)
        self._send1("/eyes/disco/cycleSpeedLbl/visible", v)
        self._send1("/eyes/disco/brightness/visible", v)

        self._send1("/eyes/disco/colorWhite/visible", v)
        self._send1("/eyes/disco/colorRed/visible", v)
        self._send1("/eyes/disco/colorOrange/visible", v)
        self._send1("/eyes/disco/colorAquamarine/visible", v)
        self._send1("/eyes/disco/colorDeepGreen/visible", v)
        self._send1("/eyes/disco/colorLightGreen/visible", v)
        self._send1("/eyes/disco/colorLavender/visible", v)
        self._send1("/eyes/disco/colorPink/visible", v)
        self._send1("/eyes/disco/colorYellow/visible", v)
        self._send1("/eyes/disco/colorMagenta/visible", v)
        self._send1("/eyes/disco/colorCyan/visible", v)
        self._send1("/eyes/disco/colorCTO2/visible", v)
        self._send1("/eyes/disco/colorCTO1/visible", v)
        self._send1("/eyes/disco/colorCTB/visible", v)
        self._send1("/eyes/disco/colorBlue/visible", v)

        self._send1("/eyes/disco/noEffect/visible", v)
        self._send1("/eyes/disco/noEffectLbl/visible", v)
        self._send1("/eyes/disco/effectSpeed/visible", v)
        self._send1("/eyes/disco/effectSpeedLbl/visible", v)
        self._send1("/eyes/disco/effect/visible", v)

        v = 0
        if self.cm.eyes_mode == controls.EYES_MODE_HEADLIGHTS:
            v = 1

        self._send1("/eyes/mode/headlights", float(v))
        self._send1("/eyes/hmode/normal/visible", v)
        self._send1("/eyes/hmode/normalLbl/visible", v)
        self._send1("/eyes/hmode/left/visible", v)
        self._send1("/eyes/hmode/leftLbl/visible", v)
        self._send1("/eyes/hmode/both/visible", v)
        self._send1("/eyes/hmode/bothLbl/visible", v)
        self._send1("/eyes/hmode/right/visible", v)
        self._send1("/eyes/hmode/rightLbl/visible", v)
        self._send1("/eyes/hmode/spotLbl/visible", v)

        v = 0
        if self.cm.eyes_mode == controls.EYES_MODE_SHOW:
            v = 1

        self._send1("/eyes/mode/show", float(v))
        self._send1("/eyes/target/up/visible", v)
        self._send1("/eyes/target/upLbl/visible", v)
        self._send1("/eyes/target/down/visible", v)
        self._send1("/eyes/target/downLbl/visible", v)
        self._send1("/eyes/target/pnt/visible", v)
        self._send1("/eyes/target/pntLbl/visible", v)
        self._send1("/eyes/target/none/visible", v)
        self._send1("/eyes/target/noneLbl/visible", v)

        # Must enable xy for 2 different modes
        v = 0
        if self.cm.eyes_mode != controls.EYES_MODE_DISCO:
            v = 1

        self._send1("/eyes/target/xy/visible", v)

        # Don't need these anymore
        self._send1("/onetime/refresh/visible", 0)
        self._send1("/onetime/refreshLbl/visible", 0)

    def control_disco_color_changed(self):
        v = 0.0
        if self.cm.disco_mix:
            v = 1.0

        self._send1("/eyes/disco/mix", v)
        self._send1("/eyes/disco/cycleSpeed", self.cm.disco_cycle_speed)

        # Don't (can't) update anything about the color selection


    def control_disco_brightness_changed(self):
        self._send1("/eyes/disco/brightness", self.cm.disco_brightness)

    def control_disco_effect_changed(self):
        if self.cm.disco_effect == 0:
            # Because the effect control is mutually exclusive, we can toggle
            # on a known spot, and then toggle it off to clear it
            self._send1("/eyes/disco/effect/1/1", 1.0)
            self._send1("/eyes/disco/effect/1/1", 0.0)

            self._send1("/eyes/disco/noEffect", 1.0)

        else:
            self._send1("/eyes/disco/noEffect", 0.0)

            y = (self.cm.disco_effect / 8) + 1
            x = self.cm.disco_effect % 8

            if x == 0:
                x = 8
                y -= 1

            self._send1("/eyes/disco/effect/%d/%d" % (x,y), 1.0)

        self._send1("/eyes/disco/effectSpeed", self.cm.disco_effect_speed)

    def control_headlights_mode_changed(self):
        v = 0.0
        if self.cm.headlights_mode == controls.HEADLIGHTS_MODE_NORMAL:
            v = 1.0
        self._send1("/eyes/hmode/normal", v);

        v = 0.0
        if self.cm.headlights_mode == controls.HEADLIGHTS_MODE_LEFT:
            v = 1.0
        self._send1("/eyes/hmode/left", v);

        v = 0.0
        if self.cm.headlights_mode == controls.HEADLIGHTS_MODE_BOTH:
            v = 1.0
        self._send1("/eyes/hmode/both", v);

        v = 0.0
        if self.cm.headlights_mode == controls.HEADLIGHTS_MODE_RIGHT:
            v = 1.0
        self._send1("/eyes/hmode/right", v);

    def control_show_target_mode_changed(self):
        v = 0.0
        if self.cm.show_target_mode == controls.SHOW_TARGET_MODE_NONE:
            v = 1.0
        self._send1("/eyes/target/none", v);

        v = 0.0
        if self.cm.show_target_mode == controls.SHOW_TARGET_MODE_UP:
            v = 1.0
        self._send1("/eyes/target/up", v);

        v = 0.0
        if self.cm.show_target_mode == controls.SHOW_TARGET_MODE_DOWN:
            v = 1.0
        self._send1("/eyes/target/down", v);

        v = 0.0
        if self.cm.show_target_mode == controls.SHOW_TARGET_MODE_PNT:
            v = 1.0
        self._send1("/eyes/target/pnt", v);

    def control_master_names_changed(self):
        addr_base = "/shows/master/choice/%d/lbl"

        l = len(self.cm.master_names)
        for ix in range(0, 6):
            s = ""
            if ix < l:
                s = self.cm.master_names[ix]
            self._send1(addr_base % ix, s)

    def control_eo_names_changed(self):
        addr_base = "/shows/eo/choice/%d/lbl"

        l = len(self.cm.eo_names)
        for ix in range(0, 4):
            s = ""
            if ix < l:
                s = self.cm.eo_names[ix]
            self._send1(addr_base % ix, s)

    def control_overlay_names_changed(self):
        addr_base = "/shows/overlay/choice/%d/lbl"

        l = len(self.cm.overlay_names)
        for ix in range(0, 4):
            s = ""
            if ix < l:
                s = self.cm.overlay_names[ix]
            self._send1(addr_base % ix, s)            


    def control_master_name_changed(self):
        self._send1("/shows/master/name", self.cm.master_name)

    def control_eo_name_changed(self):
        self._send1("/shows/eo/name", self.cm.eo_name)


    def control_max_time_changed(self):
        _range = self.cm.time_limits[1] - self.cm.time_limits[0]
        scaled = (self.cm.max_time - self.cm.time_limits[0]) / _range

        if scaled > 1.0:
            scaled = 1.0

        minsf, mins = math.modf(self.cm.max_time / 60.0)
        secs = math.floor(self.cm.max_time - (60.0 * mins))

        self._send1("/shows/master/maxTime", scaled)
        self._send1("/shows/master/maxTimeLbl", "%dm %ds" % (int(mins), int(secs)))

    def control_message_changed(self):
        self._send1("/main/message", self.cm.message)



    def control_refresh_all(self):
        self._send_all_state()

    def _send1(self, addr, txt):
        msg = OSCMessage(addr)
        msg.append(txt)
        print "Send %s" % msg
        try:
            self.client.send(msg)
        except Exception, e:
            traceback.print_exc()


    def _send_all_state(self):
        self.control_color_changed()
        # self.control_eyeMovementLock_changed()
        # self.control_eye_changed(True)
        # self.control_eye_changed(False)
        self.control_chosen_color_changed(0)
        self.control_chosen_color_changed(1)
        self.control_intensified_changed()
        self.control_colorized_changed()
        self.control_modifiers_changed()
        self.control_brightness_changed(self.cm.brightness)
        self.control_eyes_mode_changed()

        self.control_disco_color_changed()
        self.control_disco_brightness_changed()
        self.control_disco_effect_changed()

        self.control_headlights_mode_changed()
        self.control_show_target_mode_changed()

        self.control_master_names_changed()
        self.control_eo_names_changed()
        self.control_overlay_names_changed()

        self.control_master_name_changed()
        self.control_eo_name_changed()

        self.control_max_time_changed()
        self.control_message_changed()

    def serve_forever(self):
        print "TouchOSC starting serve_forever"
        browse_sdRef = pybonjour.DNSServiceBrowse(regtype = "_osc._udp", callBack = self.browse_callback)

        try:
            # try:
                while True:
                    print "TouchOSC selecting on browse_sd"
                    ready = select.select([browse_sdRef], [], [])
                    print "Select!"
                    if browse_sdRef in ready[0]:
                        pybonjour.DNSServiceProcessResult(browse_sdRef)
            # except KeyboardInterrupt:
            #     pass
        finally:
            browse_sdRef.close()


    def resolve_callback(self, sdRef, flags, interfaceIndex, errorCode, fullname,
                         hosttarget, port, txtRecord):
        if errorCode == pybonjour.kDNSServiceErr_NoError:
            print 'Resolved service:'
            print '  fullname   =', fullname
            print '  hosttarget =', hosttarget
            print '  port       =', port            
            self.resolved.append(True)

            if "TouchOSC" in fullname:
                # yay! it's one of the things we were looking for
                addr = (hosttarget, port)
                print "Adding a TouchOSC client %s:%s" % addr

                self.svc_names_to_addr[self.svc_name] = addr

                self.client.setOSCTarget( addr )

                self._send_all_state()
            else:
                print "Ignoring this because it's not a TouchOSC client"


    def browse_callback(self, sdRef, flags, interfaceIndex, errorCode, serviceName,
                        regtype, replyDomain):
        if errorCode != pybonjour.kDNSServiceErr_NoError:
            return

        if not (flags & pybonjour.kDNSServiceFlagsAdd):
            print 'Service removed %s' % serviceName
            if serviceName in self.svc_names_to_addr:
                addr = self.svc_names_to_addr[serviceName]
                self.client.delOSCTarget( addr )
                del self.svc_names_to_addr[serviceName]

            return

        print 'Service added; resolving'
        print 'serviceName=%s' % serviceName
        # This is an admittedly kind of hookey way to get the key to the resolve
        # function, but I'm not sure of a better one at the moment
        self.svc_name = serviceName

        resolve_sdRef = pybonjour.DNSServiceResolve(0,
                                                    interfaceIndex,
                                                    serviceName,
                                                    regtype,
                                                    replyDomain,
                                                    self.resolve_callback)

        try:
            while not self.resolved:
                ready = select.select([resolve_sdRef], [], [], self.timeout)
                if resolve_sdRef not in ready[0]:
                    print 'Resolve timed out'
                    break
                pybonjour.DNSServiceProcessResult(resolve_sdRef)
            else:
                self.resolved.pop()
        finally:
            resolve_sdRef.close()


if __name__=='__main__':
    to = TouchOSC()

    to.serve_forever()

