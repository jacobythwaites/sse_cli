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

Test rest service implementation.
"""
from __future__ import print_function

import threading
import time
import os
import pytest

import sys

from sparkl_cli.main import sparkl

"""
Need to load the test_rest.py implementation module from test/data.
"""
sys.path.append("sparkl_cli/test/data")

TEST_SSE = os.environ.get("TEST_SSE")
TEST_USER = os.environ.get("TEST_USER")
TEST_PASS = os.environ.get("TEST_PASS")


class Tests():
    """
    Note that all sparkl calls use the connection alias "pytest_session"
    or "pytest_nosession".
    This avoids conflict with any manual testing occurring on
    the command line.
    """
    def setup_method(self):

        # Session connection has login.
        sparkl(
            "connect",
            TEST_SSE,
            alias="pytest_session")

        # Separate no-session connection has no login.
        sparkl(
            "connect",
            TEST_SSE,
            alias="pytest_nosession")

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
            all=True,
            alias="pytest_session")

        sparkl(
            "close",
            all=True,
            alias="pytest_nosession")

    def test_sync_impl(self):

        # Load the external service implementation module.
        service = sparkl(
            "service",
            "Scratch/TestRest/REST",
            "test_rest",
            alias="pytest_session")

        solicit = {
            "solicit": "Mix/CheckPrime",
            "data": {
                "n": 13
            }
        }

        response = service.solicit(
            solicit)

        # Consume occurs in its own good time.
        time.sleep(1)

        assert response["response"] == "Yes"
        assert len(service.module.consumes) == 1

    def test_async_impl(self):

        # Load the external service implementation module.
        service = sparkl(
            "service",
            "Scratch/TestRest/REST",
            "test_rest",
            alias="pytest_session")

        solicit = {
            "solicit": "Mix/CheckPrime",
            "data": {
                "n": 13
            }
        }

        result = {}
        cv = threading.Condition()

        def callback(response):
            cv.acquire()
            result["response"] = response
            cv.notify()
            cv.release()

        cv.acquire()
        service.solicit(
            solicit, callback=callback)
        cv.wait(1)
        cv.release()

        assert result["response"]["response"] == "Yes"

    def test_no_session_impl(self):

        # Load the service implementation module with no session.
        service = sparkl(
            "service",
            "admin@sparkl.com/Scratch/TestPublicRest/REST",
            "test_rest",
            alias="pytest_nosession")

        solicit = {
            "solicit": "Mix/CheckPrime",
            "data": {
                "n": 13
            }
        }

        result = {}
        cv = threading.Condition()

        def callback(response):
            cv.acquire()
            result["response"] = response
            cv.notify()
            cv.release()

        cv.acquire()
        service.solicit(
            solicit, callback=callback)
        cv.wait(1)
        cv.release()

        assert result["response"]["response"] == "Yes"

    def test_close_invoked(self):

        # Load the close test implementation.
        service = sparkl(
            "service",
            "admin@sparkl.com/Scratch/TestPublicRest/REST",
            "test_close",
            alias="pytest_nosession")

        notify = {
            "notify": "Mix/Notify"}

        service.notify(
            notify)

        # Close occurs in separate thread.
        time.sleep(1)

        assert service.properly_closed
