"""Minimal stub for matplotlib.animation used in tests."""

class FuncAnimation:
    def __init__(self, fig, func, frames=None, interval=200, blit=False, repeat=True):
        self.fig = fig
        self.func = func
        self.frames = frames
        self.interval = interval
        self.blit = blit
        self.repeat = repeat
    def save(self, *args, **kwargs):
        # no-op save
        return None

class ArtistAnimation:
    def __init__(self, fig, artists, interval=200):
        self.fig = fig
        self.artists = artists
        self.interval = interval
    def save(self, *args, **kwargs):
        return None

__all__ = ["FuncAnimation", "ArtistAnimation"]
