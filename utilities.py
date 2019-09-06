"""A collection of general purpose code."""

#  Copyright© 2019. Stephen Rigden.
#  Last modified 9/6/19, 9:06 AM by stephen.
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
