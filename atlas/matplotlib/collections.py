"""Minimal stub for matplotlib.collections used by seaborn."""

class PatchCollection:
    def __init__(self, patches=None, **kwargs):
        self.patches = patches or []
        self.kwargs = kwargs
    def set_alpha(self, a):
        self.alpha = a

__all__ = ["PatchCollection"]
