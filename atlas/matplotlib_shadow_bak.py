# Minimal matplotlib stub to avoid GUI/backends being set up during test collection.
# Only provides a 'use' function which most code checks for when trying to
# configure backends.

def use(*args, **kwargs):
    return None

# Keep minimal attributes to avoid attribute errors
pyplot = None
