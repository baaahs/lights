Startup Scripts
===============

These startup scripts use upstart. So on a debian linux you will want to

    apt-get install upstart

before you move on to the other things.

To install the baaahs server as a system service, the code from the repo
has to be in the right place, and then two config script/files need to
get copied into appropriate locations.

This is all assuming a version of Ubuntu at 14.04 or later.

The code from the repo needs to live at

    /home/baaahs/baaahs2015

To install the baaahs service, copy the file `baaahs.conf` from this directory
to `/etc/init` and change it's ownership to root.

To make sure the baaahs service restarts when the network changes, copy the
`if-up.baaahs` file into `/etc/network/if-up.d` and also change it's ownership
to root.

To start the baaahs service, as root (sudo if you need to):

    service baaahs restart

That command can be used later to forcefully restart the service if necessary.
However, assuming the web interface is running, there is a big red "Die now"
button that can be used to restart it remotely.

When the service restarts, olad is also restarted, which should be a reasonable
good thing since it needs to be restarted on network changes anyway.


