"""The Movie Database API interface"""

#  Copyright ©2020. Stephen Rigden.
#  Last modified 12/18/20, 8:25 AM by stephen.
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
# tmdb.API_KEY = '3eb1b9746e3631d41b5ce880dbd47b20'
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
0)  TMDB Project
    ------------
    ✅.0) Setup
    ✅.1) Update all copyrights
            Add this prototype to commit list
    ✅.2) Add sort to database.all_tags
    
1)  Update database schema
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
        

2) Module tmdb.py
   --------------
    NB: This module will be called from handlers.py
    
    tmdbsimple docs
    https://github.com/celiao/tmdbsimple

    .1) Create data dataclass for tmdb data as defined in yield from get_tmdb_data.
    
    .2) Create the function: get_tmdb_data(title, year, request_api). Write integration tests with TMDB.
        request_api: GUI which will allow user to enter the API key.
        Raises:
            Invalid year format.
            Invalid API key.
            No compliant records.
            Multiple compliant records.
    
        .1) Validate the year.
        Review the following in light of SQLAlchemy's use of pythons datetime.date() for its Date type.
            It may be easier just to stay within python's datetime module. Or it may not.
        The year can be four digit year or tmdb's YYYY-MM-DD format.
        Validate the year is a four digit integer or a valid YYYY-MM-DD date.
        (See Kenneth Reitz's maya at https://github.com/timofurrer/maya for datetime package)
        
        .2) Get API key from config.Config and, if not present, get the key from the user and
        store it in config.Config.
        
        .3) Return these fields
        tmdb_id
        title
        original_title
        release_year (YYYY)
        release_date (YYYY-MM_DD)
        runtime
        overview
        genres. List of strings Consider using these as tags.
        Raise no match and multiple matches as exceptions.
        
        .4) Write pytests for all production code
    
3) Save config file.
   -----------------
    Update config.Config to hold the session's api_key.
    Save config file to permanent storage and reload it at program start.
   
4) Call TMDB for AddMovie.
   -----------------------
    Understand how to register an additional notifee for the commit neuron.
    NB: This notifee will call TMDB from new code in handlers.py.
    
    .1) Rename internal fields in guiwidgets_2.AddMovieGUI for readability
        button_enabler -> commit_button_enabler
        neuron -> commit_neuron
        
    .2) Create TMDB call stub in handlers.py.
        Write code to call TMDB when title and year have been completed.
        Test integration between guiwidgets_2 and handlers.py.
    
    .3) Handle exceptions raised by tmdb.py
        Write pytests for the new code.
    
    .4) Add fields to GUI form:
        original_title
        overview
        Write pytests for new code.
    
    .5) Populate specified fields from TMDB data.
        Fields: director, length, original_title, overview
        Write pytests for new code.
    
    .6) Write fields to database.
    
    .7) Select tags with genre names from TMDB data.
     
        .1) The Tags SQL table will need to be updated with missing tags.
        
        .2) The tags will need to be added to the Tk treeview and selected.
        
        .3) The tags will need to be selected.
        
        .4) Write pytests.

5)  Migrate Edit Movie from guiwidgets.py to guiwidgets_2.py.
    ---------------------------------------------------------
    NB: This is a 'one for one' migration. There are NO changes for handling TMDB in this section.
    That will be the subject of a future issue which will not be designed until this section has been
    completed.

    .1) SearchMovieGUI. Relink handlers.py. Update pytests
    .2) SelectMovieGUI. Relink handlers.py. Update pytests
    .3) EditMovieGUI. Relink handlers.py. Update pytests
    .4) Delete guiwidgets.py and tests
    
6)  Add TMDB handling to EditMovie.
    -------------------------------
    In abeyance until EditMovie migration has been completed.
    NB: If tmdb_id is present no data will be fetched from IMDB.
        handlers.py is responsible for interrogating the database to determine tmdb_id status and
        either return data or None.
    
    TODO) Where exactly in handlers.py is tmdb_id status updated?
    

#################### Loose ends

Store TMDB id in database and use it for quick lookup

Write TMDB data to database

Change to YYYY-MM_DD format.

Should a failed internal database serch lead to a TMDB search?  ..YES but not part of this project.

Bulk update on startup. NO
"""