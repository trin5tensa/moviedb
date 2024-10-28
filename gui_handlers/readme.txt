This readme explains how the handlers module will be refactored for DB1.

M2-Movies-2024/handlers.py
The original module which will be retained until DB1 is fully implemented and operational.

M2-Movies-2024/gui_handlers/handlers.py
This started life as a simple copy of M2-Movies-2024/handlers.py.
Functions will be removed after refactoring into guidatabase.py

M2-Movies-2024/gui_handlers/guidatabase.py
This will be the new handler for GUI and database interactions.

M2-Movies-2024/gui_handlers/moviebagfacade.py
This will have functions which can convert between the new style MovieBag objects and the variety
of old style TypedDict objects.
It will become obsolete itself as soon as the GUI modules are upgraded to use
movie bags.