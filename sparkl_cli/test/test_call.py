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

Test call.
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

    def test_call_literal(self):
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

    def test_call_read(self):
        sparkl(
            "vars",
            read=[
                ("field1", "sparkl_cli/test/data/field1.int")],
            alias="pytest")

        result = sparkl(
            "call",
            "Scratch/TestCall/Test1",
            alias="pytest")

        value = result["content"][0]["content"][0]
        assert 101 == value

    def test_call_binary_file(self):
        sparkl(
            "vars",
            read=[
                ("field2", "sparkl_cli/test/data/field2.png")],
            alias="pytest")

        result = sparkl(
            "call",
            "Scratch/TestCall/Test2",
            alias="pytest")

        value = result["content"][0]["content"][0]

        # Binary arrives as base64 encoded chars:
        # "iVBORw0K...ErkJggg==".
        assert value.endswith("ggg==")

    def test_call_binary_term(self):
        sparkl(
            "vars",
            read=[
                ("field2", "sparkl_cli/test/data/field2.png")],
            alias="pytest")

        result = sparkl(
            "call",
            "Scratch/TestCall/Test4",
            alias="pytest")

        value = result["content"][0]["content"][0]

        # Erlang binary term arrives as pretty-printed string:
        # <<137,80,78,...66,96,130>>.
        assert value.endswith("66,96,130>>")
