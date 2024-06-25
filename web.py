import cherrypy
import time
import eyes
import eye_effect
import config

class SheepyWeb(object):
    def __init__(self, queue, runner, cm, watchdog):
        self.queue = queue
        self.runner = runner

        self.cm = cm
        self.watchdog = watchdog

        self.show_library = show_library = {}

        for name in runner.master_shows:
            show_library[name] = s = {
                'type': "master"
            }
            if name in runner.random_eligible_shows:
                s['random'] = True

        for name in runner.eo_shows:
            existing = show_library.get(name)
            if existing is None:
                show_library[name] = {
                    'type': "eyes_only",
                    'controls_eyes': True
                }
            else:
                existing['controls_eyes'] = True

        for name in runner.overlay_shows:
            show_library[name] = {
                'type': 'overlay'
            }


    @cherrypy.expose
    def clear_show(self):
        self.queue.put("clear")
        return "<a href='.'/>Back</a>"

    @cherrypy.expose
    def change_run_time(self, run_time=None):
        try:
            print("RUNTIME XXXXX:::: %s" % run_time)
            run_time = int(run_time)
            self.queue.put("inc runtime:%s"%run_time)
        except Exception as e:
            print("\n\nCRASH\n\n", e)
            #probably a string... do nothing!
            pass
        return "<a href='.'/>Back</a>"

    @cherrypy.expose
    def index_old(self):
        # set a no-cache header so the show status is up to date
        cherrypy.response.headers['Cache-Control'] = "no-cache, no-store, must-revalidate, max-age=0"
        cherrypy.response.headers['Expires'] = 0

        ret_html = "<h1></h1>"
        ret_html += "<p>" + self.runner.status() + "</p>"
        ret_html += "<b>Choose a show</b><ul>"

        for s in sorted(self.shows):
            ret_html += "<li><a href='run_show?show_name=%s' > %s</a>" % (s, s)
        ret_html += "<br><br><a href='clear_show' > CLEAR SHOW // STOP</a>"
        ret_html += """<br><br><h3>Set Show Cycle Time(seconds):<form name=change_run_time action='change_run_time'>
Seconds:<input type=text name=run_time value=60><input type=submit></form>
"""
        return(ret_html)

    @cherrypy.expose
    def run_show(self, show_name=None):
        if show_name:
            self.queue.put("run_show:"+show_name)
            print("setting show to:", show_name)
        else:
            print("didn't get a show name")

        # XXX otherwise the runner.status() method
        # hasn't had time to update
        time.sleep(0.2)
        raise cherrypy.HTTPRedirect("/")


    @cherrypy.expose
    def admin(self):
        raise cherrypy.HTTPRedirect("/static/admin.html")

    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def shows(self):
        return self.show_library

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def start_show(self):
        data = cherrypy.request.json
        name = data.get("name")
        print("Start show name='%s'" % name)

        self.runner.next_show(name=name)

        return {'ok': True}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def start_eo_show(self):
        data = cherrypy.request.json
        name = data.get("name")
        print("Start EO show name='%s'" % name)

        self.runner.next_eo_show(name=name)

        return {'ok': True}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def stop_eo_show(self):
        self.runner.next_eo_show(None)
        return {'ok': True}        

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def status(self):
        now = time.time()

        out = {
            'show': {
                'name': self.runner.show.name,
                'run_time': int(self.runner.show_runtime * 1000)
            },
            'message': self.cm.message,
            'max_time': int(self.runner.max_show_time * 1000),
            'reset_state': {
                'party': {
                    'mode': self.runner.model.party_eye.reset_mode,
                    'duration': int((now - self.runner.model.party_eye.reset_changed_at)* 1000)
                },
                'business': {
                    'mode': self.runner.model.business_eye.reset_mode,
                    'duration': int((now - self.runner.model.business_eye.reset_changed_at)* 1000)
                }
            }
        }
        if self.runner.eo_show is not None:
            out['eo_show'] = {
                'name': self.runner.eo_show.name
            }

        return out

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def effect_presets(self):
        out = []

        for e in self.cm.effects:
            out.append(e.as_json())

        return out

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def save_effect(self):
        data = cherrypy.request.json

        effect = eye_effect.EyeEffect(json=data)

        if self.cm.set_effect_preset(data.get("effect_index"), effect):
            out = {"ok": True}
        else:
            out = {"ok": False}

        return out

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def manual_eyes(self):
        data = cherrypy.request.json

        if not data.get("enabled"):
            # Done with manual mode
            self.runner.set_force_mute(False)
            return {"ok": True}

        # Make sure force mute is enabled
        self.runner.set_force_mute(True)

        print("Got data %s" % str(data))

        effect = None
        if data.get("effect"):
            effect = eye_effect.EyeEffect(json=data.get("effect"))
        x = data.get("x_pos")
        y = data.get("y_pos")
        z = data.get("z_pos")

        is_xyz = data.get("pos_is_xyz") or False

        dimmer = data.get("dimmer")
        color_pos = data.get("color_pos")

        if data.get("set_party"):
            eye = self.runner.model.party_eye
            if effect is not None:
                eye.effect = effect

            if is_xyz:
                p = [x, y, z]
                print("Setting pos of %s" % str(p))
                eye.set_xyz_pos(p, False)
            else:
                print("Setting party pan=%f, tilt=%f" % (x, y))      
                eye.pan = x
                eye.tilt = y

            if isinstance(color_pos, int):
                eye.color_pos = color_pos
            else:
                print("NOT setting color_pos")

            if isinstance(dimmer, float):
                eye.dimmer = dimmer
            else:
                print("NOT setting dimmer")

        if data.get("set_business"):
            eye = self.runner.model.business_eye
            if effect is not None:
                eye.effect = effect

            if is_xyz:
                p = [x, y, z]
                print("Setting pos of %s" % str(p))
                eye.set_xyz_pos(p, False)
            else:
                print("Setting party pan=%f, tilt=%f" % (x, y))      
                eye.pan = x
                eye.tilt = y

            if isinstance(color_pos, int):
                eye.color_pos = color_pos
            else:
                print("NOT setting color_pos")

            if isinstance(dimmer, float):
                eye.dimmer = dimmer
            else:
                print("NOT setting dimmer")

            eye.go();

        return {"ok": True}



    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def server_reset(self):
        data = cherrypy.request.json

        if not data.get("please"):
            return {"ok": False, "msg": "You didn't say please"}

        self.watchdog.manual_reset()

        return {"ok": True}


    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def store_position(self):
        data = cherrypy.request.json

        x = data.get("x_pos")
        y = data.get("y_pos")
        z = data.get("z_pos")

        is_xyz = data.get("pos_is_xyz") or False

        which = data.get("position")
        eye_positions = config.get("eye_positions")

        if is_xyz:
            xyz_pos = [x,y,z]
            pnt_p = eyes.xyz_to_pnt(xyz_pos, True)
            pnt_b = eyes.xyz_to_pnt(xyz_pos, False)
        else:
            pnt_p = [x,y]
            pnt_b = [x,y]

        if which == "disco":
            # Don't need to look at left / right. Disco is only left
            p = eye_positions["disco"]
            p[0] =pnt_p

        elif which == "headlights":
            p = eye_positions["headlights"]
            p[0] = pnt_p
            p[1] = pnt_b

        try:
            config.save()
        except Exception:
            return {"ok": False, "msg": "Couldn't save the positon"}

        return {"ok": True}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def set_reset_state(self):
        data = cherrypy.request.json

        is_party = data.get("is_party")
        mode = data.get("mode")

        if is_party:
            eye = self.runner.model.party_eye
        else:
            eye = self.runner.model.business_eye

        eye.reset_mode = mode

        if eye.reset_mode == mode:
            return {"ok": True}

        return {"ok": False}
