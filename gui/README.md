------------
Concept GUI3
------------

Implement support for DB1 enhancements including utilizing the new MovieBag for all data transfers. 
Carry out enhancements, debt reduction and bug fixes.

Deliverables
------------

✅Replace all the ad-hoc data structures used to move movie data between
the gui modules and the handlers.

#502 Create new gui modules inside the gui folder:
Move mainwindow.py altogether. 
Move common support functions from guiwidgets_2 to commonsupport.py.
Move odds and ends functions from guiwidgets_2 to oddends.py (about, settings, messageboxes).
Move tag functions from guiwidgets_2 to tags.py.
Move guiwidgets_2, which, by now, only contains movie code, to movies.py.

#503 Move and rewrite SelectTagGUI and SelectMovieGUI to gui.tables.py.

GUI Enhancement issues not otherwise covered in this list.

GUI Debt reduction issues not otherwise covered in this list.

GUI Bugs not otherwise covered in this list.

Remove old code

Final clean up
