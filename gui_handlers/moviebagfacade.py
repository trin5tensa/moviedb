"""MovieBag Facade."""

#  Copyright© 2024. Stephen Rigden.
#  Last modified 10/5/24, 4:20 PM by stephen.
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

import copy

from config import MovieKeyTypedDict, FindMovieTypedDict
from globalconstants import *


class MovieBagFacade(MovieBag):
    """This subclass of MovieBag provides movie bag constructors.

    It is temporary until the GUI API is rewritten for movie bags at which
    time this subclass will become obsolete.
    """

    # noinspection PyTypedDict
    @classmethod
    def from_movie_key_typed_dict(cls, movie: MovieKeyTypedDict) -> "MovieBagFacade":
        """Converts a MovieKeyTypedDict into a MovieBag object.

        Args:
        print(f"{movie=}")
            movie:

        Returns:
            A movie bag object.
        """
        return cls(title=movie["title"], year=MovieInteger(movie["year"]))

    # noinspection PyTypedDict
    @classmethod
    def from_movie_td(cls, movie: MovieTD) -> "MovieBagFacade":
        """Converts a MovieTD into a MovieBag object.

        Args:
            movie:

        Returns:
            A movie bag object.
        """
        movie = copy.deepcopy(movie)  # Testing support (before and after)
        # noinspection PyTypeChecker
        movie["year"] = MovieInteger(movie["year"])
        if movie.get("director"):
            # noinspection PyTypeChecker
            movie["directors"] = {movie["director"]}
            del movie["director"]
        if movie.get("duration"):
            # noinspection PyTypeChecker
            movie["duration"] = MovieInteger(movie["duration"])
        if movie.get("movie_tags"):
            # noinspection PyTypeChecker
            movie["movie_tags"] = {movie for movie in movie["movie_tags"]}
        return cls(movie)

    # noinspection PyTypedDict
    @classmethod
    def from_find_movie_typed_dict(cls, movie: FindMovieTypedDict) -> "MovieBagFacade":
        """Converts a FindMovieTypedDict into a MovieBag object.

        Args:
            movie:

        Returns:
            A movie bag object.
        """
        movie = copy.deepcopy(movie)  # Testing support (before and after)
        if movie.get("year"):
            year_range = f"{movie['year'][0]}-{movie['year'][1]}"
            # noinspection PyTypeChecker
            movie["year"] = MovieInteger(year_range)
        if movie.get("director"):
            # noinspection PyTypeChecker
            movie["directors"] = {movie["director"]}
            del movie["director"]
        if movie.get("minutes"):
            duration_range = f"{movie['minutes'][0]}-{movie['minutes'][1]}"
            # noinspection PyTypeChecker
            movie["duration"] = MovieInteger(duration_range)
            del movie["minutes"]
        if movie.get("tags"):
            # noinspection PyTypeChecker
            movie["movie_tags"] = {movie for movie in movie["tags"]}
            del movie["tags"]
        return cls(movie)
