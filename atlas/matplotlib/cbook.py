"""Minimal matplotlib.cbook stub for tests."""

class silent_list:
    pass


def normalize_kwargs(kwargs, allowed=None):
    # Minimal passthrough used by seaborn/palettes
    return kwargs

__all__ = ["silent_list", "normalize_kwargs"]
