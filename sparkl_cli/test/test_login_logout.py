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

Test login and logout
"""
import os
import pytest

from sparkl_cli.main import sparkl

TEST_SSE = os.environ.get("TEST_SSE")
TEST_USER = os.environ.get("TEST_USER")
TEST_PASS = os.environ.get("TEST_PASS")


class Tests():

    def test_login(self):
        sparkl(
            "connect",
            url=TEST_SSE)
        result = sparkl(
            "login",
            user=TEST_USER,
            password=TEST_PASS)
        assert result["tag"] == "user"
        assert result["attr"]["name"] == TEST_USER

    def test_logout(self):
        result = sparkl("logout")
        sparkl("close", all=True)
        assert result["tag"] == "user"
        assert result["attr"]["name"] == "unknown@unknowndomain"
