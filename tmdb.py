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
#  Last modified 11/4/22, 9:55 AM by stephen.
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
import sys
from typing import Union

import requests
import tmdbsimple


TIMEOUT = 0.001


def search_movies(tmdb_api_key: str, title_query: str, primary_release_year: int = None,
                  year: int = None, language: str = None, include_adult: bool = False,
                  region: str = None) -> list[dict[str, Union[str, list[str]]]]:
    """Search for movies.
    
    Args:
        tmdb_api_key:
        title_query: (required) Pass a text query to search. This value should be URI encoded. (See
            Percent-encoding on Wikipedia: https://en.wikipedia.org/wiki/Percent-encoding)
        year: (optional) A filter to limit the results to a specific year (looking at all release dates).
        primary_release_year: (optional) A filter to limit the results to a specific primary
            release year.
        language: (optional) ISO 639-1 code.
        include_adult: (optional) Choose whether to include adult content in the results.
        region: (optional) Specify a ISO 3166-1 code to filter by region. Must be uppercase.

    Raises:
        TMDBAPIKeyException:
            API Key error.
        TMDBConnectionTimeout:
            Unable to connect to TMDB

    Returns:
        Movies with a title that is a superstring of title_query restricted by the caller's
        filter arguments.
        This function returns the first twenty compliant records.
    """
    
    tmdbsimple.API_KEY = tmdb_api_key
    search = tmdbsimple.Search()
    
    try:
        search.movie(query=title_query, primary_release_year=primary_release_year, year=year,
                     language=language, include_adult=include_adult, region=region, timeout=TIMEOUT)

    except requests.exceptions.HTTPError as exc:
        if (exc.args[0][:38]) == '401 Client Error: Unauthorized for url':
            msg = f"API Key error: {exc.args[0][:38]}"
            logging.error(msg)
            raise TMDBAPIKeyException(msg) from exc

        else:
            logging.error(exc)
            raise
    
    except requests.exceptions.ConnectionError as exc:
        msg = f"Unable to connect to TMDB. \n{exc.args[0].args[0]}"
        logging.info(msg)
        raise TMDBConnectionTimeout(msg) from exc

    else:
        return search.results


def get_tmdb_movie_info(tmdb_api_key: str, tmdb_movie_id: str) -> dict[str, Union[str, list[str]]]:
    """
    Retrieve the details of a movie using its TMDB id.

    Args:
        tmdb_api_key: TMDB's API key.
        tmdb_movie_id: The movie's TMDB id.

    Raises:
        TMDBAPIKeyException:
            API Key error.
        TMDBMovieIDMissing:
            A TMDB movie cannot be found although it is known to have formerly existed.
        TMDBConnectionTimeout:
            Unable to connect to TMDB

    Returns:
        A dict representation of the JSON returned from the API. This may include any or none of the
        following keys. The list is partial and does not include keys which are not of interest to
        this program at the time of writing.

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
        director(s)
    """

    movie_info = _get_tmdb_movie_info(tmdb_api_key, tmdb_movie_id)
    directors = _get_tmdb_directors(tmdb_api_key, tmdb_movie_id)
    movie_info.update(directors)
    return movie_info


class TMDBException(Exception):
    """Base class for tmdb exceptions."""
    
    
class TMDBAPIKeyException(TMDBException):
    """Exception raised for problems with the TMDB API Key"""
    
    
class TMDBMovieIDMissing(TMDBException):
    """ Exception raised if a TMDB movie was not found although it is known to have formerly existed. """
    
    
class TMDBNoRecordsFound(TMDBException):
    """No compliant records were found."""
    
    
class TMDBConnectionTimeout(TMDBException):
    """Failed to establish a new connection."""


def _get_tmdb_directors(tmdb_api_key: str, tmdb_movie_id: str) -> dict[str, list[str]]:
    """
    Retrieve the directors of a movie using its TMDB id.

    Args:
        tmdb_api_key: The TMDB API key
        tmdb_movie_id: The movie's TMDB id.

    Raises:
        TMDBAPIKeyException:
            API Key error.
        TMDBMovieIDMissing:
            A TMDB movie cannot be found although it is known to have formerly existed.
        TMDBConnectionTimeout:
            Unable to connect to TMDB

    Returns:
        A dictionary item with a key of 'Directors' and a value which is a list of directors.
    """

    tmdb_key = 'Director'
    tmdbsimple.API_KEY = tmdb_api_key
    movie = tmdbsimple.Movies(tmdb_movie_id)

    # noinspection DuplicatedCode
    try:
        movie_credits = movie.credits(timeout=TIMEOUT)

    except requests.exceptions.HTTPError as exc:
        # Incorrect API key
        if (exc.args[0][:38]) == '401 Client Error: Unauthorized for url':
            msg = f"API Key error: {exc.args[0]}"
            logging.error(msg)
            raise TMDBAPIKeyException(msg) from exc

        # Movie not found. Since this movie id originated from TMDB this is unexpected.
        # As of 1/5/2021 the TMDB URL ends with movie/XXX where XXX is the requested tmdb_id code.
        if (exc.args[0][:36]) == '404 Client Error: Not Found for url:':
            msg = f"The TMDB id '{tmdb_movie_id}' was not found on the TMDB site. \n{exc.args[0]}"
            logging.error(msg)
            raise TMDBMovieIDMissing(msg) from exc

        else:
            logging.error(exc)
            raise

    except requests.exceptions.ConnectionError as exc:
        msg = f"Unable to connect to TMDB. {exc.args[0].args[0]}"
        logging.info(msg)
        raise TMDBConnectionTimeout(msg) from exc

    else:
        crew = movie_credits['crew']
        directors = [person.get('name') for person in crew if person.get('job') == tmdb_key]
        return {tmdb_key: directors}

    
def _get_tmdb_movie_info(tmdb_api_key: str, tmdb_movie_id: str) -> dict:
    """
    Retrieve the details of a movie using its TMDB id.

    Args:
        tmdb_api_key: The TMDB API key
        tmdb_movie_id: The movie's TMDB id.

    Raises:
        TMDBAPIKeyException:
            API Key error.
        TMDBMovieIDMissing:
            A TMDB movie cannot be found although it is known to have formerly existed.
        TMDBConnectionTimeout:
            Unable to connect to TMDB

    Returns:
        A dict representation of the JSON returned from the API. This may include any or none of the
        following keys. The list is partial and does not include keys which are not of interest to
        this program at the time of writing.

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
    if not tmdb_api_key:
        msg = 'No API key provided.'
        logging.error(msg)
        raise TMDBAPIKeyException(msg)
    
    tmdbsimple.API_KEY = tmdb_api_key
    movie = tmdbsimple.Movies(tmdb_movie_id)

    # noinspection DuplicatedCode
    try:
        return movie.info(timeout=TIMEOUT)

    except requests.exceptions.HTTPError as exc:
        # Incorrect API key
        if (exc.args[0][:38]) == '401 Client Error: Unauthorized for url':
            msg = f"API Key error: {exc.args[0]}"
            logging.error(msg)
            raise TMDBAPIKeyException(msg) from exc

        # Movie not found. Since this movie id originated from TMDB this is unexpected.
        # The TMDB URL ends with movie/XXX where XXX is the requested tmdb_id code.
        if (exc.args[0][:36]) == '404 Client Error: Not Found for url:':
            msg = f"The TMDB id '{tmdb_movie_id}' was not found on the TMDB site. \n{exc.args[0]}"
            logging.error(msg)
            raise TMDBMovieIDMissing(msg) from exc

        else:
            logging.error(exc)
            raise

    except requests.exceptions.ConnectionError as exc:
        msg = f"Unable to connect to TMDB. {exc.args[0].args[0]}"
        logging.info(msg)
        raise TMDBConnectionTimeout(msg) from exc


def _intg_test_search_by_tmdb_id(api_key):
    """Retrieve Seven Samurai."""
    movie = _get_tmdb_movie_info(api_key, '346')
    assert movie['id'] == 346
    assert movie['title'] == 'Seven Samurai'
    print(f"PASSED: Integration test of intg_test_search_by_tmdb_id.")


def _intg_test_search_movies(api_key):
    # Raise invalid API key exception
    try:
        print("Expected error message: 'API Key error:  Unauthorized for url'")
        search_movies('garbage key', 'Gobble&*()Recook !@#$')
    except TMDBAPIKeyException:
        print(f"PASSED: TMDBAPIKeyException correctly raised.")

    # Test garbage search string finds no movies
    movies = search_movies(api_key, 'Gobble&*()Recook !@#$')
    assert movies == []
    print(f"PASSED: Garbage search string correctly returned an empty list.")

    # Find movies with title matching a substring
    substring = 'The Postman Always'
    print(f"\nTitles retrived for {substring=}")
    movies = search_movies(api_key, substring)
    for movie in movies:
        print(f"{movie['id'], movie['title'], movie['release_date'][:4]}")
    print()


def _intg_test_get_directors(api_key):
    directors = _get_tmdb_directors(api_key, '2501')
    assert directors == {'Director': ['Doug Liman']}
    print(f"PASSED: intg_test_get_directors found expected director.")


def main():
    """Integration tests and usage examples."""
    api_key = input('Enter TMDB API key >>> ')
    _intg_test_search_by_tmdb_id(api_key)
    _intg_test_search_movies(api_key)
    _intg_test_get_directors(api_key)

 
if __name__ == '__main__':
    sys.exit(main())
