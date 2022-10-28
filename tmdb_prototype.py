"""The Movie Database API interface"""

#  Copyright (c) 2022-2022. Stephen Rigden.
#  Last modified 10/15/22, 12:37 PM by stephen.
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
                print('GOT IT!:', response['id'], response['title'], response['original_title'],
                      response['release_date'])
                print()
                for k in response.keys():
                    print(f'{k:25} {response[k]}')
            
    except KeyError:
        # NB For production code: Key errors can occur at multiple points.
        pass
