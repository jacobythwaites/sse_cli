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

Node information implementation.
"""
from __future__ import print_function

from sparkl_cli.common import (
    get_connection,
    sync_request)


def parse_args(subparser):
    """
    Adds module-specific subcommand arguments.
    """
    subparser.add_argument(
        "node",
        type=str,
        nargs="?",
        help="internal node name, such as node3@10.0.0.1")


def command(args):
    """
    Administrator only.

    Shows information about a node, including nodes it is connected to and
    the extensions on the node.

    If no node name is specified, shows info about the node on which the
    session exists.
    """
    connection = get_connection(args)
    if args.node:
        node = args.node
    else:
        node = connection["node"]

    response = sync_request(
        args, "GET", "sse/info",
        params={"node": node})

    return response.json()
