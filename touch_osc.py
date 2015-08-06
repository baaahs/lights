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

    svcName = None
    svcNamesToAddr = {}

    def __init__(self, cm, server):
        self.client = OSCMultiClient(server=server)
        self.cm = cm
        self.cm.addListener(self)

    def control_colorChanged(self):
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

    def control_eyeChanged(self, isParty):
        try:
            tilt = self.cm.pEyeTilt
            pan = self.cm.pEyePan
            xyEnable = self.cm.pEyeXYEnable * 1.0
            addrBase = "/eyes/p"

            if not isParty:
                tilt = self.cm.bEyeTilt
                pan = self.cm.bEyePan
                xyEnable = self.cm.bEyeXYEnable * 1.0
                addrBase = "/eyes/b"

            self._send1(addrBase + "Tilt", tilt)
            self._send1(addrBase + "Pan", pan)
            self._send1(addrBase + "XYEnable", xyEnable)

            if isParty:
                self._send1("/eyes/dimmer/1", self.cm.pDimmer)
            else:
                self._send1("/eyes/dimmer/2", self.cm.bDimmer)

            self._send1("/eyes/skyPos", 1.0 * self.cm.eyeSkyPos)
        except Exception, e:
            print e


    def control_eyeMovementLockChanged(self):
        print "control_eyeMovementLockChanged ..."
        if self.cm.eyeMovementLocked:
            self._send1("/eyes/movementLock", 1.0)
        else:
            self._send1("/eyes/movementLock", 0.0)

    def control_eyeColorChanged(self):
        if self.cm.colorMix:
            self._send1("/eyes/colorMix", 1.0)
        else:
            self._send1("/eyes/colorMix", 0.0)

        self._send1("/eyes/colorCycle", self.cm.colorCycleSpeed)

        if self.cm.pColorEnable:
            self._send1("/eyes/pColorEnable", 1.0)
        else:
            self._send1("/eyes/pColorEnable", 0.0)

        if self.cm.bColorEnable:
            self._send1("/eyes/bColorEnable", 1.0)
        else:
            self._send1("/eyes/bColorEnable", 0.0)

    def control_chosenColorChanged(self, cIx):

        addr = "/main/color/%d/" % cIx
        for i in range(1,8):
            a = "%s%d" % (addr, i)
            if self.cm.chosenColorsIx[cIx] == i:
                self._send1(a, 1.0)
            else:
                self._send1(a, 0.0)

        for i in range(101,108):
            a = "%s%d" % (addr, i)
            if self.cm.chosenColorsIx[cIx] == i:
                self._send1(a, 1.0)
            else:
                self._send1(a, 0.0)

    def control_speedChanged(self):
        pos = self.cm.speedMulti - 1.0
        self._send1("/main/speed/changeRel", pos)
        self._send1("/main/speed/lblMulti", "%.2fx" % self.cm.speedMulti)
        self._send1("/main/speed/lblBPM", "%.1f bpm" % (120.0 * self.cm.speedMulti))


    def control_intensifiedChanged(self):
        self._send1("/main/intensified", self.cm.intensified)

    def control_colorizedChanged(self):
        self._send1("/main/colorized", self.cm.colorized)

    def control_modifiersChanged(self):
        for ix,val in enumerate(self.cm.modifiers):
            addr = "/main/modifier/%d" % ix
            if val:
                self._send1(addr, 1.0)
            else:
                self._send1(addr, 0.0)

    def control_refreshAll(self):
        self._sendAllState()

    def _send1(self, addr, txt):
        msg = OSCMessage(addr)
        msg.append(txt)
        print "Send %s" % msg
        try:
            self.client.send(msg)
        except Exception, e:
            traceback.print_exc()


    def _sendAllState(self):
        self.control_colorChanged()
        self.control_eyeMovementLockChanged()
        self.control_eyeChanged(True)
        self.control_eyeChanged(False)
        self.control_chosenColorChanged(0)
        self.control_chosenColorChanged(1)
        self.control_intensifiedChanged()
        self.control_colorizedChanged()


    def serve_forever(self):
        print "TouchOSC starting serve_forever"
        browse_sdRef = pybonjour.DNSServiceBrowse(regtype = "_osc._udp", callBack = self.browse_callback)

        try:
            try:
                while True:
                    print "TouchOSC selecting on browse_sd"
                    ready = select.select([browse_sdRef], [], [])
                    print "Select!"
                    if browse_sdRef in ready[0]:
                        pybonjour.DNSServiceProcessResult(browse_sdRef)
            except KeyboardInterrupt:
                pass
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

                self.svcNamesToAddr[self.svcName] = addr

                self.client.setOSCTarget( addr )

                self._sendAllState()
            else:
                print "Ignoring this because it's not a TouchOSC client"


    def browse_callback(self, sdRef, flags, interfaceIndex, errorCode, serviceName,
                        regtype, replyDomain):
        if errorCode != pybonjour.kDNSServiceErr_NoError:
            return

        if not (flags & pybonjour.kDNSServiceFlagsAdd):
            print 'Service removed %s' % serviceName
            if serviceName in self.svcNamesToAddr:
                addr = self.svcNamesToAddr[serviceName]
                self.client.delOSCTarget( addr )
                del self.svcNamesToAddr[serviceName]

            return

        print 'Service added; resolving'
        print 'serviceName=%s' % serviceName
        # This is an admittedly kind of hookey way to get the key to the resolve
        # function, but I'm not sure of a better one at the moment
        self.svcName = serviceName

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

