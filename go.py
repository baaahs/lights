#!/usr/bin/env python2.7
import sys
import time
import traceback
import Queue
import threading
import signal
import random
import os

import sheep
import shows
import util
import controls_model
import touch_osc
import watchdog

from model.simulator import SimulatorModel
from model.mirror import MirrorModel

import config

# fail gracefully if cherrypy isn't available
_use_cherrypy = False
try:
    import cherrypy
    _use_cherrypy = True
except ImportError:
    print "WARNING: CherryPy not found; web interface disabled"

def _stacktraces(signum, frame):
    txt = []
    for threadId, stack in sys._current_frames().items():
        txt.append("\n# ThreadID: %s" % threadId)
        for filename, lineno, name, line in traceback.extract_stack(stack):
            txt.append('File: "%s", line %d, in %s' % (filename, lineno, name))
            if line:
                txt.append("  %s" % (line.strip()))

    print "\n".join(txt)

signal.signal(signal.SIGQUIT, _stacktraces)

def speed_interpolation(val):
    """
    Interpolation function to map OSC input into ShowRunner speed_x

    Input values range from 0.0 to 1.0
    input 0.5 => 1.0
    input < 0.5 ranges from 2.0 to 1.0
    input > 0.5 ranges from 1.0 to 0.5
    """
    if val == 0.5:
        return 1.0
    elif val < 0.5:
        return low_interp(val)
    else:
        return hi_interp(val)

low_interp = util.make_interpolater(0.0, 0.5, 2.0, 1.0)
hi_interp  = util.make_interpolater(0.5, 1.0, 1.0, 0.5)

watchdog = watchdog.Watchdog()

class ShowRunner(threading.Thread):
    def __init__(self, model, queue, cm, max_showtime=240):
        super(ShowRunner, self).__init__(name="ShowRunner")

        self.model = model
        self.mutable_model = sheep.make_mutable_sheep(model)

        self.queue = queue
        self.cm = cm

        # Tight coupling - yeah!!!!
        self.cm.add_listener(self)
        self.cm.show_runner = self        

        # Some cursors for show selection
        self.master_cursor = 0
        self.eo_cursor = 0
        self.overlay_cursor = 0

        self.running = True
        self.max_show_time = max_showtime
        self.show_runtime = 0

        # map of names -> show ctors
        self.shows = dict(shows.load_shows())

        # But now let's sort that into more useful lists based on
        # meta data
        self.master_shows = []
        self.overlay_shows = []
        self.eo_shows = []
        self.random_eligible_shows = []
        for name in self.shows:
            _class = self.shows[name]

            # Overlays are ONLY overlays            
            if hasattr(_class, "show_type"):
                if _class.show_type == "overlay":
                    self.overlay_shows.append(name)
                    continue

            # If a non-overlay is capable of controlling the eyes, then
            # it can be added to the eyes only list
            if hasattr(_class, "controls_eyes") and _class.controls_eyes:
                self.eo_shows.append(name)

            # If a show doesn't want to be added to the master list,
            # it has to say that it is an eyes only show
            if hasattr(_class, "show_type") and _class.show_type != "master":
                continue

            # Add it to the master list
            self.master_shows.append(name)

            ok_for_random = True
            if hasattr(_class, "ok_for_random"):
                ok_for_random = _class.ok_for_random

            if ok_for_random:
                self.random_eligible_shows.append(name)


        # Sort all these lists
        self.master_shows = sorted(self.master_shows)
        self.overlay_shows = sorted(self.overlay_shows)
        self.eo_shows = sorted(self.eo_shows)

        # Print them to the console for debugging
        print "Master shows: %s" % str(self.master_shows)
        print "Eyes Only shows: %s" % str(self.eo_shows)
        print "Overlay shows: %s" % str(self.overlay_shows)
        print "Random eligible shows: %s" % str(self.random_eligible_shows)

        self.randseq = self.random_show_name()

        # current show object & frame generator
        self.show = None
        self.framegen = None

        # The eyeShow is just like a show, except it can be None and it doesn't
        # automatically change when the base show changes. 
        self.eo_model = sheep.make_eyes_only_sheep(self.mutable_model)
        self.eo_show = None
        self.eo_framegen = None

        # And then ALSO an overlay show - OMG, so many shows!
        # This uses .model, the unmuted version
        self.overlay_show = None
        self.overlay_framegen = None

        # current show parameters

        # show speed multiplier - ranges from 0.5 to 2.0
        # 1.0 is normal speed
        # lower numbers mean faster speeds, higher is slower
        self.speed_x = 1.0

        self._push_master_names()
        self._push_eo_names()
        self._push_overlay_names()
        self.cm.set_max_time(self.max_show_time)

        self.force_muted = False


    def random_show_name(self):
        """
        Return an infinite sequence of randomized show names
        Remembers the last 'norepeat' items to avoid replaying shows too soon
        Norepeat defaults to 1/3 the size of the sequence
        """
        seq = self.random_eligible_shows

        norepeat=int(len(seq)/3)
        if norepeat < 1:
            norepeat = 1

        seen = []
        while True:
            n = random.choice(seq)
            while n in seen:
                n = random.choice(seq)
            seen.append(n)
            while len(seen) >= norepeat:
                seen.pop(0)
            yield n

    def control_speed_changed(self):
        print "Setting default show speed to %f" % self.cm.speed_multi

        # speed_x is opposite of speedMulti, so we have to invert speedMulti
        self.speed_x = 1.0 / self.cm.speed_multi

    def control_max_time_changed(self):
        self.max_show_time = int(self.cm.max_time)

    # We multiplex this to the models rather than making them listeners
    # because there are so many other things they won't care about so
    # let's not waste the time with those
    def control_brightness_changed(self, val):
        self.model.both.set_brightness(val)
        self.model.party.set_brightness(val)
        self.model.business.set_brightness(val)
        self.model.party_eye.set_brightness(val)
        self.model.business_eye.set_brightness(val)


    def status(self):
        if self.running:
            return "Running: %s (%d seconds left)" % (self.show.name, self.max_show_time - self.show_runtime)
        else:
            return "Stopped"

    def check_queue(self):
        msgs = []
        try:
            while True:
                m = self.queue.get_nowait()
                if m:
                    msgs.append(m)

        except Queue.Empty:
            pass

        if msgs:
            for m in msgs:
                self.process_command(m)

    def process_command(self, msg):
        if isinstance(msg,basestring):
            if msg == "shutdown":
                self.running = False
                print "ShowRunner shutting down"
            elif msg == "clear":
                self.clear()
                time.sleep(2)
            elif msg.startswith("run_show:"):
                self.running = True
                show_name = msg[9:]
                self.next_show(show_name)
            elif msg.startswith("inc runtime"):
                self.max_show_time = int(msg.split(':')[1])

        elif isinstance(msg, tuple):
            # osc message
            # ('/1/command', [value])
            try:
                print "OSC:", msg

                (addr,val) = msg
                addr = addr.split('/z')[0]
                val = val[0]
                assert addr[0] == '/'

                (ns, cmd) = addr[1:].split('/')
                if ns == '1':
                    # control command
                    if cmd == 'next':
                        self.next_show()
                    elif cmd == 'previous':
                        if self.prev_show:
                            self.next_show(self.prev_show.name)
                    elif cmd == 'speed':
                        self.speed_x = speed_interpolation(val)
                        print "setting speed_x to:", self.speed_x

                    pass
                elif ns == '2':
                    # show command
                    if self.show_params:
                        self.show.set_param(cmd, val)
            except ValueError:
                # When we get addresses with multiple path elements
                # from TouchOSC things go badly in the above code,
                # thus we ignore them.
                pass
            except IndexError:
                # When we get addresses with multiple path elements
                # from TouchOSC things go badly in the above code,
                # thus we ignore them.
                pass

        else:
            print "ignoring unknown msg:", str(msg)

    def clear(self):
        self.model.both.clear()


    def next_show(self, name=None):
        s = None
        if name:
            if name in self.shows:
                s = self.shows[name]

                if hasattr(s, "show_type") and s.show_type == "eyes_only":
                    self.next_eo_show(name)
                    return
                    
            else:
                print "unknown show:", name

        if not s:
            print "choosing random show"
            name = self.randseq.next()
            s = self.shows[name]

        self.clear()
        self.prev_show = self.show

        self.show = s(self.mutable_model)
        print "next show:" + self.show.name
        self.framegen = self.show.next_frame()
        # self.show_params = hasattr(self.show, 'set_param')
        # if self.show_params:
        #     print "Show can accept OSC params!"

        if hasattr(self.show, "handles_colorized"):
            self.model.party.handle_colorized = not self.show.handles_colorized
            self.model.business.handle_colorized = not self.show.handles_colorized
            self.model.both.handle_colorized = not self.show.handles_colorized
        else:
            self.model.party.handle_colorized = True
            self.model.business.handle_colorized = True            
            self.model.both.handle_colorized = True

        self.show_runtime = 0

        # Don't worry about whether a show can _actually_ accept control parameters
        # or not. Just call them a listener and if they don't accept things then the
        # exceptions will get surpressed
        self.cm.del_listener(self.prev_show)
        self.cm.add_listener(self.show)
        try:
            self.show.set_controls_model(self.cm)
        except AttributeError:
            pass

        try:
            self.show.control_refreshAll()
        except AttributeError:
            pass

        self.cm.set_master_name(name)
        self.cm.set_message("[%s]" % name)


    def next_eo_show(self, name):
        """
        Set the next eyes only show which has later access than the base show
        to the eyes models. Because it is valid to set a None show, the name is
        is always required here.
        """

        show_constructor = None
        if name:
            show_constructor = self.shows[name]

        if not show_constructor:
            # Clear any existing show
            if self.eo_show:
                self.cm.del_listener(self.eo_show)

            self.eo_show = None
            self.eo_framegen = None
            name = "Off"
        else:
            self.eo_show = show_constructor(self.eo_model)
            self.eo_framegen = self.eo_show.next_frame()

            self.cm.add_listener(self.eo_show)
            try:
                self.eo_show.set_controls_model(self.cm)
            except AttributeError:
                pass

            try:
                self.eo_show.control_refreshAll()
            except AttributeError:
                pass

        self.cm.set_eo_name(name)


    #######
    # Interface from controls_model 
    def move_master_cursor(self, delta):
        self.master_cursor += delta
        if self.master_cursor > len(self.master_shows) - 1:
            self.master_cursor = len(self.master_shows) - 1
        if self.master_cursor < 0:
            self.master_cursor = 0

        self._push_master_names()

    def select_master_random(self):
        self.next_show()

    def select_master(self, index):
        ix = self.master_cursor + index
        if ix > len(self.master_shows) - 1:
            print "Index out of range for master show. Ignoring"
            return

        name = self.master_shows[ix]
        self.next_show(name)


    def move_eo_cursor(self, delta):
        self.eo_cursor += delta
        if self.eo_cursor > len(self.eo_shows) - 1:
            self.eo_cursor = len(self.eo_shows) - 1
        if self.eo_cursor < 0:
            self.eo_cursor = 0

        self._push_eo_names()

    def eo_off(self):
        self.next_eo_show(None)

    def select_eo(self, index):
        ix = self.eo_cursor + index
        if ix > len(self.eo_shows) - 1:
            print "Index out of range for eo show. Ignoring"
            return

        name = self.eo_shows[ix]
        self.next_eo_show(name)


    def move_overlay_cursor(self, delta):
        self.overlay_cursor += delta
        if self.overlay_cursor > len(self.overlay_shows) - 1:
            self.overlay_cursor = len(self.overlay_shows) - 1
        if self.overlay_cursor < 0:
            self.overlay_cursor = 0

        self._push_overlay_names()

    def start_overlay(self, index):
        ix = self.overlay_cursor + index
        if ix > len(self.overlay_shows) - 1:
            print "Index out of range for overlay show. Ignoring"
            return

        name = self.overlay_shows[ix]
        print "Start overlay show %s" % name

        # Mute the mutable model
        self._set_model_muted(True)


        show_constructor = self.shows[name]

        self.overlay_show = show_constructor(self.model)
        self.overlay_framegen = self.overlay_show.next_frame()

        try:
            self.overlay_show.set_controls_model(self.cm)
        except AttributeError:
            pass

        try:
            self.overlay_show.control_refreshAll()
        except AttributeError:
            pass



    def stop_overlay(self, index):
        ix = self.overlay_cursor + index
        if ix > len(self.overlay_shows) - 1:
            print "Index out of range for overlay show. Ignoring"
            return

        name = self.overlay_shows[ix]
        print "Stopping overlay show %s" % name

        # Unmute the mutable model
        if not self.force_muted:
            self._set_model_muted(False)

        # This should sufficiently make them go away
        self.overlay_show = None
        self.overlay_framegen = None

    def _set_model_muted(self, val):
        self.mutable_model.both.muted = val
        self.mutable_model.party.muted = val
        self.mutable_model.business.muted = val
        self.mutable_model.party_eye.muted = val
        self.mutable_model.business_eye.muted = val

    def _push_master_names(self):
        self.cm.set_master_names(self.master_shows[self.master_cursor:])

    def _push_eo_names(self):
        self.cm.set_eo_names(self.eo_shows[self.eo_cursor:])

    def _push_overlay_names(self):
        self.cm.set_overlay_names(self.overlay_shows[self.overlay_cursor:])

    #######
    # For the web

    def set_force_mute(self, muted):
        self.force_muted = muted

        if not muted and self.overlay_show:
            # An overlay is running, don't unmute things underneath it
            return

        self._set_model_muted(muted)


    #######

    def get_next_frame(self):
        "return a delay or None"
        try:
            return self.framegen.next()
        except StopIteration:
            return None

    def get_next_eo_frame(self):
        try:
            return self.eo_framegen.next()
        except StopIteration:
            return None

    def get_next_overlay_frame(self):
        try:
            return self.overlay_framegen.next()
        except StopIteration:
            return None

    def run(self):
        if not (self.show and self.framegen):
            self.next_show()

        next_frame_at = 0.0
        next_eo_frame_at = 0.0
        next_overlay_frame_at = 0.0

        show_started_at = time.time()
        while self.running:
            try:
                # Indicate that we are still alive...
                watchdog.ping()

                self.check_queue()
                start = time.time()

                if start >= next_frame_at:
                    #print "%f next frame" % start
                    # ZOMG, gotta get a new show from
                    d = self.get_next_frame()

                    # If they give us an advisory time, we will record it, otherwise
                    # we will keep asking for frames as quickly as we can
                    if d:
                        next_frame_at = time.time() + (d * self.speed_x)

                else:
                    #print "%f not yet" % start
                    d = False

                if start >= next_eo_frame_at and self.eo_framegen:
                    deo = self.get_next_eo_frame()

                    if deo:
                        next_eo_frame_at = time.time() + (deo * self.speed_x)

                if start >= next_overlay_frame_at and self.overlay_framegen:
                    doverlay = self.get_next_overlay_frame()

                    if doverlay:
                        next_overlay_frame_at = time.time() + (doverlay * self.speed_x)

                # Always output things, because they could have
                # changed by UI controls for instance
                if self.overlay_show is not None or self.force_muted:
                    self.model.party_eye.go()
                    self.model.business_eye.go()
                    self.model.both.go()
                else:
                    self.mutable_model.party_eye.go()
                    self.mutable_model.business_eye.go()
                    self.mutable_model.both.go()

                # Maybe this show is done?
                if start - show_started_at > self.max_show_time:
                    print "max show time elapsed, changing shows"
                    self.next_show()
                    next_frame_at = show_started_at = time.time()
                else:
                    # Not a new show yet, so we are going to pause, but never
                    # more that .023s which yields roughly the max DMX framerate
                    # of 44hz

                    now = time.time()
                    to_sleep = 0.023 
                    until_next = next_frame_at - now
                    until_next_eo = next_eo_frame_at - now
                    until_next_overlay = next_overlay_frame_at - now

                    if until_next_eo < until_next and until_next_eo > 0.001:
                        until_next = until_next_eo

                    if until_next_overlay < until_next and until_next_overlay > 0.001:
                        until_next = until_next_overlay

                    if until_next < to_sleep and until_next > 0.001:
                        to_sleep = until_next

                    #print "toSleep = %s" % str(toSleep)
                    time.sleep(to_sleep)

            except Exception:
                print "unexpected exception in show loop!"
                traceback.print_exc()
                self.next_show()

def osc_listener(q, cm, port=5700):
    "Create the OSC Listener thread"
    import osc_serve

    listen_address=('0.0.0.0', port)
    print "Starting OSC Listener on %s:%d" % listen_address
    osc = osc_serve.create_server(listen_address, q, cm)
    st = threading.Thread(name="OSC Listener", target=osc.serve_forever)
    st.daemon = True
    return st, osc

def bonjour_server(name="Sheep", port=5700):
    "Create the bonjour server, returns (thread, shutdownEvent)"
    from lib import bonjour
    shutdownEvent = threading.Event()
    st = threading.Thread(name="Bonjour broadcaster", target=bonjour.serve_forever, args=(name, port, shutdownEvent))
    return (st, shutdownEvent)

def start_touch_osc(inst):
    "Spawn a thread which will run the bonjour discovery of TouchOSC instances on the local network"
    st = threading.Thread(name="TouchOSC", target=inst.serve_forever)
    st.daemon = True
    return st


class SheepServer(object):
    def __init__(self, sheep_model, args):
        self.args = args
        self.sheep_model = sheep_model

        self.queue = Queue.LifoQueue()
        self.controls_model = controls_model.ControlsModel()

        # All of the sheep_model elements need to know about the
        # controls_model for various reasons, so we inject it here
        # into all of them
        self.sheep_model.party.cm = self.controls_model
        self.sheep_model.business.cm = self.controls_model
        self.sheep_model.both.cm = self.controls_model
        self.sheep_model.party_eye.cm = self.controls_model
        self.sheep_model.business_eye.cm = self.controls_model

        # We _might_ want to make the eyes listeners so they can update
        # DMX values that aren't otherwise mapped, although our hope is to
        # map all functions, so maybe we won't do that just yet. (We did have to
        # do it for IG3 so we could get the "random DMX value" functionality passed
        # directly into the pixel array)

        self.runner = None

        self.osc_thread = None

        self.bonjour_thread = None
        self.bonjour_exit_flag = None

        self.running = False
        self._create_services()

    def _create_services(self):
        "Create sheep services, trying to fail gracefully on missing dependencies"
        # Bonjour advertisement
        # XXX can this also advertise the web interface?
        # XXX should it only advertise services that exist?
        try:
            (t, flag) = bonjour_server(name="Sheep@" + util.get_hostname("unknown"))
            self.bonjour_thread = t
            self.bonjour_exit_flag = flag
        except Exception, e:
            print "WARNING: Can't create bonjour service"
            print e

        # OSC listener
        try:
            self.osc_thread, self.osc_s = osc_listener(self.queue, self.controls_model)
        except Exception, e:
            print "WARNING: Can't create OSC listener"
            print e

        try:
            self.touch_osc = touch_osc.TouchOSC(self.controls_model, self.osc_s)
            self.touch_osc_thread = start_touch_osc(self.touch_osc)
        except Exception, e:
            print "WARNING: Can't create TouchOSC watcher"
            print e

        # Show runner
        self.runner = ShowRunner(self.sheep_model, self.queue, self.controls_model, args.max_time)
        if args.shows:
            print "setting show:", args.shows[0]
            self.runner.next_show(args.shows[0])

    def start(self):
        if self.running:
            print "start() called, but sheep is already running!"
            return

        try:
            if self.bonjour_thread:
                self.bonjour_thread.start()

            if self.osc_thread:
                self.osc_thread.start()

            if self.touch_osc_thread:
                self.touch_osc_thread.start()

            self.runner.start()

            self.running = True
        except Exception, e:
            print "Exception starting sheep!"
            traceback.print_exc()

    def stop(self):
        watchdog.stop()
        if self.running: # should be safe to call multiple times
            try:
                if self.bonjour_thread:
                    print "Setting bonjour exit flag"
                    self.bonjour_exit_flag.set()

                # OSC listener is a daemon thread so it will clean itself up

                # ShowRunner is shut down via the message queue
                self.queue.put("shutdown")

                self.running = False
            except Exception, e:
                print "Exception stopping sheep!"
                traceback.print_exc()

    def go_headless(self):
        "Run without the web interface"
        print "Running without web interface"
        try:
            while True:
                time.sleep(999) # control-c breaks out of time.sleep
        except KeyboardInterrupt:
            print "Exiting on keyboard interrupt"

        self.stop()

    def go_web(self):
        "Run with the web interface"
        import cherrypy
        from web import SheepyWeb

        cherrypy.engine.subscribe('stop', self.stop)

        port = 9990
        _dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "web", "static"))
        print _dir

        config = {
            'global': {
                'server.socket_host' : '0.0.0.0',
                'server.socket_port' : port,
                # 'engine.timeout_monitor.on' : True,
                # 'engine.timeout_monitor.frequency' : 240,
                # 'response.timeout' : 60*15
            },

            '/index': {
                'tools.staticfile.on': True,
                'tools.staticfile.filename': os.path.join(_dir, "index.html")
            },

            '/static': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': _dir
            }
        }

        # this method blocks until KeyboardInterrupt
        cherrypy.quickstart(SheepyWeb(self.queue, self.runner, self.controls_model, watchdog),
                            '/',
                            config=config)


if __name__=='__main__':

    config.load()

    sim_host = ""
    if config.has("sim_host"):
        sim_host = config.get("sim_host")

    sim_port = 4444
    if config.has("sim_port"):
        sim_port = config.get("sim_port")

    cfg_mode = None
    if config.has("mode"):
        cfg_mode = config.get("mode")

    import argparse
    parser = argparse.ArgumentParser(description='Baaahs Light Control')

    parser.add_argument('--max-time', type=float, default=float(300),
                        help='Maximum number of seconds a show will run (default 300)')

    parser.add_argument('--simulator',dest='simulator',action='store_true')
    parser.add_argument('--host',dest='sim_host', type=str, default=sim_host, help="Hostname or ip for simulator")
    parser.add_argument('--port',dest='sim_port', type=int, default=sim_port, help="Port for simulator")

    parser.add_argument('--universe',dest='universe', type=int, default=0, help="DMX universe")

    parser.add_argument('--mirror',dest='mirror',action='store_true', help="Mirror to both sim and OLA")

    parser.add_argument('--debug',dest='debug',action='store_true')

    parser.add_argument('--list', action='store_true', help='List available shows')
    parser.add_argument('shows', metavar='show_name', type=str, nargs='*',
                        help='name of show (or shows) to run')

    args = parser.parse_args()

    if args.list:
        print "Available shows:"
        print ', '.join([s[0] for s in shows.load_shows()])
        sys.exit(0)



    if args.mirror or cfg_mode == "mirror":
        from model.ola_model import OLAModel
        print "Mirroring to both OLA universe %d and sim %s:%d" % (args.universe, args.sim_host, args.sim_port)
        sim = SimulatorModel(args.sim_host, port=args.sim_port, debug=args.debug)
        ola = OLAModel(512, universe=args.universe)
        model = MirrorModel(sim, ola)
    elif args.simulator or cfg_mode == "simulator":
        # sim_host = "localhost"
        print "Using SheepSimulator at %s:%d" % (args.sim_host, args.sim_port)
        model = SimulatorModel(args.sim_host, port=args.sim_port, debug=args.debug)
    else:
        from model.ola_model import OLAModel
        print "Using OLA model universe=%d" % args.universe
        model = OLAModel(512, universe=args.universe)

    sheep_sides = sheep.make_sheep(model)
    app = SheepServer(sheep_sides, args)
    try:
        app.start() # start related service threads

        # enter main blocking event loop
        if _use_cherrypy:
            app.go_web()
        else:
            app.go_headless()

    except Exception, e:
        print "Unhandled exception running sheep!"
        traceback.print_exc()
    finally:
        app.stop()
