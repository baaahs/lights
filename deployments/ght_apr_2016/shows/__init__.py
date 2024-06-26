import os
import importlib
import inspect
from operator import itemgetter
import random

from util import memoized

# I don't see why we would bother to memoize this. That can almost certainly
# not be a terribly good thing to do...
#@memoized
def load_shows(path=None):
    "Return a list of tuples (name, class) describing shows found in the shows directory"
    if not path:
        path = __path__[0]

    _shows = []
    for m in [m for m in os.listdir(path) if not m.startswith('_') and m.endswith('.py')]:
        try:
            assert m.endswith('.py')
            m = m[:-3] # drop the .py from the filename
            module_name = "shows." + m
            # print "trying to load ", module_name

            mod = importlib.import_module(module_name)
            # print type(mod)

            # module may explicitly export multiple shows
            if hasattr(mod, '__shows__'):
                # print mod
                # print mod.__shows__
                # XXX validate these in any way?
                _shows.extend(mod.__shows__)
            else:
                # we have go to rooting around for things that look like shows
                for (name,t) in inspect.getmembers(mod):
                    if inspect.isclass(t):
                        is_show = False
                        if hasattr(t, "is_show"):
                            is_show = t.is_show
                        elif hasattr(t, 'next_frame'):
                            is_show = True

                        # print "likely show:", name, type(t)

                        if is_show:
                            if hasattr(t, "name"):
                                name = t.name
                            _shows.append( (name, t) )

        except Exception as e:
            print("exception loading module from %s, skipping" % m)
            import traceback
            traceback.print_exc()
    # sort show tuples by name before returning them
    #return sorted(_shows, key=itemgetter(0))
    # Don't sort because they just get put into a dictionary anyway
    return _shows

# def random_shows(path=None, norepeat=None):
#     """
#     Return an infinite sequence of randomized show constructors
#     Remembers the last 'norepeat' items to avoid replaying shows too soon
#     Norepeat defaults to 1/3 the size of the sequence
#     """
#     seq = [ctor for (name,ctor) in load_shows(path)]

#     if not norepeat:
#         norepeat=int(len(seq)/3)

#     seen = []
#     while True:
#         n = random.choice(seq)
#         while n in seen:
#             n = random.choice(seq)
#         seen.append(n)
#         if len(seen) >= norepeat:
#             seen = seen[1:]
#         yield n
