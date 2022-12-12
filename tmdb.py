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
#  Copyright (c) 2022-2022. Stephen Rigden.
#  Last modified 12/12/22, 12:13 PM by stephen.
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

import config
import exception

tmdbsimple.REQUESTS_TIMEOUT = (2, 5)  # seconds for connect and read.


def search_tmdb(tmdb_api_key: str, title_query: str, work_queue: queue.Queue) -> None:
    """Search and queue movies as the producer end of the producer and consumer pattern.
    
    Args:
        tmdb_api_key:
        title_query: Pass a text query to search.
        work_queue: A LIFO queue intended to return successive searches by the user so the user has immediate
        feedback on the effect of improving her search string.

    Raises:
        These internal exceptions allow the handler module to initiate user interactions.
        TMDBAPIKeyException:
            API Key error.
        TMDBConnectionTimeout:
            Unable to connect to TMDB
    """
    # todo
    #   Doc review
    tmdbsimple.API_KEY = tmdb_api_key
    try:
        movies: list[config.MovieTypedDict] = _retrieve_compliants(title_query)

    except requests.exceptions.ConnectionError as exc:
        msg = f"Unable to connect to TMDB. {exc.args[0].args[0]}"
        logging.info(msg)
        raise exception.TMDBConnectionTimeout(msg) from exc

    except requests.exceptions.HTTPError as exc:
        # Incorrect API key
        if exc.args and (exc.args[0][:38]) == '401 Client Error: Unauthorized for url':
            msg = f"API Key error: {exc.args[0]}"
            logging.error(msg)
            raise exception.TMDBAPIKeyException(msg) from exc

        else:
            _, exc_inst, _ = sys.exc_info()
            logging.error(repr(exc_inst))
            raise

    else:
        work_queue.put(movies)


def _retrieve_compliants(title_query):
    # todo
    #   Doc review
    compliants = _search_movies(title_query)

    movies = []
    for compliant in compliants:
        tmdb_id = compliant['id']
        movie = _data_conversion(_get_tmdb_movie_info(tmdb_id))
        movies.append(movie)
    return movies


def _data_conversion(tmdb_movie):
    # todo
    #   Doc review
    # The release_date is YYYY-MM-DD if it's present.
    if date:=tmdb_movie.get('release_date', ''):
        year = date[:4]
    else:
        year = ''

    movie = config.MovieTypedDict(
        title=tmdb_movie.get('title', ''),
        year=year,
        director=tmdb_movie.get('directors', ''),
        minutes=tmdb_movie.get('runtime', ''),
        notes=tmdb_movie.get('overview', ''),
    )
    return movie


def _search_movies(title_query: str, primary_release_year: int = None,
                   year: int = None, language: str = None, include_adult: bool = False, region: str = None):
    """Search and queue movies as the producer end of the producer and consumer pattern.
    
    Args:
        title_query: Pass a text query to search.
        year: A filter to limit the results to a specific year.
        primary_release_year: A filter to limit the results to a specific primary release year.
        language: ISO 639-1 code.
        include_adult: Choose whether to include adult content in the results.
        region: Specify an ISO 3166-1 code to filter by region. Must be uppercase.

    Raises:
        TMDBAPIKeyException:
            API Key error.
        TMDBConnectionTimeout:
            Unable to connect to TMDB
    """
    # todo
    #   Doc review
    search = tmdbsimple.Search()
    search.movie(query=title_query, primary_release_year=primary_release_year, year=year,
                 language=language, include_adult=include_adult, region=region)
    return search.results


def _get_tmdb_movie_info(tmdb_movie_id: str) -> dict:
    """
    Retrieve the details of a movie using its TMDB id.

    Args:
        tmdb_api_key: The TMDB API key
        tmdb_movie_id: The movie's TMDB id.

    Raises:
        TMDBAPIKeyException:
            API Key error.
        TMDBMovieIDMissing:
            A TMDB movie cannot be found, although it is known to have formerly existed.
        TMDBConnectionTimeout:
            Unable to connect to TMDB

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
    # todo
    #   Doc review
    movie = tmdbsimple.Movies(tmdb_movie_id)

    try:
        info = movie.info()

    except requests.exceptions.HTTPError as exc:
        # Movie not found. Since this movie id originated from TMDB this is unexpected.
        # The TMDB URL ends with movie/XXX where XXX is the requested tmdb_id code.
        if exc.args and (exc.args[0][:36]) == '404 Client Error: Not Found for url:':
            msg = f"The TMDB id '{tmdb_movie_id}' was not found on the TMDB site. \n{exc.args[0]}"
            logging.error(msg)
            raise exception.TMDBMovieIDMissing(msg) from exc
        else:
            raise

    crew = movie.credits().get('crew')
    if crew:
        directors = [person.get('name') for person in crew if person.get('job') == 'Director']
        info.update(dict(directors=directors))
    return info
