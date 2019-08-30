"""A collection of general purpose code."""
#  Copyright© 2019. Stephen Rigden.
from functools import wraps
from typing import Callable


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
