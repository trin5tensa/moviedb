"""The Movie Database API interface"""

#  Copyright ©2021. Stephen Rigden.
#  Last modified 1/26/21, 7:57 AM by stephen.
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import tmdbsimple as tmdb
tmdb.API_KEY = input('TMDB API key >>> ')

# Find 'The Host', 2006
print()
search = tmdb.Search()
response = search.movie(query='The Host')
for m in search.results:
    try:
        if m['title'] == 'The Host' or m['original_title'] == 'The Host':
            print('\tinitial screen:', m['id'], m['title'])
            movie = tmdb.Movies(m['id'])
            response = movie.info()
            print('\tresponse:', response['title'], response['original_title'], response['release_date'])
            if ((response['title'] == 'The Host'
                 or response['original_title'] == 'The Host')
                    and response['release_date'][0:4] == '2006'):
                print('GOTIT:', response['id'], response['title'], response['original_title'],
                      response['release_date'])
                print()
                for k in response.keys():
                    print(f'{k:25} {response[k]}')
            
    except KeyError:
        # NB For production code: Key errors can occur at multiple points.
        pass


"""
✅0)  TMDB Project
    ------------
    ✅.0) Setup
    ✅.1) Update all copyrights
            Add this prototype to commit list
    ✅.2) Add sort to database.all_tags
 
    
✅1)  Update database schema
      ----------------------
    ✅.0) Setup.
    
    ✅.1)Add these fields to the database schema:
            tmdb_id
            original_title
            release_date. SQLAlchemy uses python's datetime.date()
            synopsis (= tmdb.overview)
        NB: genres will be added as tags

    ❌.2) Create a property 'year'.
        This will return the year from Movie.release_date if populated otherwise it will return
        Movie.year.
        Hybrid attributes:
        https://docs.sqlalchemy.org/en/14/orm/extensions/hybrid.html#defining-setters
        SQL Expressions as Mapped Attributes:
        https://docs.sqlalchemy.org/en/13/orm/mapped_sql_expr.html
        SO: using hybrid properties in a query
        https://stackoverflow.com/questions/42485423/sqlalchemy-using-hybrid-properties-in-a-query
        ❌ Complicated for margingal value.


✅2) Module tmdb.py
     --------------
    NB: This module will be called from handlers.py
    
    tmdbsimple docs
    https://github.com/celiao/tmdbsimple

        ✅.1) Create these functions:
            Search for movies
            Get data on movie specified by tmdb id
            Get directors of movie specified by tmdb id
            
        ✅.2) Handle timeouts
            https://requests.readthedocs.io/en/master/user/quickstart/#timeouts
            How does tmdbsimple implement this requests parameter?
        
        ✅.3) Write pytests for all production code
    
✅3) Save config file.
     -----------------
    
    ✅ Update config.Config to hold the session's api_key.
    ✅ Save config file to permanent storage and reload it at program start.
   
   
✅4) Call TMDB for AddMovie.
   -----------------------
    Understand how to register an additional notifee for the commit neuron.
    NB: This notifee will call TMDB from new code in handlers.py.
    
    ✅.1) Rename internal fields in guiwidgets_2.AddMovieGUI for readability
        button_enabler -> commit_button_enabler
        neuron -> commit_neuron
    
    ✅.2) Outline handlers.search_tmdb
    
    ✅.3) Outline get_tmdb_movie
    
    
5) Outline design for revised AddMovie.
   ------------------------------------
    Screen layout
    Decide what information causes calls to tmdb for compliant movie searches.
    Code for TMDB handling and presentation
    Code for handling user selection of TMDB list of compliant movies
    

6)  Migrate Edit Movie from guiwidgets.py to guiwidgets_2.py.
    ---------------------------------------------------------
    NB: This is a 'one for one' migration. There are NO changes for handling TMDB in this section.
    That will be the subject of a future issue which will not be designed until this section has been
    completed.

    .1) SearchMovieGUI. Relink handlers.py. Update pytests
    .2) SelectMovieGUI. Relink handlers.py. Update pytests
    .3) EditMovieGUI. Relink handlers.py. Update pytests
    .4) Delete guiwidgets.py and tests
    
7)  Add TMDB handling to EditMovie.
    -------------------------------
    In abeyance until EditMovie migration has been completed.
    NB: If tmdb_id is present no data will be fetched from IMDB.
        handlers.py is responsible for interrogating the database to determine tmdb_id status and
        either return data or None.
    
    QUESTION) Where exactly in handlers.py should tmdb_id status be updated?
    

#################### Loose ends

Store TMDB id in database and use it for quick lookup

Write TMDB data to database

Change to YYYY-MM-DD format.  ?Change it where exactly

Should a failed internal database search lead to a TMDB search?  ..YES but not part of this project.

Bulk update on startup. NO
"""