"""Observer pattern and neurons."""

#  Copyright ©2021. Stephen Rigden.
#  Last modified 3/5/21, 8:14 AM by stephen.
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
    
    def register(self, notifee: Callable):
        """Register a notifee.

        Each registered notifee: Callable will be called whenever the notify method of this class is
        called. The registered notifees will be invoked using the same arguments as were supplied to
        the notify method (cf. docs for Neuron.register)).

        Args:
            notifee: This callable will be invoked by the notify method with the arguments
            supplied to that method.
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
    """An observer that can observe multiple events. """
    
    events: Dict[Any, bool] = field(default_factory=dict, init=False, repr=False)
    
    def __call__(self, event_id: Any, state: bool):
        raise NotImplementedError
    
    def register_event(self, event_id: Any, state: bool = False):
        """Register an event
        
        Each registered notifee will be called whenever the notify method of this class is
        called. The registered notifees will be invoked using a calculated boolean argument (cf. docs
        for Observer.register)). The calculation algorithm is contained in the __call__ method of
        subclasses.
        
        Args:
            event_id: The unique id of the notifier. This is only used to distinguish between notifiers.
            state:
        """
        self.events[event_id] = state

    def notify(self, fired: bool):
        """Call every notifee.
        
        Whereas Observer.notify will accept any arguments (*args, **kwargs) the arguments to
        Neuron.notify must be restricted to a single boolean to indicate whether or not the neuron
        has fired.
        
        Args:
            fired:
        """
        super().notify(fired)


@dataclass
class AndNeuron(Neuron):
    """An observer that can observe multiple events.
    
    Use Case:
    Input forms often have multiple fields which must all be completed before the form can be accepted.
    For example, a 'Commit' button should only be active if all required fields are completed.
    This requires an observer that responds to multiple stimuli. It only reacts when each observed field
    sends True.
    
    Usage:
    1) Instantiate Neuron.
    2) Call the method 'register_event' to register the events which will be observed. It is mandatory
    to pre-register events which could notify an AddNeuron.
    3) Call the parent method 'register' to register one or more closures. Each closure will execute the
    action required in a target object (e.g. Activate a button). The target object could be another
    neuron.
    4) Call <neuron object>(<event id>, state). This will notify the registered notifees with 'True'
    if all the events are 'True' otherwise with 'False'.
    5) Call the parent method deregister to remove a notifee.
    """
    
    def __call__(self, event_id: Any, state: bool):
        """Update one event and update all notifees."""
        self.events[event_id] = state
        super().notify(all(self.events.values()))


@dataclass
class OrNeuron(Neuron):
    """An observer that can observe multiple events.
    
    Use Case:
    Input forms often have multiple fields one of which must be completed before the form can be
    accepted.
    For example, a 'Search' button should only be active if any field that can be used for the search
    is completed. This requires an observer that responds to multiple stimuli. It will react when
    any observed field sends True.
 
    Usage:
    1) Instantiate Neuron.
    2) Register events. Events which could notify an OrNeuron may be registered at any time prior to
    their use.
    3) Call the parent method 'register' to register one or more closures. Each closure will execute the
    action required in a target object (e.g. Activate a button). The target object could be another
    neuron.
    4) Call <neuron object>(<event id>, state). This will notify the registered notifees with 'True'
    if any of the events are 'True' otherwise with 'False'.
    5) Call the parent method deregister to remove a notifee.
    """
    
    def __call__(self, event_id: Any, state: bool):
        """Update one event and update all notifees."""
        self.events[event_id] = state
        super().notify(any(self.events.values()))
