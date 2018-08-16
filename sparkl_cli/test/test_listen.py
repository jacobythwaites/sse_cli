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

Test websocket listen.
"""
from __future__ import print_function

import os
import pytest

from sparkl_cli.main import sparkl

TEST_SSE = os.environ.get("TEST_SSE")
TEST_USER = os.environ.get("TEST_USER")
TEST_PASS = os.environ.get("TEST_PASS")


class Tests():
    """
    Note that all sparkl calls use the connection alias "pytest".
    This avoids conflict with any manual testing occurring on
    the command line.
    """

    def setup_method(self):
        sparkl(
            "connect",
            TEST_SSE,
            alias="pytest")

        sparkl(
            "login",
            TEST_USER,
            TEST_PASS,
            alias="pytest")

        sparkl(
            "put",
            "sparkl_cli/test/data/TestCall.xml",
            "Scratch",
            alias="pytest")

        # Listen to the sequencer using 'events' prop on this object.
        self.events = sparkl(
            "listen",
            "Scratch/TestCall/Sequencer",
            alias="pytest")

    def teardown_method(self):
        sparkl(
            "rm",
            "Scratch/TestCall",
            alias="pytest")

        sparkl(
            "logout",
            alias="pytest")

        sparkl(
            "close",
            all=True,
            alias="pytest")

    def test_events_occur(self):
        sparkl(
            "vars",
            literal=[
                ("field1", 100)])

        result = sparkl(
            "call",
            "Scratch/TestCall/Test1",
            alias="pytest")

        value = result["content"][0]["content"][0]
        assert 100 == value

        # At least 4 events should have occurred.
        for n in range(1, 4):
            event = next(self.events)
            assert type(event).__name__ == "dict"
