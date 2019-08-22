"""A collection of general purpose code."""
# moviedatabase-#43 CoroutineCloseException not necessary - remove
# TODO Remove layout reminder comments.
# Python package imports
from functools import wraps
from typing import Callable


# Third party package imports


# Project Imports


# Constants


# Variables


# Pure data Dataclasses
# Named tuples


# API Classes


# API Functions
# moviedatabase-#43 CoroutineCloseException not necessary - remove
def coroutine_primer(func: Callable) -> Callable:
    """Decorator: primes `func` by advancing to first `yield`.

    From Fluent Python 2nd Ed. Luciano Ramalho
    """

    @wraps(func)
    def primer(*args, **kwargs) -> Callable:
        gen = func(*args, **kwargs)
        next(gen)
        return gen

    return primer


# Internal Module Classes


# Internal Module Functions
