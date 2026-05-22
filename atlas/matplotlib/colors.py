"""Minimal stub for matplotlib.colors used by seaborn and other visualization code."""

def to_rgb(c):
    # Accept tuples, hex strings (#rrggbb) or names; simple implementation
    if isinstance(c, (tuple, list)):
        return tuple(float(x) for x in c)
    if isinstance(c, str) and c.startswith('#') and len(c) == 7:
        r = int(c[1:3], 16)/255.0
        g = int(c[3:5], 16)/255.0
        b = int(c[5:7], 16)/255.0
        return (r, g, b)
    # fallback
    return (0.0, 0.0, 0.0)


def to_hex(c):
    r,g,b = to_rgb(c)
    return '#{:02x}{:02x}{:02x}'.format(int(r*255), int(g*255), int(b*255))

# Minimal Colormap and Normalize classes used by seaborn typing
class Colormap:
    def __init__(self, name=None):
        self.name = name
    def __call__(self, v):
        return to_rgb(v)

class Normalize:
    def __init__(self, vmin=None, vmax=None):
        self.vmin = vmin
        self.vmax = vmax
    def __call__(self, v):
        return v

__all__ = ["to_rgb", "to_hex", "Colormap", "Normalize"]
