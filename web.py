import cherrypy
import time
import eye_effect

class SheepyWeb(object):
    def __init__(self, queue, runner, cm):
        self.queue = queue
        self.runner = runner

        self.cm = cm

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
            print "RUNTIME XXXXX:::: %s" % run_time
            run_time = int(run_time)
            self.queue.put("inc runtime:%s"%run_time)
        except Exception as e:
            print "\n\nCRASH\n\n", e
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
            print "setting show to:", show_name
        else:
            print "didn't get a show name"

        # XXX otherwise the runner.status() method
        # hasn't had time to update
        time.sleep(0.2)
        raise cherrypy.HTTPRedirect("/")



    
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
        print "Start show name='%s'" % name

        self.runner.next_show(name=name)

        return {'ok': True}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def start_eo_show(self):
        data = cherrypy.request.json
        name = data.get("name")
        print "Start EO show name='%s'" % name

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
        out = {
            'show': {
                'name': self.runner.show.name,
                'run_time': self.runner.show_runtime                
            },
            'message': self.cm.message,
            'max_time': self.runner.max_show_time
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