"""MovieBag Facade."""

#  Copyright© 2024. Stephen Rigden.
#  Last modified 12/31/24, 1:01 PM by stephen.
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

from collections.abc import Sequence

from config import MovieKeyTypedDict, FindMovieTypedDict, MovieUpdateDef
from globalconstants import MovieBag, MovieInteger, MovieTD


def convert_from_movie_key_typed_dict(movie: MovieKeyTypedDict) -> MovieBag:
    """Converts a MovieKeyTypedDict into a MovieBag object.

    Args:
        movie:

    Returns:
        A movie bag object.

    Use Case:
        It is temporary until the GUI API is rewritten for movie bags at
        which time this method will become obsolete.
    """
    return MovieBag(title=movie["title"], year=MovieInteger(movie["year"]))


def convert_to_movie_key_typed_dict(movie_bag: MovieBag) -> MovieKeyTypedDict:
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


# noinspection DuplicatedCode
def convert_from_movie_td(movie: MovieTD) -> MovieBag:
    """Converts a MovieTD into a MovieBag object.

    Args:
        movie: A MovieTD()

    Returns:
        A movie bag object.

    Use Case:
        It is temporary until the GUI API is rewritten for movie bags at
        which time this method will become obsolete.
    """
    movie_bag = MovieBag()
    if movie.get("title"):
        movie_bag["title"] = movie["title"]
    if movie.get("director"):
        movie_bag["directors"] = set(movie["director"].split(", "))
    if movie.get("notes"):
        movie_bag["notes"] = movie["notes"]
        movie_bag["synopsis"] = movie["notes"]
    if movie.get("year"):
        movie_bag["year"] = MovieInteger(movie["year"])
    if movie.get("minutes"):
        movie_bag["duration"] = MovieInteger(movie["minutes"])
    if movie.get("tags"):
        movie_bag["movie_tags"] = {movie for movie in movie["tags"]}  # pragma no branch
    return movie_bag


# noinspection DuplicatedCode
def convert_from_find_movie_typed_dict(movie: FindMovieTypedDict) -> MovieBag:
    """Converts a FindMovieTypedDict into a MovieBag object.

    Args:
        movie: FindMovieTypedDict()

    Returns:
        A movie bag object.

    Use Case:
        It is temporary until the GUI API is rewritten for movie bags at
        which time this method will become obsolete.
    """
    movie_bag = MovieBag()
    if movie.get("title"):
        movie_bag["title"] = movie["title"]
    if movie.get("director"):
        movie_bag["directors"] = set(movie["director"].split(", "))
    if movie.get("notes"):
        movie_bag["notes"] = movie["notes"]
    if movie.get("year"):
        movie_bag["year"] = _range_converter(movie["year"])
    if movie.get("minutes"):
        movie_bag["duration"] = _range_converter(movie["minutes"])
    if movie.get("tags"):
        movie_bag["movie_tags"] = {movie for movie in movie["tags"]}  # pragma no branch
    return movie_bag


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
    movie = MovieUpdateDef(**convert_to_movie_key_typed_dict(movie_bag))
    if movie_bag.get("directors"):
        movie["director"] = ", ".join(movie_bag.get("directors"))
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
    match len(value):
        case 1:
            duration_range = f"{value[0]}"
        case 2:
            duration_range = f"{value[0]}-{value[1]}"
        case _:  # pragma: nocover
            raise ValueError(
                f"Length of value must be 1 or 2 not" f" {len(value)}. {value=}"
            )
    return MovieInteger(duration_range)
