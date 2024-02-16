""" Test patterns.py """
#  Copyright (c) 2023-2024. Stephen Rigden.
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


from pytest_check import check

import patterns


# noinspection PyMissingOrEmptyDocstring
class TestObserver:
    def test_observer(self):
        foo1_calls = []
        foo2_calls = []
        argus = ("arg1", "arg2")
        kwargus = {"kwarg1": "kwarg1", "kwarg2": "kwarg2"}

        def foo1(*args, **kwargs):
            foo1_calls.append((args, kwargs))

        def foo2(*args, **kwargs):
            foo2_calls.append((args, kwargs))

        observer = patterns.Observer()
        observer.register(foo1)
        observer.register(foo2)

        observer.notify(*argus, **kwargus)
        observer.deregister(foo2)
        observer.notify(*argus, **kwargus)

        #  Test correct registration and notification.
        check.equal(
            foo1_calls,
            [
                (("arg1", "arg2"), {"kwarg1": "kwarg1", "kwarg2": "kwarg2"}),
                (("arg1", "arg2"), {"kwarg1": "kwarg1", "kwarg2": "kwarg2"}),
            ],
        )
        #  Test correct deregistration.
        check.equal(
            foo2_calls,
            [(("arg1", "arg2"), {"kwarg1": "kwarg1", "kwarg2": "kwarg2"})],
        )
