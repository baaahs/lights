Using The Simulator
===================

This is the user documentation for the simulator. See the main README.md file for information
about getting it installed.

Since the simulator runs inside Processing, at the very beginning of the setup() function
you'll see a size() call which defines the window size. If the window is too small, or more
likely if it is too big for your laptop, just make the X and Y values smaller here.

When the simulator starts you are presented with a side view of the sheep. This is a
full 3D model so you can use your mouse to move around by dragging.

  * Left Button - Orbit
    Horizontal movement will make the sheep spin around. Vertical movement will cause
    the camera to arc up into the sky, although the camera will remain pointed at
    the sheep the whole time.
  * Right Button - Pan & Tilt
    Without moving the position of the camera, the point the camera is looking at will be
    moved to the left or right with horizontal movement and up or down with vertical
    movement.
  * Middle Button - Translation
    Horizontal movement moves the camera and the point the camera is looking at
    to the left and the right relative to the current view of the camera. Cinematically
    this is a "truck" motion. Just play with it and you'll understand. Vertical movement
    will "boom" the camera up and the point it is looking at up and down.
  * Scroll Wheel - Zoom
    The field of view is zoomed in and out along the axis of the camera. Extremely close
    and exteremly far fields of view will look crazy and surfaces will start to clip.

When you've gotten lost, the three button in the upper most left side of the screen will
reset your view to one of 3 predefined locations.

The second UI control is the checkbox to show labels. This will cause the logical names
of all sides to be displayed more or less near the surfaces that are mapped to that name.
Yes, some of them are hard or impossible to read. Mapping text in 3D space is a pain
in the ass. Sorry. 

The next bit of UI allows you to enable the highlighting of a single logical panel,
which frequently maps to multiple surfaces on the 3D model. The party side is shown
in red and the business side is shown in blue, overriding any colors being sent be 
a running show.  Use the "Prev" and "Next" buttons to change which logical panel
is highlighted. The number is shown to the right of the Next button.

The Constrasting Colors button will set all the sheep panels to a set of reasonably
contrasting colors. This is a good way to see what the logical panels (as opposed to
the model surfaces) all are at a glance. Of course, if the simulator is busy being
driven by the show runner, these colors are going to get overwritten quickly, so this
is most useful when the show runner server isn't running.

Logical Panels vs. Surfaces
===========================

As a show author, you really only care about logical panels. These are almost the same
as the panel numbers the physical build crew used to design and construct the sheep, but
not exactly because they added a second alphanumeric designator for "front" and "rear"
that it would be a pain to refactor all our code to use.

Instead, in the world of shows, panels are either "Party" or "Business", and they have
an integer number. This is what we mean by a "logical panel". To further complicate things,
the 3D model is made up of a set of surfaces which do not map 1 to 1 with the physically
constructed panels. As much as reasonable the logical panels should map to physical 
panels, but particularly in the head and tail areas this may not be true. Additionally,
each ear and the tail are made up of several panels, but are treated as a single
logical panel from a show perspective.

Where there **is** a one to one mapping is between logical panels and DMX channels. That
mapping is configured inside the show runner.

Inside the simulator there is a mapping from logical panels (what the shows speak) to
3D model surfaces. Thus, when a show says turn panel 10 red, the simulator may turn 
multiple surfaces red to show what that will look like in real life.

Since a show writer needs to know what the logical name of each panel is, the simulator 
has a feature where you can have labels shown on or close-ish to each panel to show 
their number. Unfortunately the ones on the business side are reversed, but this is better
than nothing.

These logical labels are shown on each surface, which means many of the labels appear on
more than one surface. When that is the case, the label is shown at normal size on the
first surface and at a smaller size on the secondary surfaces.

The Eyes
========

One of the coolest new features of the simulator is that it models the Sharpies and
understands the exact same DMX channels that the real ones do. However, not all of the
features available on the real life lights are modeled. In particular animations of
things like the color wheel are generally not.

Things that are implemented:

  * Pan & Tilt - with a movement animation that should run at roughly the same speed
    as the real lights. This is approximately 3 seconds for 540 degrees of Pan, and
    approximately 1.8 seconds for 270 degrees of Tilt.
  * Color - These are rough approximations of the colors on the wheel. The half steps
    of the wheel and animated rotation are not modeled. In real life when you change
    from one color to the next, the color wheel may have to cycle through other
    intermediate things and you may or may not want that.
  * Dimming - This is simulated with the alpha channel of the modeled cones.


Keyboard Stuff
==============

Generally this isn't needed except when re-mapping panels.

  * The `[` and `]` keys are shortcuts for the "Prev" and "Next" buttons that move
    the logical panel highlighter. If the "Show Highlight" box is not checked you
    won't see that highlighter, but the position will still be changed. If you hold shift
    while pressing them (so you're typing `{` and `}`) the panel number will change by
    10, otherwise it changes by 1
  * The `,` and `.` keys control the position of the surface cursor, which is the
    nasty bright green surface that starts out on the tip of the tail. By moving this
    cursor around and looking at the output in the processing IDE window you can determine
    the surface index of anything on the sheep. The shifted versions (the < > characters)
    move the cursor by 10 positions and the normal comma and dot move it by 1 position.
  * To change the running logical mapping of a surface type the integer portion of
    the logical name first, then press either `b` or `p` for business or party side to
    re-map that surface. You should see some output in the processing window and if you
    have the labels showing you should see the label change. This changed mapping
    isn't saved automatically. When you restart the simulator it will be lost.
  * To save the current version of surface mappings, press `s`. This intentionally writes
    to a different file than the one which is used to load mappings, so you must manually
    go and copy the changed data over if you want to use it. Check the code if you're
    doing this.


