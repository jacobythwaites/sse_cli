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

Show object command implementation.
"""
from __future__ import print_function

from sparkl_cli.common import (
    get_current_folder,
    get_object,
    resolve)


def parse_args(subparser):
    """
    Adds module-specific subcommand arguments.
    """
    subparser.add_argument(
        "object",
        type=str,
        help="object id or path")


def command(args):
    """
    Retrieves the specified object by path or id.
    """
    path = resolve(
        get_current_folder(args), args.object)

    return get_object(args, path)
