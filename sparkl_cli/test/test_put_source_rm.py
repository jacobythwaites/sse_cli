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

Test source functions.
"""
from __future__ import print_function

import os
import types
import glob
import xml.dom.minidom
from shutil import copyfile
from multiprocessing import Process
from time import sleep
import http.server
import socketserver
import requests

from sparkl_cli.main import sparkl
from sparkl_cli.common import mktemp_pathname

TEST_SSE = os.environ.get("TEST_SSE")
TEST_USER = os.environ.get("TEST_USER")
TEST_PASS = os.environ.get("TEST_PASS")

TEST_ALIAS = "pytest"
PATH_TO_TEST_DATA = "sparkl_cli/test/data"
PRIMES_FILE_PATH = "sparkl_cli/test/data/Primes.xml"
TEST_CALL_FILE_PATH = "sparkl_cli/test/data/TestCall.xml"
PRIMES_SPARKL_PATH = "Scratch/Primes"
TEST_CALL_SPARKL_PATH = "Scratch/TestCall"


class Tests():

    def setup_method(self):
        sparkl(
            "connect",
            TEST_SSE,
            alias=TEST_ALIAS)

        sparkl(
            "login",
            TEST_USER,
            TEST_PASS,
            alias=TEST_ALIAS)

    def teardown_method(self):
        sparkl(
            "logout",
            alias=TEST_ALIAS)
        sparkl(
            "close",
            all=True,
            alias=TEST_ALIAS)
        for tmp in glob.glob("tmp*.*"):
            os.remove(tmp)

    def test_put(self):
        result = sparkl(
            "put",
            PRIMES_FILE_PATH,
            "Scratch",
            alias=TEST_ALIAS)

        assert result["tag"] == "change"

    def test_put_url(self, httpserver):
        """
        Note the dependency on the pytest funcargs library
        pytest_localserver.
        """
        httpserver.serve_content(
            open(TEST_CALL_FILE_PATH).read())

        result = sparkl(
            "put",
            httpserver.url + "/TestCall.xml",
            "Scratch",
            alias=TEST_ALIAS)

        assert result["tag"] == "change"
        scratch_folders = sparkl(
            "ls",
            "Scratch",
            alias=TEST_ALIAS)["content"]
        assert any(folder["attr"]["name"] == "TestCall"
                   for folder in scratch_folders)

    def test_source_xml(self):
        result = sparkl(
            "source",
            PRIMES_SPARKL_PATH,
            alias=TEST_ALIAS)
        parsed = xml.dom.minidom.parseString(result)
        assert parsed.firstChild.localName == "folder"

    def test_source_save(self):
        result = sparkl(
            "source",
            PRIMES_SPARKL_PATH,
            output="tmp.xml",
            alias=TEST_ALIAS)
        parsed = xml.dom.minidom.parse("tmp.xml")
        assert parsed.firstChild.localName == "folder"

    def test_render(self):
        result = sparkl(
            "render",
            PRIMES_SPARKL_PATH,
            output="tmp.html",
            alias=TEST_ALIAS)
        with open("tmp.html", "r") as html_file:
            line = html_file.readline()
        assert line == "<html>\n"

    def test_local_render(self):
        result = sparkl(
            "render",
            PRIMES_FILE_PATH,
            file=True,
            output="tmp.html",
            alias=TEST_ALIAS)
        with open("tmp.html", "r") as html_file:
            line = html_file.readline()
        assert line == "<html>\n"

    def test_render_monitor(self):
        result = sparkl(
            "render",
            PRIMES_FILE_PATH,
            file=True,
            alias=TEST_ALIAS,
            watch=True)
        assert isinstance(result, types.GeneratorType)

    def test_render_local_monitor(self):

        # Create temporary file and copy Primes into it
        temp_path = mktemp_pathname(".xml")
        copyfile(PRIMES_FILE_PATH, temp_path)

        # Start monitoring in a separate process
        monitor_process = Process(target=sparkl,
                                  args=("render", temp_path),
                                  kwargs={"alias": TEST_ALIAS,
                                          "watch": True,
                                          "file": True,
                                          "output": "tmp.html",
                                          "interval": 1})
        monitor_process.start()

        # Copy the content of the test call mix into the temp file
        copyfile(TEST_CALL_FILE_PATH, temp_path)
        sleep(2)

        # Stop monitoring process
        monitor_process.terminate()

        # Check if the output file was updated
        with open("tmp.html", 'r') as data:
            assert "TestCall" in data.read()

        # Get rid of the temporary file
        os.remove(temp_path)

    def test_rm(self):
        for test_file in [PRIMES_SPARKL_PATH, TEST_CALL_SPARKL_PATH]:
            result = sparkl(
                "rm",
                test_file,
                alias=TEST_ALIAS)
            print(result)
            assert result["tag"] == "change"
