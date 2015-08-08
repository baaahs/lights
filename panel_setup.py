import array
import traceback
from ola.ClientWrapper import ClientWrapper
import json

universe = 0
wrapper = ClientWrapper()
client = wrapper.Client()
pixels = [0] * 512

eye_p = 0
eye_b = 0

MAX_PANEL = 90

panels=[]
for i in range(0, MAX_PANEL):
    panels.append( [-1, -1] )

is_dirty = False
skip_known = False

dmx_cursor = 0

def print_known():
    print " panel number[ party dmx, business dmx]"
    for i in range(1, MAX_PANEL):
        if i > 1 and (i-1) % 6 == 0:
            print ""

        p = panels[i]
        print "%2d[" % i,

        if p[0] != -1:
            print "%3d" % (p[0]+1),
        else:
            print "   ",

        print ",",

        if p[1] != -1:
            print "%3d" % (p[1]+1),
        else:
            print "   ",

        print "]",

    print ""


def callback(s):
    print s

def go():
    data = array.array('B')
    data.extend(pixels)
    client.SendDmx(universe, data, callback)

    # print "data %s" % str(data)


def change_dmx(delta):
    global dmx_cursor
    pixels[dmx_cursor] = 0
    pixels[dmx_cursor+1] = 0
    pixels[dmx_cursor+2] = 0

    dmx_cursor += delta

    if dmx_cursor < 0:
        dmx_cursor = 0
    if dmx_cursor > 510:
        dmx_cursor = 510

    pixels[dmx_cursor] = 255
    pixels[dmx_cursor+1] = 255
    pixels[dmx_cursor+2] = 255

def goto_dmx(addr):
    global dmx_cursor
    pixels[dmx_cursor] = 0
    pixels[dmx_cursor+1] = 0
    pixels[dmx_cursor+2] = 0

    dmx_cursor = addr

    if dmx_cursor < 0:
        dmx_cursor = 0
    if dmx_cursor > 510:
        dmx_cursor = 510

    pixels[dmx_cursor] = 255
    pixels[dmx_cursor+1] = 255
    pixels[dmx_cursor+2] = 255

def clear_panel(panel):
    print "Clearing panel %s" % panel
    panels[panel] = [0,0]

def print_help():
    global skip_known
    skip_known = True
    print "No help yet..."

def save():
    global is_dirty
    global skip_known

    # Do this all by hand because we want a particular human editable ordering
    with open("dmx_setup.json", "w") as f:

        f.write("{\n")

        for i in range(1, MAX_PANEL):
            p = panels[i]

            if p[0] != -1:
                f.write("\t\"%dp\": %d,\n" % (i, p[0]))

        f.write("\n")

        for i in range(1, MAX_PANEL):
            p = panels[i]

            if p[1] != -1:
                f.write("\t\"%db\": %d,\n" % (i, p[1]))

        f.write("\n")

        f.write("\t\"EYEp\": %d,\n" % (eye_p))
        f.write("\t\"EYEb\": %d\n" % (eye_b))

        f.write("}\n")

    print "\n Saved to dmx_setup.json"
    is_dirty = False
    skip_known = True


def handle_mapping(id):
    global is_dirty
    try:
        num = int(id[:-1])
    except ValueError:
        print "Invalid id '%s' ids must be an integer followed by either p or b like 17b or 42b" % id    

    s = id[-1:]
    if s != "p" and s != "b":
        print "Invalid id '%s' ids must be an integer followed by either p or b like 17b or 42b" % id
        return

    s_ix = 0
    if s == 'b':
        s_ix = 1

    panels[num][s_ix] = dmx_cursor
    change_dmx(3)
    is_dirty = True

def handle_command(cmd):

    try:
        if cmd == "help":
            print_help()
        elif cmd == "exit" or cmd == "quit":
            if is_dirty:
                print "Use quit! to exit without saving"
            else:
                return False
        elif cmd == "quit!" or cmd == "q!":
            return False
        elif cmd == "save":
            save()
        elif cmd == "n" or cmd == "no":
            change_dmx(3)
        elif cmd == "p":
            change_dmx(-3)
        elif cmd[:4] == "goto":
            goto_dmx(int(cmd[5:])-1)
        elif cmd[:5] == "clear":
            clear_panel(int(cmd[6:]))

        elif cmd == "":
            pass

        else:
            handle_mapping(cmd)
    except Exception:
        traceback.print_exc()


    return True

if __name__=='__main__':

    # Load existing things
    with open('data/dmx_mapping.json', 'r') as f:
        PANEL_MAP = json.load(f)

        for key in PANEL_MAP:
            try:
                num = int(key[:-1])
            except ValueError:
                continue

            if num >= MAX_PANEL:
                print "Ignoring %s because max panel is %d" % (key, MAX_PANEL)
                continue

            if key[-1:] == "p":
                panels[num][0] = PANEL_MAP[key]
            else:
                panels[num][1] = PANEL_MAP[key]

        eye_p = PANEL_MAP.get("EYEp") or 0
        eye_b = PANEL_MAP.get("EYEb") or 0


    goto_dmx(0)

    while True:
        if not skip_known:
            print_known()
        skip_known = False

        print ""

        print "DMX = %d  What's on? (enter a panel id or 'help' for more)" % (dmx_cursor+1)

        go()
        try:
            cmd = raw_input("> ")
        except KeyboardInterrupt:
            cmd = "exit"

        if not handle_command(cmd):
            print ""
            break


