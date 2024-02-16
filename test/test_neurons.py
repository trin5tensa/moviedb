"""Test module."""

#  Copyright (c) 2020-2024. Stephen Rigden.
#  Last modified 2/16/24, 9:16 AM by stephen.
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

from contextlib import contextmanager

import neurons


# noinspection PyMissingOrEmptyDocstring
class TestObserver:
    notify_calls = []

    def test_observer_object_created(self):
        with self.observer_context() as observer:
            assert observer == neurons.Observer()

    def test_notifee_registered(self):
        with self.observer_context() as observer:
            observer.register(self.notify)
            assert observer.notifees[0] == self.notify

    def test_notifee_deregistered(self):
        with self.observer_context() as observer:
            observer.notifees = [self.notify]
            observer.deregister(self.notify)
            assert observer.notifees == []

    def test_notifee_notified(self):
        with self.observer_context() as observer:
            observer.register(self.notify)
            args = ("test arg",)
            kwargs = dict(test_kwarg="test kwarg")
            observer.notify(*args, **kwargs)
            assert self.notify_calls[0] == (args, kwargs)

    @contextmanager
    def observer_context(self):
        # noinspection PyTypeChecker
        yield neurons.Observer()

    def notify(self, *args, **kwargs):
        self.notify_calls.append(
            (args, kwargs),
        )


class TestBaseNeuron:
    def test_event_registered(self):
        neuron = neurons.Neuron()
        neuron.register_event("event")
        assert neuron.events == dict(event=False)


class TestORNeuron:
    def test_neuron_invocation(self):
        calls = []
        neuron = neurons.OrNeuron()
        neuron.register_event("event1", False)
        neuron.register_event("event2", False)
        neuron.register(lambda state: calls.append(state))
        neuron("event2", True)
        assert calls[0] is True
