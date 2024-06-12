"""Global constants and type definitions."""

#  Copyright ©2024. Stephen Rigden.
#  Last modified 6/12/24, 6:53 AM by stephen.
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
from datetime import datetime
from typing import TypedDict, NotRequired

from movieinteger import MovieInteger

DIRECTOR = "director"
DIRECTORS = "directors"
DURATION = "minutes"
MOVIE_TAG = "tag"
MOVIE_TAGS = "tags"
NOTES = "notes"
STARS = "stars"
SYNOPSIS = "synopsis"
TITLE = "title"
YEAR = "year"


class MovieTD(TypedDict):
    """Type definition for movie.

    Deprecated. Use MovieBag.
    """

    TITLE: str
    YEAR: str
    DIRECTOR: NotRequired[str]
    DURATION: NotRequired[str]
    NOTES: NotRequired[str]
    MOVIE_TAGS: NotRequired[Sequence[str]]


class MovieBag(TypedDict, total=False):
    """A structured bag for movie data.

    Whilst the individual fields are defined in detail there is no requirement or guarantee
    that any particular field is present. That is the responsibility of the data producer and
    data consumer.
    """

    title: str
    year: MovieInteger
    duration: MovieInteger
    directors: set[str]
    stars: set[str]
    synopsis: str
    notes: str
    movie_tags: set[str]

    # Database fields
    id: int
    created: datetime
    updated: datetime
