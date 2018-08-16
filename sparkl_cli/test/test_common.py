"""
Copyright 2018 SPARKL Limited

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Test module for common.py
"""
import os

from sparkl_cli import common


# pylint: disable=too-few-public-methods
class ArgsMixin(object):
    pass


class Tests():

    def setup_method(self):
        self.args = ArgsMixin()

    def teardown_method(self):
        pass

    def test_get_working_root(self):
        result = common.get_working_root()
        assert os.path.exists(result)

    def test_get_working_dir(self):
        self.args.session = "1000"
        result = common.get_working_dir(self.args)
        assert os.path.exists(result)

    def test_garbage_collect_1(self):
        """
        Garbage collection should remove non-existent pid.
        """
        self.args.session = 123456
        working_dir = common.get_working_dir(self.args)
        assert os.path.exists(working_dir)
        common.garbage_collect()
        assert not os.path.exists(working_dir)

    def test_garbage_collect_2(self):
        """
        Garbage collection should not remove live pid.
        """
        self.args.session = os.getppid()
        working_dir = common.get_working_dir(self.args)
        assert os.path.exists(working_dir)
        common.garbage_collect()
        assert os.path.exists(working_dir)

    def test_get_state(self):
        self.args.session = 1000
        state = common.get_state(self.args)
        assert {} == state

    def test_set_state(self):
        self.args.session = os.getppid()
        state = {
            "connections": {
                "foo": {
                    "url": "some url"}}}
        common.set_state(self.args, state)
        result = common.get_state(self.args)
        assert state == result
