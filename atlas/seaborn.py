"""Minimal stub for seaborn to avoid heavy imports during tests.
Provides lightweight replacements for commonly used plotting helpers used in tests.
"""

def pairplot(*args, **kwargs):
    return None


def heatmap(*args, **kwargs):
    return None


def set_theme(*args, **kwargs):
    return None

def set_style(*args, **kwargs):
    return None

def set_palette(*args, **kwargs):
    return None


def color_palette(*args, **kwargs):
    return []


def boxplot(*args, **kwargs):
    return None

def barplot(*args, **kwargs):
    return None

# Compatibility attributes
__all__ = ["pairplot", "heatmap", "set_theme", "color_palette", "boxplot", "barplot"]
