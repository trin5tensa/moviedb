"""test module.

This module contains tests written after the major database upgrade and
reflects the changes to sundries.py needed to support the changed API of
the DBv1 database.
"""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 2/4/25, 1:28 PM by stephen.
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


import config
from globalconstants import *
from handlers import moviebagfacade


def test_convert_from_movie_key_typed_dict():
    title = "Test title"
    year = 4242
    movie = config.MovieKeyTypedDict(title=title, year=year)

    # noinspection PyUnresolvedReferences
    movie_bag = moviebagfacade.convert_from_movie_key_typed_dict(movie)

    assert movie_bag == MovieBag(title=title, year=MovieInteger(year))


def test_convert_to_movie_key():
    title = "Test Title"
    year = "4242"
    movie_bag = MovieBag(title=title, year=MovieInteger(year))

    movie_key = moviebagfacade.convert_to_movie_key_typed_dict(movie_bag)

    assert movie_key == moviebagfacade.config.MovieKeyTypedDict(
        title=title, year=int(year)
    )


def test_convert_to_movie_update_def():
    title = "Convert to Update"
    year = "4242"
    director_1 = "Harriet House"
    director_2 = "Ira Indigo"
    duration = "42"
    notes = "Movie update definition."
    tags = {"tag 1", "tag 2", "tag 3"}
    # noinspection PyTypeChecker
    movie_bag = MovieBag(
        title=title,
        year=MovieInteger(year),
        duration=MovieInteger(duration),
        directors=[director_1, director_2],
        notes=notes,
        tags=tags,
    )

    movie = moviebagfacade.convert_to_movie_update_def(movie_bag)

    assert movie == config.MovieUpdateDef(
        title=title,
        year=int(year),
        director=", ".join([director_1, director_2]),
        minutes=int(duration),
        notes=notes,
        tags=list(tags),
    )
