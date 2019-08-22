"""
Decorators
"""
from functools import wraps


def prevent_signal_call_on_bulk_load(signal_handler):
    """
    Prevent signals to execute while bulk data is loaded / imported
    """
    @wraps(signal_handler)
    def wrapper(*args, **kwargs):
        if kwargs.get('raw'):
            return
        signal_handler(*args, **kwargs)

    return wrapper
