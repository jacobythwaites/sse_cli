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

Session command implementation.
"""
from __future__ import print_function

from sparkl_cli.common import (
    get_working_dir)


def parse_args(_subparser):
    """
    Adds the module-specific subcommand arguments.
    """


def command(args):
    """
    Shows the session number, which can be used by another
    process invoking `sparkl -s SESSION`.
    """
    result = {
        "tag": "session",
        "attr": {
            "id": args.session,
            "dir": get_working_dir(args)
        }
    }

    return result
