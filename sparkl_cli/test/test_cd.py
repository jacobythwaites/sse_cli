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

Test current and change folder.
"""
import os
import pytest

from sparkl_cli.main import sparkl

TEST_SSE = os.environ.get("TEST_SSE")
TEST_USER = os.environ.get("TEST_USER")
TEST_PASS = os.environ.get("TEST_PASS")


class Tests():

    """
    Note that all sparkl calls use the connection alias "pytest_session".
    """
    def setup_method(self):

        # Session connection has login.
        sparkl(
            "connect",
            TEST_SSE,
            alias="pytest_session")

        sparkl(
            "login",
            TEST_USER,
            TEST_PASS,
            alias="pytest_session")

        # Load the test mixes.
        sparkl(
            "put",
            "sparkl_cli/test/data/TestRest.xml",
            "Scratch",
            alias="pytest_session")

        sparkl(
            "put",
            "sparkl_cli/test/data/TestPublicRest.xml",
            "Scratch",
            alias="pytest_session")

    def teardown_method(self):

        # Unload the test mixes
        sparkl(
            "rm",
            "Scratch/TestRest",
            alias="pytest_session")

        # Unload the test mixes
        sparkl(
            "rm",
            "Scratch/TestPublicRest",
            alias="pytest_session")

        sparkl(
            "logout",
            alias="pytest_session")

        sparkl(
            "close",
            alias="pytest_session")

    def test_cd_1(self):
        result = sparkl(
            "cd",
            alias="pytest_session")
        assert result["tag"] == "folder"
        assert result["attr"]["path"] == "/"

    def test_cd_2(self):
        result = sparkl(
            "cd",
            "Scratch",
            alias="pytest_session")
        assert result["tag"] == "folder"
        assert result["attr"]["path"] == "/Scratch"

    def test_cwd_1(self):
        result = sparkl(
            "cd",
            "Scratch",
            alias="pytest_session")

        result = sparkl(
            "ls",
            alias="pytest_session")
        assert result["tag"] == "content"
        assert result["attr"]["folder"] == "/Scratch"
