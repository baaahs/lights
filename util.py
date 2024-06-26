import collections
import functools
import datetime

# https://wiki.python.org/moin/PythonDecoratorLibrary#Memoize
class memoized(object):
    """
    Decorator. Caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned
    (not reevaluated).
    """
    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        if not isinstance(args, collections.Hashable):
            # uncacheable. a list, for instance.
            # better to not cache than blow up.
            return self.func(*args)
        if args in self.cache:
            return self.cache[args]
        else:
            value = self.func(*args)
            self.cache[args] = value
            return value

    def __repr__(self):
        "Return the function's docstring."
        return self.func.__doc__

    def __get__(self, obj, objtype):
        "Support instance methods."
        return functools.partial(self.__call__, obj)

# http://stackoverflow.com/questions/1969240/mapping-a-range-of-values-to-another
def make_interpolater(in_min, in_max, out_min, out_max):
    "Return a function that translates from one range to another"
    # Figure out how wide each range is
    inSpan = in_max - in_min
    outSpan = out_max - out_min

    # Compute the scale factor between left and right values
    scaleFactor = float(outSpan) / float(inSpan)

    # create interpolation function using pre-calculated scaleFactor
    def interp_fn(value):
        return out_min + (value-in_min)*scaleFactor

    return interp_fn

def get_hostname(default=None):
    "Return the hostname of the current system"
    try:
        import socket
        name = socket.gethostname()
        return name.split('.')[0]
    except Exception as e:
        return default


def wrapped_list(list, which):
    """
    Selects an element from a list, wrapping in either direction.
    """
    if which < 0:
        ix = len(list) + (which % len(list))
    else:
        ix = which % len(list)

    return list[ix]

def prettydate(d):
    diff = datetime.datetime.utcnow() - d
    s = diff.seconds
    if diff.days > 7 or diff.days < 0:
        return d.strftime('%d %b %y')
    elif diff.days == 1:
        return '1 day ago'
    elif diff.days > 1:
        return '{} days ago'.format(diff.days)
    elif s <= 1:
        return 'just now'
    elif s < 60:
        return '{} seconds ago'.format(s)
    elif s < 120:
        return '1 minute ago'
    elif s < 3600:
        return '{} minutes ago'.format(s/60)
    elif s < 7200:
        return '1 hour ago'
    else:
        return '{} hours ago'.format(s/3600)