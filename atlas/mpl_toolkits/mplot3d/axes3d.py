"""Minimal stub of Axes3D used in tests.
"""

class Axes3D:
    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
    def plot(self, *args, **kwargs):
        return None
    def scatter(self, *args, **kwargs):
        return None

__all__ = ["Axes3D"]
