"""Test module."""

#  Copyright© 2019. Stephen Rigden.
#  Last modified 12/24/19, 8:31 AM by stephen.
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

from contextlib import contextmanager

import observerpattern


class TestObserver:
    test_notifee_calls = None
    
    def test_observer_object_created(self):
        with self.observer_context() as observer:
            assert observer == observerpattern.Observer()
    
    def test_notifee_registered(self):
        with self.observer_context() as observer:
            observer.register(self.test_notifee)
            assert observer.notifees[0] == self.test_notifee
    
    def test_notifee_deregistered(self):
        with self.observer_context() as observer:
            observer.notifees = [self.test_notifee]
            observer.deregister(self.test_notifee)
            assert observer.notifees == []
    
    def test_notifee_notified(self):
        with self.observer_context() as observer:
            observer.register(self.test_notifee)
            args = ('test arg',)
            kwargs = dict(test_kwarg='test kwarg')
            observer.notify(*args, **kwargs)
            assert self.test_notifee_calls[0] == (args, kwargs)
    
    # noinspection PyMissingOrEmptyDocstring
    @contextmanager
    def observer_context(self):
        # noinspection PyTypeChecker
        yield observerpattern.Observer()

    def test_notifee(self, *args, **kwargs):
        if not self.test_notifee_calls:
            self.test_notifee_calls = []
        self.test_notifee_calls.append((args, kwargs), )


class TestNeuron:
    
    def test_neuron_object_created(self):
        with self.neuron_context() as neuron:
            assert neuron == observerpattern.AndNeuron()
    
    def test_event_registered(self):
        with self.neuron_context() as neuron:
            neuron.register_event('event')
            assert neuron.events == dict(event=False)
    
    def test_neuron_invocation(self):
        calls = []
        with self.neuron_context() as neuron:
            neuron.register_event('event1', True)
            neuron.register_event('event2', False)
            neuron.register(lambda state: calls.append(state))
            neuron('event2', True)
            assert calls[0] is True
    
    # noinspection PyMissingOrEmptyDocstring
    @contextmanager
    def neuron_context(self):
        yield observerpattern.AndNeuron()
