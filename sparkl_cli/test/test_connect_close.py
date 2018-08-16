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

Test module tests connect and close.
"""
import os
import pytest

from sparkl_cli.main import sparkl

TEST_SSE = os.environ.get("TEST_SSE")


class Tests():

    def test_close_all(self):
        result = sparkl(
            "close",
            all=True)
        assert result["tag"] == "closed"

    def test_connect_1(self):
        result = sparkl(
            "connect")
        assert result["tag"] == "connections"

    def test_connect_2(self):
        result = sparkl(
            "connect",
            url=TEST_SSE)
        assert result["tag"] == "pong"

    def test_close(self):
        result = sparkl("close")
        assert result["tag"] == "closed"
