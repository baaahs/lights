BAAAHS 2015 Edition
===================

![Simulator Screenshot](https://raw.githubusercontent.com/tomseago/baaahs2015/master/data/SheepSimulator.png)

## Requirements

* Python 2.7
  [http://www.python.org](http://www.python.org)

* Processing 2.2.1+ (for simulator only)
  [http://www.processing.org](http://www.processing.org)

There are a few 3rd party python modules that need to be installed:

  * Python:
    * cherrypy
    * pybonjour
  * Processing:
    * G4P
    * Shapes 3D

Install python modules with *easy_install* (You can also use *pip* if you have a preference)  For example:

    easy_install cherrypy

Don't worry too much if you can't get some of the dependencies to install - you'll still be able to run the software, just with some features missing.  Python and Processing are the most important parts if you just want to write shows.

The Processing libraries are pretty reliable to install.

  * Open Processing
  * Go to the *Sketch* menu
  * Select "Import Library" then "Add Library"
  * In the dialog window that opens, search for "G4P" then search for "Shapes 3D". Both are by Peter Lager because apparently he does good work.

Unlike the python code, without those libraries the simulator won't run. The good news is that they are easy to install.

## Getting Started

First, check out the repository:

    git clone git@github.com:tomseago/baaahs2015.git

(or alternately `git clone https://github.com/tomseago/baaahs2015.git` )

(Note, the old repo for 2014 used hg instead of git and was at http://bitbucket.org/grgbrn/baaahs2014)

The simulator lives in the 'SheepSimulator' directory.  Open the file 'SheepSimulator.pde' in Processing, and run it.

To start the lighting software talking to the simulator:

	python go.py --simulator

You can also specify which show to run by using the name of the show:

    python go.py --simulator MyShow

You can also choose which show is running through the web interface:

[http://localhost:9990/](http://localhost:9990/)

## Writing Shows

This means writing a Python class that adheres to the show interface. Shows can now control both
panels and/or eyes. We definitely need more eye controlling shows 'cause that's the newest thing.

See the files in the 'doc' directory for details.

## Contributing Shows

You have some options here. The basic thing that has to get accomplished is your .py file with your show in it
(see above) needs to get added to the repository. The preference is to do this by submitting a pull request to
the master branch of the repo.

You can either fork the code on github (which anyone can do at anytime), make your changes, and then submit
a pull request. This is perhaps the easiest way to jump in because anyone from the Intarwebs can do so at
any point without needing any permission or anything like that.

An alternate way to contribute is to simply clone the repo locally, *make your own branch*, commit your changes *to 
your branch*, then push them and finally create a pull request. To push your changes you will need to be
added as a collaborator, which any of the other collaborators should be able to do. Bothering Tom Seago is a good
way to get this done.  The downside here is that you need to be careful to be working on your branch not
the master branch.

For more info about how pull requests work, see https://help.github.com/articles/using-pull-requests/

The alternate alternate path is to simple email/fb/carrier pigeon your .py file to Tom S. He's not in love 
with this plan, but will get it added eventually if you do so.

## OSC Control

Lighting can be controlled wirelessly over OSC. We're using [TouchOSC](http://hexler.net/software/touchosc), which is available for [iOS](https://itunes.apple.com/app/touchosc/id288120394) and [Android](https://play.google.com/store/apps/details?id=net.hexler.touchosc_a).  (It costs $4.99, but it's worth it, we promise!)

You'll need to install the app on your phone or tablet, then install a layout.

1. Download the TouchOSC Editor from the [TouchOSC page](http://hexler.net/software/touchosc) (scroll down to 'Downloads') 
2. Open the show control layout from the baaahs repository (misc/BAAAHS 2015.touchosc)
3. Click 'Sync' in the TouchOSC Editor menubar and follow the on-screen instructions
	
For more details on controlling shows with OSC, check the 'doc' directory in this repository.

## Hardware Support

Communicating with the hardware requires [OLA.](http://www.opendmx.net)

OS X:

    brew install ola --with-python

Debian / Ubuntu:

    sudo apt-get install ola ola-python ola-rdm-tests

## Tips

Trouble installing python dependencies?  Try some of these magic incantations:

OS X:

    pip install --no-use-wheel CherryPy

    pip install setuptools-git
    pip install --allow-external pybonjour pybonjour

Debian / Ubuntu:

    apt-get install libavahi-compat-libdnssd1

    pip install --allow-external pybonjour --allow-unverified pybonjour pybonjour



