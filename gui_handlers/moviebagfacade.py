"""MovieBag Facade."""

#  Copyright© 2024. Stephen Rigden.
#  Last modified 10/17/24, 11:10 AM by stephen.
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

from config import MovieKeyTypedDict, FindMovieTypedDict, MovieUpdateDef
from globalconstants import *


class MovieBagFacade(MovieBag):
    """This subclass of MovieBag provides movie bag constructors.

    Use Case:
        It is temporary until the GUI API is rewritten for movie bags at
        which time this subclass will become obsolete.
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

        Use Case:
            It is temporary until the GUI API is rewritten for movie bags at
            which time this method will become obsolete.
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

        Use Case:
            It is temporary until the GUI API is rewritten for movie bags at
            which time this method will become obsolete.
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

        Use Case:
            It is temporary until the GUI API is rewritten for movie bags at
            which time this method will become obsolete.
        """
        movie_bag = cls.__new__(MovieBagFacade)
        if movie.get("title"):
            movie_bag["title"] = movie["title"]
        if movie.get("year"):
            movie_bag["year"] = _range_converter(movie["year"])
        if movie.get("director"):
            movie_bag["directors"] = set(movie["director"].split(", "))
        if movie.get("minutes"):
            movie_bag["duration"] = _range_converter(movie["minutes"])
        if movie.get("notes"):
            movie_bag["notes"] = movie["notes"]
        if movie.get("tags"):
            movie_bag["movie_tags"] = {movie for movie in movie["tags"]}
        return movie_bag


def convert_to_movie_key(movie_bag: MovieBag) -> MovieKeyTypedDict:
    """Returns a config.MovieKeyTypedDict object.

    Use Case:
        It is temporary until the GUI API is rewritten for movie bags at
        which time this function will become obsolete.
    """
    movie_key = MovieKeyTypedDict(
        title=movie_bag["title"],
        year=int(movie_bag["year"]),
    )
    return movie_key


def convert_to_movie_update_def(movie_bag: MovieBag) -> MovieUpdateDef:
    """Converts a new style MovieBag object into an old style MovieUpdateDef object.

    Args:
        movie_bag:

    Returns:
        A MovieUpdateDef object

    Use Case:
        It is temporary until the GUI API is rewritten for movie bags at
        which time this function will become obsolete.
    """
    movie = MovieUpdateDef(**convert_to_movie_key(movie_bag))
    if movie_bag.get("directors"):
        movie["director"] = list(movie_bag.get("directors"))
    if movie_bag.get("duration"):
        movie["minutes"] = int(movie_bag.get("duration"))
    if movie_bag.get("notes"):
        movie["notes"] = movie_bag.get("notes")
    if movie_bag.get("movie_tags"):
        movie["tags"] = list(movie_bag.get("movie_tags"))
    return movie


def _range_converter(value: Sequence[str]) -> MovieInteger:
    """Converts a 'range' string into a MovieInteger object.

    Args:
        value: The year and minutes item in the old style FindMovieTypedDict
        contained a sequence of stings. The intended use was for either
        a sing numeric string or a pair of numeric strings.
        For example: [1960] or [1960, 1965].

    Returns:
        A MovieInt object.
    """
    # not todo Common code already tested within caller
    match len(value):
        case 1:
            duration_range = f"{value[0]}"
        case 2:
            duration_range = f"{value[0]}-{value[1]}"
        case _:
            raise ValueError(
                f"Length of value must be 1 or 2 not" f" {len(value)}. {value=}"
            )
    return MovieInteger(duration_range)
