"""MovieBag Facade."""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 2/3/25, 2:59 PM by stephen.
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

import config

from globalconstants import MovieBag, MovieInteger


def convert_from_movie_key_typed_dict(movie: config.MovieKeyTypedDict) -> MovieBag:
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


def convert_to_movie_key_typed_dict(movie_bag: MovieBag) -> config.MovieKeyTypedDict:
    """Returns a config.MovieKeyTypedDict object.

    Use Case:
        It is temporary until the GUI API is rewritten for movie bags at
        which time this function will become obsolete.
    """
    movie_key = config.MovieKeyTypedDict(
        title=movie_bag["title"],
        year=int(movie_bag["year"]),
    )
    return movie_key


def convert_to_movie_update_def(movie_bag: MovieBag) -> config.MovieUpdateDef:
    """Converts a new style MovieBag object into an old style MovieUpdateDef object.

    Args:
        movie_bag:

    Returns:
        A MovieUpdateDef object

    Use Case:
        It is temporary until the GUI API is rewritten for movie bags at
        which time this function will become obsolete.
    """
    movie = config.MovieUpdateDef(**convert_to_movie_key_typed_dict(movie_bag))
    if movie_bag.get("directors"):
        movie["director"] = ", ".join(movie_bag.get("directors"))
    if movie_bag.get("duration"):
        movie["minutes"] = int(movie_bag.get("duration"))
    if movie_bag.get("notes"):
        movie["notes"] = movie_bag.get("notes")
    if movie_bag.get("tags"):
        movie["tags"] = list(movie_bag.get("tags"))
    return movie
