This readme explains how the handlers module will be refactored for DB1.

M2-Movies-2024/handlers.py
The original module which will be retained until DB1 is fully implemented and operational.

M2-Movies-2024/gui_handlers/handlers.py
This started life as a simple copy of M2-Movies-2024/handlers.py.
Code will be deleted from here as its functionality is migrated to guidatabase.py

M2-Movies-2024/gui_handlers/guidatabase.py
This is the new primary handler for managing GUI and database interactions.

M2-Movies-2024/gui_handlers/moviebagfacade.py
This is subclass of moviebag with constructor methods which create a MovieBag()
using the obsolescent typed dicts from the config module.
It will become obsolete itself as soon as the GUI modules are upgraded to use
movie bags.