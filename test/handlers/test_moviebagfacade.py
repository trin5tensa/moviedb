"""test module.

This module contains tests written after the major database upgrade and
reflects the changes to sundries.py needed to support the changed API of
the DBv1 database.
"""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 1/23/25, 1:06 PM by stephen.
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


def test_convert_from_movie_td():
    title = "Test title"
    year = "4242"
    director = "Test director"
    duration = "42"
    notes = "A test note"
    tags = ["Tag 1", "Tag 2"]
    # todo MovieTD
    movie = MovieTD(
        title=title,
        year=year,
        director=director,
        minutes=duration,
        notes=notes,
        tags=tags,
    )

    # noinspection PyUnresolvedReferences
    movie_bag = moviebagfacade.convert_from_movie_td(movie)

    assert movie_bag == MovieBag(
        title=title,
        year=MovieInteger(year),
        directors={director},
        duration=MovieInteger(duration),
        notes=notes,
        synopsis=notes,
        movie_tags=set(tags),
    )


def test_convert_from_movie_td_with_no_data():
    # noinspection PyArgumentList
    # todo MovieTD
    movie = MovieTD()

    movie_bag = moviebagfacade.convert_from_movie_td(movie)

    assert movie_bag == MovieBag()


def test_convert_to_movie_key():
    title = "Test Title"
    year = "4242"
    movie_bag = MovieBag(title=title, year=MovieInteger(year))

    movie_key = moviebagfacade.convert_to_movie_key_typed_dict(movie_bag)

    assert movie_key == moviebagfacade.MovieKeyTypedDict(title=title, year=int(year))


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
        movie_tags=tags,
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


def test_convert_from_find_movie_typed_dict_with_singles():
    title = "Test title"
    year = "4242"
    directors = "Test director"
    duration = "42"
    notes = "A test note"
    tags = "Tag 1"
    movie = config.FindMovieTypedDict(
        title=title,
        year=[year],
        director=directors,
        minutes=[duration],
        notes=notes,
        tags=list(tags),
    )

    # noinspection PyUnresolvedReferences
    movie_bag = moviebagfacade.convert_from_find_movie_typed_dict(movie)

    assert movie_bag == MovieBag(
        title=title,
        year=MovieInteger(year),
        directors={directors},
        duration=MovieInteger(duration),
        notes=notes,
        movie_tags=set(tags),
    )


def test_convert_from_find_movie_typed_dict_with_doubles():
    title = "Test title"
    lo_year = 4242
    hi_year = 4244
    year = [str(lo_year), str(hi_year)]
    director_1 = "Michael Metcalf"
    director_2 = "Nancy Nagulto"
    directors = director_1 + ", " + director_2
    lo_duration = 42
    hi_duration = 44
    duration = [str(lo_duration), str(hi_duration)]
    notes = "A test note"
    tags = ["Tag 1", "Tag 2"]
    movie = config.FindMovieTypedDict(
        title=title,
        year=year,
        director=directors,
        minutes=duration,
        notes=notes,
        tags=tags,
    )

    # noinspection PyUnresolvedReferences
    movie_bag = moviebagfacade.convert_from_find_movie_typed_dict(movie)

    assert movie_bag == MovieBag(
        title=title,
        year=MovieInteger(str(lo_year) + "-" + str(hi_year)),
        directors={director_1, director_2},
        duration=MovieInteger(str(lo_duration) + "-" + str(hi_duration)),
        notes=notes,
        movie_tags=set(tags),
    )
