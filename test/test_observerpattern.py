"""Test module."""

#  Copyright© 2019. Stephen Rigden.
#  Last modified 11/24/19, 12:40 PM by stephen.
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
