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

Set var command implementation.

Each entry in the vars dict is keyed by name. The value is a
tuple comprising ('literal', value) or ('read', value), where
the latter refers to a file containing the value.
"""
from __future__ import print_function

from sparkl_cli.common import (
    get_state,
    set_state)


def parse_args(subparser):
    """
    Adds module-specific subcommand arguments.
    """
    subparser.add_argument(
        "-c", "--clear",
        action="store_true",
        help="clear all vars (before any are set)")

    subparser.add_argument(
        "-l", "--literal",
        nargs=2,
        metavar=("name", "value"),
        action="append",
        help="literal value (e.g. -l age 35)")

    subparser.add_argument(
        "-r", "--read",
        nargs=2,
        metavar=("name", "filename"),
        action="append",
        help="read value from filename (e.g. -r contract file.pdf)")


def get_vars(args):
    """
    Gets the vars dict associated with the current session,
    or the empty dict if none are set.
    """
    state = get_state(args)
    return state.get("vars", {})


def set_vars(args, vars_dict):
    """
    Sets the vars dict associated with the current session.
    """
    state = get_state(args)
    state["vars"] = vars_dict
    set_state(args, state)


def command(args):
    """
    Optionally clears all existing vars, then sets one or more vars
    ready to be used in subsequent operation calls.

    Values can be literal, or read from a file.

    With no arguments, lists existing vars. The 'nofile' token
    indicates a file does not exist.

    If no arguments are supplied, shows current var values.
    """
    if args.clear:
        vars_dict = {}
    else:
        vars_dict = get_vars(args)

    if args.literal:
        for (name, value) in args.literal:
            vars_dict[name] = ["literal", value]

    if args.read:
        for (name, value) in args.read:
            vars_dict[name] = ["read", value]

    set_vars(args, vars_dict)

    content = []
    for var_name in sorted(vars_dict.keys()):
        [method, value] = vars_dict[var_name]
        struct = {
            "tag": var_name,
            "attr": {
                "method": method,
                "value": value
            }
        }
        content.append(struct)

    result = {
        "tag": "vars",
        "attr": {
            "count": len(vars_dict)
        },
        "content": content
    }

    return result
