"""Minimal stub for matplotlib.figure.Figure used by packages like seaborn."""

class Figure:
    def __init__(self, *args, **kwargs):
        self.axes = []
    def add_subplot(self, *args, **kwargs):
        ax = object()
        self.axes.append(ax)
        return ax
    def savefig(self, *args, **kwargs):
        return None

__all__ = ["Figure"]
