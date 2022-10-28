"""A collection of general purpose code."""

#  Copyright (c) 2022-2022. Stephen Rigden.
#  Last modified 10/15/22, 12:37 PM by stephen.
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
