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

Close command implementation.
"""
from __future__ import print_function

from sparkl_cli.CliException import (
    CliException)

from sparkl_cli.common import (
    get_state,
    set_state,
    delete_cookies)


def parse_args(subparser):
    """
    Adds the module-specific subcommand arguments.
    """
    subparser.add_argument(
        "-a", "--all",
        action="store_true",
        help="close all connections")


def close_connection(args, alias):
    """
    Closes the connection  with the given alias, if already open.
    """
    state = get_state(args)
    connections = state.get("connections", {})
    if connections.get(alias):
        delete_cookies(args)
        connections.pop(alias)
        set_state(args, state)
    else:
        raise CliException(
            "No connection alias {Alias}".format(
                Alias=alias))


def command(args):
    """
    Closes the connection with the given alias, if already open.
    If --all is specified, closes all connections.
    """
    connections = get_state(args).get("connections", {})
    count = 0

    if args.all:
        for alias in connections:
            close_connection(args, alias)
            count += 1
    elif args.alias in connections:
        close_connection(args, args.alias)
        count = 1

    result = {
        "tag": "closed",
        "attr": {
            "count": count
        }
    }

    return result
