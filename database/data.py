"""Data for database prototyping"""

#  Copyright ©2024. Stephen Rigden.
#  Last modified 6/14/24, 8:11 AM by stephen.
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

from globalconstants import MovieBag
from movieinteger import MovieInteger

title_year = MovieBag(title="Title-Year", year=MovieInteger(2042))

title_low_year = MovieBag(title="Title-Low-Year", year=MovieInteger(1066))

title_high_year = MovieBag(title="Title-High-Year", year=MovieInteger(10066))

movie_tags = ["5 Star", "4 Star", "3 Star"]

tagged_movie = MovieBag(
    title="Tagged-Movie",
    year=MovieInteger(2042),
    movie_tags={"5 Star", "3 Star", "No Star"},
    stars={"Sylvia Star", "Nepo Star"},
    directors={"Donald Dirac", "Sidney Star", "Nepo Dirac"},
)

new_movie = MovieBag(
    title="Updated Movie",
    year=MovieInteger(1942),
    movie_tags={"4 Star", "No Star"},
    stars={"Sylvia Star", "Sidney Star", "Upandcoming Star"},
    directors={"Donald Dirac", "Sidney Star"},
)

star_movie = MovieBag(
    title="Star Movie",
    year=MovieInteger(2042),
    stars={"Sylvia Star", "Sidney Star"},
)

star_movie_2 = MovieBag(
    title="Star Movie 2",
    year=MovieInteger(2042),
    stars={"Sylvia Star", "Sidney Star", "Son of Sidney"},
)

director_movie = MovieBag(
    title="Director Movie",
    year=MovieInteger(2042),
    directors={"Donald Dirac", "Nepo Dirac"},
)

ego_movie = MovieBag(
    title="Ego-Movie",
    year=MovieInteger(2042),
    directors={"Donald Dirac"},
    stars={"Donald Dirac", "Sidney Star", "Daughter of Sidney"},
)
