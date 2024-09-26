"""test module.

This module contains tests written after the major database upgrade and
reflects the changes to handlers.py needed to support the changed API of
the DBv1 database.
"""

#  Copyright© 2024. Stephen Rigden.
#  Last modified 9/26/24, 6:30 AM by stephen.
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
from gui_handlers import moviebagfacade


# noinspection PyMissingOrEmptyDocstring
class TestMovieBagFacade:
    def test_from_movie_key_typed_dict(self):
        title = "Test title"
        year = 4242
        movie = config.MovieKeyTypedDict(title=title, year=year)

        # noinspection PyUnresolvedReferences
        movie_bag = moviebagfacade.MovieBagFacade.from_movie_key_typed_dict(movie)

        assert movie_bag == MovieBag(title=title, year=MovieInteger(year))

    def test_from_movie_td(self):
        title = "Test title"
        year = "4242"
        director = "Test director"
        duration = "42"
        notes = "A test note"
        movie_tags_ = ["Tag 1", "Tag 2"]
        movie = MovieTD(
            title=title,
            year=year,
            director=director,
            duration=duration,
            notes=notes,
            movie_tags=movie_tags_,
        )

        # noinspection PyUnresolvedReferences
        movie_bag = moviebagfacade.MovieBagFacade.from_movie_td(movie)

        assert movie_bag == MovieBag(
            title=title,
            year=MovieInteger(year),
            directors={director},
            duration=MovieInteger(duration),
            notes=notes,
            movie_tags=set(movie_tags_),
        )

    def test_from_find_movie_typed_dict(self):
        title = "Test title"
        lo_year = 4242
        hi_year = 4244
        year = [str(lo_year), str(hi_year)]
        director = "Test director"
        lo_duration = 42
        hi_duration = 44
        duration = [str(lo_duration), str(hi_duration)]
        notes = "A test note"
        movie_tags_ = ["Tag 1", "Tag 2"]
        movie = config.FindMovieTypedDict(
            title=title,
            year=year,
            director=director,
            minutes=duration,
            notes=notes,
            tags=movie_tags_,
        )

        # noinspection PyUnresolvedReferences
        movie_bag = moviebagfacade.MovieBagFacade.from_find_movie_typed_dict(movie)

        assert movie_bag == MovieBag(
            title=title,
            year=MovieInteger(str(lo_year) + "-" + str(hi_year)),
            directors={director},
            duration=MovieInteger(str(lo_duration) + "-" + str(hi_duration)),
            notes=notes,
            movie_tags=set(movie_tags_),
        )
