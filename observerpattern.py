"""The Observer pattern and usabilty functionalit ."""

#  Copyright© 2019. Stephen Rigden.
#  Last modified 11/20/19, 7:06 AM by stephen.
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


from dataclasses import dataclass, field
from typing import Callable, List


@dataclass
class Observer:
    """The classic observer pattern.

    Usage:
    1) Instantiate Observer.
    2) Call the method register to register one or more callables (observers).
    3) Call the method notify to call all of the observers.
    4) Call the method deregister to remove a observer and stop it from being called.
    """
    
    # moviedb-#94 Test this class
    notifees: List[Callable] = field(default_factory=list)
    
    def register(self, notifee):
        """Register an observer.

        Args:
            notifee: Any callable.
        """
        self.notifees.append(notifee)
    
    def deregister(self, notifee):
        """Remove an observer.

        Args:
            notifee:
        """
        self.notifees.remove(notifee)
    
    def notify(self, *args, **kwargs):
        """Call every observer.

        Args:
            *args: Passed through as observer arguments
            **kwargs: Passed through as observer arguments
        """
        for observer in self.notifees:
            observer(*args, **kwargs)

# moviedb-#94 Implement neurons
