"""Minimal sbml I/O compatibility layer for tests."""

def read_sbml_model(path_or_str, *args, **kwargs):
    # Return a minimal model-like object or None
    class Model:
        def __init__(self):
            self.id = 'stub_model'
    return Model()


def write_sbml_model(model, path, *args, **kwargs):
    # Write stub SBML (no-op)
    with open(path, 'w') as f:
        f.write('<sbml></sbml>')
    return True


def validate_sbml_model(model):
    return True

__all__ = ["read_sbml_model", "write_sbml_model", "validate_sbml_model"]
