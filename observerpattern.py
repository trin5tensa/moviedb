"""The Observer pattern and usabilty functionality."""

#  Copyright© 2019. Stephen Rigden.
#  Last modified 12/3/19, 10:05 AM by stephen.
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
from typing import Any, Callable, Dict, List


@dataclass
class Observer:
    """The classic observer pattern.

    Usage:
    1) Instantiate Observer.
    2) Call the method register to register one or more callables.
    3) Call the method notify to call all of the notifees. This will call each registered callable with
        the arguments supplied to the notify method.
    4) Call the method deregister to remove a observer and stop it from being called.
    """
    
    notifees: List[Callable] = field(default_factory=list, init=False, repr=False)
    
    def register(self, notifee):
        """Register a notifee.

        Args:
            notifee: Any callable.
        """
        self.notifees.append(notifee)
    
    def deregister(self, notifee):
        """Remove a notifee.

        Args:
            notifee:
        """
        self.notifees.remove(notifee)
    
    def notify(self, *args, **kwargs):
        """Call every notifee.

        Args:
            *args: Passed through from triggering event.
            **kwargs: Passed through from triggering event.
        """
        for observer in self.notifees:
            observer(*args, **kwargs)


@dataclass
class Neuron(Observer):
    """An observer that can observe multiple events.
    
    Use Case:
    Input forms often have multiple fields which must be completed before the form can be accepted.
    For example, an 'OK' button should only be active if all relevant fields are completed.
    This requires an observer that responds to multiple stimuli.
    
    Usage:
    1) Instantiate Neuron.
    2) Call the method register_event to register one or more events.
    3) Call the method register to register one or more callables.
    4) Call <neuron object>(<event id>, state). This will notify the registered notifees with 'True'
    if all the events are 'True' otherwise with 'False'.
    5) Call the method deregister to remove a observer and stop it from being called.
    """
    
    events: Dict[Any, bool] = field(default_factory=dict, init=False, repr=False)
    
    def __call__(self, event_id: Any, state: bool):
        """Update one event and update all notifees."""
        self.events[event_id] = state
        super().notify(all(self.events.values()))
    
    def register_event(self, event_id: Any, state: bool = False):
        """Register an event
        
        Args:
            event_id:
            state:
        """
        self.events[event_id] = state
