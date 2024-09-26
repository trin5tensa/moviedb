"""MovieBag Facade."""

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
        movie["year"] = MovieInteger(movie["year"])
        if movie["director"]:
            movie["directors"] = {movie["director"]}
            del movie["director"]
        if movie["duration"]:
            movie["duration"] = MovieInteger(movie["duration"])
        if movie["movie_tags"]:
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
        if movie["year"]:
            year_range = f"{movie['year'][0]}-{movie['year'][1]}"
            movie["year"] = MovieInteger(year_range)
        if movie["director"]:
            movie["directors"] = {movie["director"]}
            del movie["director"]
        if movie["minutes"]:
            duration_range = f"{movie['minutes'][0]}-{movie['minutes'][1]}"
            movie["duration"] = MovieInteger(duration_range)
            del movie["minutes"]
        if movie["tags"]:
            # noinspection PyTypeChecker
            movie["movie_tags"] = {movie for movie in movie["tags"]}
            del movie["tags"]
        return cls(movie)
