"""TMDB Interface

TMDB (The Movie DataBase)
API Overview
https://www.themoviedb.org/documentation/api
Docs
https://developers.themoviedb.org/3/getting-started/introduction
Discover examples
https://www.themoviedb.org/documentation/api/discover

tmdbsimple.py
https://github.com/celiao/tmdbsimple
"""

#  Copyright© 2025. Stephen Rigden.
#  Last modified 2/7/25, 2:01 PM by stephen.
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
import logging
import queue
import sys

import requests
import tmdbsimple

import exception
from globalconstants import MovieBag, MovieInteger

tmdbsimple.REQUESTS_TIMEOUT = (2, 5)  # seconds for connect and read.


def search_tmdb(tmdb_api_key: str, title_query: str, work_queue: queue.Queue) -> None:
    """Searches TMDB for movies and puts them into a queue.

    Note: The TMDB interface and the private functions of this module can
    search for much more than title matches, but for simplicity only
    title searches are supported.

    Args:
        tmdb_api_key:
        title_query: A text search pattern for movie titles.
        work_queue: Caller's threadsafe queue for return of compliant movies.

    Raises:
        TMDBAPIKeyException:
            The API key is invalid.
        TMDBConnectionTimeout:
            Connection failure.
    """
    tmdbsimple.API_KEY = tmdb_api_key
    try:
        movie_bags: list[MovieBag] = _retrieve_compliants(title_query)

    except requests.exceptions.ConnectionError as exc:
        msg = f"Unable to connect to TMDB. {exc.args[0].args[0]}"
        logging.info(msg)
        raise exception.TMDBConnectionTimeout(msg) from exc

    except requests.exceptions.HTTPError as exc:
        if exc.args and (exc.args[0][:38]) == "401 Client Error: Unauthorized for url":
            msg = f"API Key error: {exc.args[0]}"
            logging.error(msg)
            raise exception.TMDBAPIKeyException(msg) from exc

        else:
            _, exc, _ = sys.exc_info()
            logging.error(repr(exc))
            raise

    else:
        work_queue.put(movie_bags)


def _retrieve_compliants(title_query: str) -> list[MovieBag]:
    """Searches TMDB for movies.

    Search TMDB to retrieve movie id keys. Use the key to retrieve detailed movie records.

    Args:
        title_query: A text search pattern for movie titles.

    Returns:
        A list of up to 20 movie bags.
    """
    compliants = _search_movies(title_query)

    movie_bags = []
    for compliant in compliants:
        tmdb_id = compliant["id"]
        movie_bag = _data_conversion(_get_tmdb_movie_info(tmdb_id))
        movie_bags.append(movie_bag)
    return movie_bags


def _data_conversion(tmdb_movie: dict) -> MovieBag:
    """Converts a TMDB movie mapping into a movie bag.

    Args:
        tmdb_movie: A TMDB movie mapping.

    Returns:
        A movie bag.
    """

    movie_bag = MovieBag()
    for k, v in tmdb_movie.items():
        if v:
            match k:
                case "title":
                    movie_bag["title"] = v
                case "release_date":
                    # release_date format YYYY-MM-DD
                    movie_bag["year"] = MovieInteger(v[:4])
                case "runtime":
                    movie_bag["duration"] = MovieInteger(v)
                case "directors":
                    movie_bag["directors"] = set(v)
                case "overview":  # pragma no branch
                    movie_bag["notes"] = v
    return movie_bag


def _search_movies(
    title_query: str,
    primary_release_year: int = None,
    year: int = None,
    language: str = None,
    include_adult: bool = False,
    region: str = None,
) -> list[dict]:
    """Searches TMDB for movie id keys.

    Args:
        title_query: A text search pattern for movie titles.
        primary_release_year: A filter to limit the results to a specific primary release year.
        year: A filter to limit the results to a specific year.
        language: ISO 639-1 code.
        include_adult: Choose whether to include adult content in the results.
        region: Specify an ISO 3166-1 code to filter by region. Must be uppercase.

    Returns:
        A list of compliant TMDB movies.

    Raises:
        TMDBAPIKeyException:
            API Key error.
        TMDBConnectionTimeout:
            Unable to connect to TMDB

    """
    search = tmdbsimple.Search()
    search.movie(
        query=title_query,
        primary_release_year=primary_release_year,
        year=year,
        language=language,
        include_adult=include_adult,
        region=region,
    )
    # noinspection PyUnresolvedReferences
    return search.results


def _get_tmdb_movie_info(tmdb_movie_id: str) -> dict:
    """
    Retrieves the details of a movie using its TMDB id.

    Args:
        tmdb_movie_id: The movie's TMDB id.

    Raises:
        TMDBMovieIDMissing:
            A TMDB movie cannot be found, although it is known to have formerly existed.

    Returns:
        A dict representation of the JSON returned from the API. This may include any or none of the
        following keys. The list is partial and does not include keys which are not of interest to
        this program.

        genres (Single item list containing a dictionary with keys: id, name)
        id
        imdb_id
        original_language
        original_title
        overview
        production_companies (Single item list containing a dictionary with keys: id, logo_path,
        name, origin_country)
        production_countries (Single item list containing a dictionary with keys: id, name)
        release_date
        runtime
        spoken_languages (Single item list containing a dictionary with keys: id, logo_path,
        name, origin_country)
        title
    """
    movie = tmdbsimple.Movies(tmdb_movie_id)

    try:
        info = movie.info()

    except requests.exceptions.HTTPError as exc:
        # Movie not found. Since this movie id originated from TMDB this is unexpected.
        # The TMDB URL ends with movie/XXX where XXX is the requested tmdb_id code.
        if exc.args and (exc.args[0][:36]) == "404 Client Error: Not Found for url:":
            msg = f"The TMDB id '{tmdb_movie_id}' was not found on the TMDB site. \n{exc.args[0]}"
            logging.error(msg)
            raise exception.TMDBMovieIDMissing(msg) from exc
        else:
            raise

    crew = movie.credits().get("crew")
    if crew:
        directors = [
            person.get("name") for person in crew if person.get("job") == "Director"
        ]
        info.update(dict(directors=directors))
    return info
