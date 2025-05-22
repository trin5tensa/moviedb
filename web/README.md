Web1 Project Concept Statement
=
Introduction
-
This project will replace the tmdbsimple package with the requests package 
and extend the capabilities of the TMDB interface.

Sub projects
-

### Replace tmdbsimple package.
- Learn REST (Representational State Transfer).
- Create a prototype module to access the TMDB API using the requests package.
- Extend the prototype to recreate the internal API for access from other 
moviedb modules.
- Code and test a new `web.tmdb.py` to replace `tmdb.py`
- Delete TMDB Exceptions module. See now superseded issue #524.

### Convert threaded tmdb.py to python async.
- Revise principles of python async.
- Select async equivalent of requests. This will be aiohttp or similar.
- Create a prototype async module to access the TMDB API.
- Extend the prototype to recreate the internal API for access from other 
moviedb modules.
- Code and test a new `web.aiotmdb.py` to replace `web.tmdb.py`.

### Improve TMDB search criteria.

- Improve TMDB search criteria. This will depend on the API of TMDB and 
the criteria available in moviedb.

### Automatically identify movie stars.
- How to identify a movie's stars? Review data available from the TMDB API. 
Check the TMDB tech forum for suggestions.
- Create a protoype for extracting stars for a move from TMDB

### Bugs and clean up.
- Bugs
- Todos
- Delete README.md