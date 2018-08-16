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

Test vars.
"""
import pytest

from sparkl_cli.main import sparkl


class Tests():

    def test_list(self):
        result = sparkl("vars")
        assert(result["tag"] == "vars")

    def test_clear_all(self):
        result = sparkl(
            "vars",
            clear=True)
        assert result["tag"] == "vars"
        assert result["attr"]["count"] == 0

    def test_set_literal(self):
        result = sparkl(
            "vars",
            literal=[
                ("foo", 1),
                ("bar", 2)
            ])
        assert result["tag"] == "vars"
        assert result["attr"]["count"] == 2
        assert len(result["content"]) == 2
        bar = result["content"][0]
        foo = result["content"][1]
        assert foo["tag"] == "foo"
        assert bar["tag"] == "bar"

    def test_replace_literal(self):
        result = sparkl(
            "vars",
            literal=[
                ("bar", 3)
            ])
        bar = result["content"][0]
        assert bar["attr"]["value"] == 3

    def test_var_insert(self):
        result = sparkl(
            "vars",
            literal=[
                ("baz", "this is baz")
            ])
        baz = result["content"][1]
        assert baz["tag"] == "baz"
