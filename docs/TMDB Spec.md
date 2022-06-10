# TMDB Concept Spec
### Introduction
The Movie Database (TMDB) is a free on-line database with a published API. 

The TMDB feature will add the ability to automatically search TMDB and return a list of matching titles. The user will be able to select one item from the list. Selection will cause the form fields to be populated with TMDB data.

This specification outlines the proposed process and assigns functional responsibilities.

## Basic pattern

Not included in this basic pattern:
- Details of exception handling.
- Actions to get API Key.
- Asynchronous handling of the internet search.
- Code to allow the user to select and populate the returned TMDB data.

NB. All function names are provisional.

### Tkinter Setup Thread
Schedule the consumer and the observer.

#### MODIFY `guiwidgets_2.AddMovieGUI.__post_init__`
Completed.
- Observe changes to the title field.
  - Add a new observer of the title field.
  - Call `guiwidgets_2.AddMovieGUI.tmdb_search` when it changes.

#### MODIFY `guiwidgets_2.AddMovieGUI.__post_init__`
Issue #267
- Add an asynchronous queue to `guiwidgets_2.AddMovieGUI`.
  - Add attribute `tmdb_work_queue`: queue.LifoQueue initialized to `queue.LifoQueue` if possible.
  - Otherwise set it to `None` and carry out initialization in `__post_init__`.

#### NEW STUB `guiwidgets_2.AddMovieGUI.tmdb_consumer`
Issue #268 """Consume movies placed in the work queue."""
- Initiate the polling of the work queue. 
  - Create a stub guiwidgets_2._tmdb_consumer
  - In `guiwidgets_2.AddMovieGUI.__post_init__` schedule a call to the stub via the event loop
  - Put a self recall onto Tk/Tcl's event loop with a delay of 250 ms.
  - Save the event queue id for deletion in `guiwidgets_2.destroy`.
  - Add a 'Rescheduled tmdb_consumer called' print statement.
- Stop polling the work queue.
  - Cancel the task in Tk/Tcl's event loop which polls the work queue.

#### NEW `guiwidgets_2.AddMovieGUI.tmdb_search`
Issue #269 """Create TMDB producer events."""
- Create the stub function `handler.tmdb_io_handler`.
  - Pass this function in the constructor of `guiwidgets_2.AddMovieGUI`.
- Validation
  - Return without further processing if the title substring is empty.
- Introduce a time delay to avoid premature search invocation.
  - Add an event to Tk/Tcl's event loop.
  - Place a tkinter delayed event call to `handler.tmdb_io_handler`. The delay is 1s.
- Call the producer
  - Delete the delayed event call if a following key press arrives in less than 1s.
  - Pass the title substring and work queue to `handler.tmdb_io_handler`.

### Tkinter Production Thread

#### NEW `handler.tmdb_io_handler`
- """Search TMDB for compliant movies."""
  - Try calling `tmdb.tmdb_producer`
  - FOR LATER ADDITION: Handle IMDB exceptions here.

#### NEW `tmdb.tmdb_producer`
- """Put compliant TMDB movies into work queue."""
  - If user has turned off tmdb access return immediately.
  - Get tmdb key.
  - Add new definitions to the config module.
    - Add a new TypedDict, `config.TMDBRecord` for the TMDB record: `tmdb_id, title, date, director, length, synopsis.`
    - Add a new defined type for the list of movies: `typing.NewType(TMDBSearch, list[TMDBRec])`.
  - Get the first 20 matches for title substring from TMDB
  - For each movie get the fields needed to populate the TMDBRecord.
  - Put the TMDB record into the work queue.

### Tkinter Consumer Thread

#### `guiwidgets_2.AddMovieGUI.tmdb_consumer`
- """Get TMDB movies from work queue."""
  - Check the work queue and if work is present: 
    - Remove the first item. It is a LIFO queue.
    - STUB: Print it to `sysout`
    - Remove any remaining tasks and discard them. They are older and have been superseded.
