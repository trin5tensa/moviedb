# TMDB Concept Spec
### Introduction
The Movie Database (TMDB) is a free on-line database with a published API. 

The TMDB feature will add the ability to automatically search TMDB and return a list of matching titles. The user will be able to select one item from the list. Selection will cause the form fields to be populated with TMDB data.

This specification outlines the proposed process and assigns functional responsibilities.

## Basic pattern

Not included in this basic pattern:
- Details of exception handling.
- Actions to handle user clearance of title field which would lead to an empty search substring.
- Actions to get API Key.
- Handling of short lengths of title field; i.e. full titles with a length <= 2 e.g. "If".
- Asynchronous handling of the internet search.
- Code to allow the user to select and populate the returned TMDB data.

NB. All function names are provisional.

### Tkinter Setup Thread
Schedule the consumer and the observer.

#### MODIFY `guiwidgets_2.AddMovieGUI.__post_init__`
- Observe changes to the title field.
  - Add a new observer of the title field.
  - Call `guiwidgets_2.AddMovieGUI.tmdb_search` when it changes.

#### NEW `guiwidgets_2.AddMovieGUI.tmdb_search`
- """Create TMDB consumer and producer events."""
  - Validation
    - Return without further processing if:
      - The title substring is empty.
      - The user has turned off TMDB lookups
  - Set up the consumer
    - Schedule polling of the work queue in Tk/Tcl's event loop via an initialization call to `guiwidgets_2.AddMovieGUI.tmdb_consumer`.
  - Set up the producer 
    - Add an asynchronous queue to `guiwidgets_2.AddMovieGUI`.
      - Add attribute `tmdb_work_queue`: queue.LifoQueue initialized to `queue.LifoQueue` if possible.
      - Otherwise set it to `None` and carry out initialization in `__post_init__`.
    - Add an event to Tk/Tcl's event loop.
    - Call is to `handler.tmdb_io_handler`.
    - Pass the title substring and work queue.

#### MODIFY `guiwidgets_2.AddMovieGUI.destroy`
- Stop polling the work queue.
  - Cancel the task in Tk/Tcl's event loop which polls the work queue.

### Tkinter Production Thread

#### NEW `handler.tmdb_io_handler`
- """Search TMDB for compliant movies."""
  - Try calling `tmdb.tmdb_producer`
  - FOR LATER ADDITION: Handle IMDB exceptions here.

#### NEW `tmdb.tmdb_producer`
- """Put compliant TMDB movies into work queue."""
  - Add new definitions to the config module.
    - Add a new TypedDict, `config.TMDBRecord` for the TMDB record: `tmdb_id, title, date, director, length, synopsis.`
    - Add a new defined type for the list of movies: `typing.NewType(TMDBSearch, list[TMDBRec])`.
  - Get the first 20 matches for title substring from TMDB
  - For each movie get the fields needed to populate the TMDBRecord.
  - Put the TMDB record into the work queue.

### Tkinter Consumer Thread

#### NEW `guiwidgets_2.AddMovieGUI.tmdb_consumer`
- """Get TMDB movies from work queue."""
  - Put a self recall onto Tk/Tcl's event loop with a delay of 250 ms.
  - Save the event queue id for deletion in `guiwidgets_2.destroy`.
  - Check the work queue and if work is present: 
    - Remove the first item. It is a LIFO queue.
    - STUB: Print it to `sysout`
    - Remove any remaining tasks and discard them. They are older and have been superseded.
