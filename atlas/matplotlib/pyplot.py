"""Minimal stub of matplotlib.pyplot used in tests.
Implements a few no-op functions commonly used in plotting code: plot, figure, savefig, show, imshow.
"""

import types

class Figure:
    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
    def savefig(self, *args, **kwargs):
        # no-op: tests expect this to be callable
        return None


def figure(*args, **kwargs):
    return Figure(*args, **kwargs)


def plot(*args, **kwargs):
    # no-op plotting
    return None


def show(*args, **kwargs):
    # no-op
    return None


def imshow(*args, **kwargs):
    # no-op
    return None


def clf():
    # clear figure - no-op
    return None


def savefig(*args, **kwargs):
    # no-op: accept both fig.savefig(...) and plt.savefig(...)
    return None

def close(fig=None):
    # no-op figure close
    return None


def subplots(nrows=1, ncols=1, **kwargs):
    # Return a minimal (fig, ax) pair. Ax is a simple object with minimal API used by tests.
    fig = Figure()
    class Ax:
        def plot(self, *a, **k):
            return None
        def imshow(self, *a, **k):
            return None
        def scatter(self, *a, **k):
            return None
        def set_title(self, *a, **k):
            return None
        def set_xlabel(self, *a, **k):
            return None
        def set_ylabel(self, *a, **k):
            return None
        def grid(self, *a, **k):
            return None
        def legend(self, *a, **k):
            return None
        def set_xlim(self, *a, **k):
            # Accept calls like set_xlim(left, right) or set_xlim((left, right))
            return None
        def set_ylim(self, *a, **k):
            return None
        def set_aspect(self, *a, **k):
            return None
        def fill_between(self, *a, **k):
            return None
        def set_xticks(self, *a, **k):
            return None
        def set_yticks(self, *a, **k):
            return None
        def hist(self, *a, **k):
            return None
    ax = Ax()
    return fig, ax

# Minimal style support
class _Style:
    def __init__(self):
        self.available = []
    def use(self, name):
        # no-op
        return None

style = _Style()

# Export module-level symbols typically used
__all__ = ["figure", "plot", "show", "imshow", "clf", "Figure", "style", "subplots"]
