/*
 * Copyright (c) 2022. Stephen Rigden.
 * Last modified 11/5/22, 4:51 PM by stephen.
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

SELECT m.title, m.year, m.director, t.tag
FROM movie_tag
JOIN movies m on m.id = movie_tag.movies_id
JOIN tags t on t.id = movie_tag.tags_id
ORDER BY m.title