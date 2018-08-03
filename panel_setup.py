#!/usr/bin/env python2.7
import array
import traceback
from ola.ClientWrapper import ClientWrapper
import json

universe = 0
wrapper = ClientWrapper()
client = wrapper.Client()
pixels = [255] * 512

eye_p = 0
eye_b = 0

MAX_PANEL = 90

panels = []
for i in range(0, MAX_PANEL):
    panels.append( [ [], [] ] )

is_dirty = False

# When this is set to true by a handler, the "known mappings" UI display is not output
# after the handler is done. It must be reset each time.
skip_known = False

dmx_cursor = 1

def print_mapping(a):
    if len(a) == 0:
        print "     ",
        return

    print "%3d" % (a[0]),
    if len(a) > 1:
        print u"\u2026",
    else:
        print " ",



def print_known():
    print " panel number[ party dmx, business dmx]"
    for i in range(1, MAX_PANEL):
        if i > 1 and (i-1) % 6 == 0:
            print ""

        p = panels[i]
        print "%2d[" % i,

        print_mapping(p[0])
        print ",",
        print_mapping(p[1])


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
    # Because DMX is 1 based and lists are 0, we subtract 1 from the value
    # when writing to a buffer list
    global dmx_cursor
    pixels[dmx_cursor-1] = 255
    pixels[dmx_cursor] = 255
    pixels[dmx_cursor+1] = 255

    dmx_cursor += delta

    if dmx_cursor < 1:
        dmx_cursor = 1
    if dmx_cursor > 510:
        dmx_cursor = 510

    pixels[dmx_cursor-1] = 255
    pixels[dmx_cursor] = 0
    pixels[dmx_cursor+1] = 0

def goto_dmx(addr):

    global dmx_cursor
    pixels[dmx_cursor-1] = 255
    pixels[dmx_cursor] = 255
    pixels[dmx_cursor+1] = 255

    dmx_cursor = addr

    if dmx_cursor < 1:
        dmx_cursor = 1
    if dmx_cursor > 510:
        dmx_cursor = 510

    pixels[dmx_cursor-1] = 255
    pixels[dmx_cursor] = 0
    pixels[dmx_cursor+1] = 0

def clear_panel(panel):
    print "Clearing panel %s" % panel
    panels[panel] = [[],[]]

def show_mapping(m):
    for x in m:
        print "%3d " % (x),

def show_panel(panel):
    global skip_known
    skip_known = True

    print "Panel %d" % panel
    print "   party: ",
    show_mapping(panels[panel][0])
    print "\nbusiness: ",
    show_mapping(panels[panel][1])


def print_help():
    global skip_known
    skip_known = True

    print "help - show this summary"
    print "exit - exit if data has not changed"
    print "quit - exit if data has not changed, must use quit! if the data has changed"
    print "save - save the current mapping to dmx_setup.json (which is not the file loaded by default)"
    print "n, no, next - Advance DMX mapping by 3"
    print "p, prev     - Move DMX cursor backwards by 3"
    print "u           - Bump DMX up by 1"
    print "d           - Bump DMX down by 1"
    print "goto <num>  - Move cursor to channel <num>"
    print "clear <panel_num> - Remove all mappings for <panel_num>"
    print "show  <panel_num> - Show detail for <panel_num>"

def write_mapping(f, panel, m):
    f.write("\t")
    f.write("\"%s\": [" % panel)

    started = False
    for x in m:
        if started:
            f.write(", ")
        started = True
        f.write("%d" % x)

    f.write("],\n")


def save():
    global is_dirty
    global skip_known

    # Do this all by hand because we want a particular human editable ordering
    with open("dmx_setup.json", "w") as f:

        f.write("{\n")

        for i in range(1, MAX_PANEL):
            p = panels[i]

            if len(p[0]) > 0:
                write_mapping(f, "%dp" % i, p[0])
            #     f.write("\t\"%dp\": [" % (i))


            #     for x in p[0]:
            #         f.write("%d")

            # if p[0] != -1:
            #     f.write("\t\"%dp\": %d,\n" % (i, p[0]))

        f.write("\n")

        for i in range(1, MAX_PANEL):
            p = panels[i]

            if len(p[1]) > 0:
                write_mapping(f, "%db" % i, p[1])
            # if p[1] != -1:
            #     f.write("\t\"%db\": %d,\n" % (i, p[1]))

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

    panels[num][s_ix].append( dmx_cursor )
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
        elif cmd == "n" or cmd == "no" or cmd == "next":
            change_dmx(3)
        elif cmd == "p" or cmd == "prev":
            change_dmx(-3)
        elif cmd == "u":
            change_dmx(1)
        elif cmd == "d":
            change_dmx(-1)
        elif cmd[:4] == "goto":
            goto_dmx(int(cmd[5:]))
        elif cmd[:5] == "clear":
            clear_panel(int(cmd[6:]))
        elif cmd[:4] == "show":
            show_panel(int(cmd[5:]))

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

            v = PANEL_MAP[key]
            if type(v) is int:
                v = [v]

            if key[-1:] == "p":
                panels[num][0] = panels[num][0] + v
            else:
                panels[num][1] = panels[num][1] + v

        eye_p = PANEL_MAP.get("EYEp") or 0
        eye_b = PANEL_MAP.get("EYEb") or 0


    goto_dmx(0)

    while True:
        if not skip_known:
            print_known()
        skip_known = False

        print ""

        print "DMX = %d  What's on? (enter a panel id or 'help' for more)" % (dmx_cursor)

        go()
        try:
            cmd = raw_input("> ")
        except KeyboardInterrupt:
            cmd = "exit"

        if not handle_command(cmd):
            print ""
            break


