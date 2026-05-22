"""Minimal stub for matplotlib.markers used by seaborn."""

class MarkerStyle:
    def __init__(self, marker=None):
        self.marker = marker
    def get_marker(self):
        return self.marker

__all__ = ["MarkerStyle"]
