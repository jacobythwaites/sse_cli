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

Open command implementation.
"""
from __future__ import print_function

from sparkl_cli.CliException import (
    CliException)

from sparkl_cli.common import (
    get_state,
    set_state,
    sync_request)


def parse_args(subparser):
    """
    Module-specific subcommand arguments.
    """
    subparser.add_argument(
        "-v", "--verify",
        type=str,
        default=True,
        help="""
            (https only) path to sse CA certificate if required,
            or 'false' to disable certificate validation.
            """)

    subparser.add_argument(
        "url",
        nargs="?",
        type=str,
        help="URL of a SPARKL node, e.g. http://localhost:8000")


def get_connections(args):
    """
    Shows connections, if any.
    """
    state = get_state(args)
    connections = state.get("connections", {})
    count = len(connections)

    content = []
    if count > 0:
        for alias in connections:
            connection = connections[alias]
            url = connection["url"]
            verify = connection["verify"]
            item = {
                "tag": "connection",
                "attr": {
                    "alias": alias,
                    "url": url,
                    "verify": verify
                }
            }
            content.append(item)

    result = {
        "tag": "connections",
        "attr": {
            "count": count
        },
        "content": content
    }

    return result


def new_connection(args):
    """
    Opens a new connection with the specified alias to the host url,
    unless there is already a connection with that alias.

    Prints the ping info if connection is valid.
    Prints an error if the connection cannot be opened. This will cause
    there to be no current connection.
    """
    state = get_state(args)
    connections = state.get("connections", {})

    if args.alias in connections:
        raise CliException(
            "Alias {Alias} is already open".format(
                Alias=args.alias))

    verify = False
    if args.verify:
        if args.verify == "false":
            verify = False
        else:
            verify = args.verify

    if not verify:
        print("WARNING: SSE CERTIFICATE VALIDATION DISABLED")

    connection = {
        "url": args.url,
        "verify": verify}
    connections[args.alias] = connection
    state["connections"] = connections
    set_state(args, state)

    response = sync_request(
        args, "GET", "sse/ping")

    if response:
        node = response.json()["attr"]["node"]
        connection["node"] = node
        set_state(args, state)
        return response.json()

    connections.pop(args.alias, None)
    set_state(args, state)
    raise CliException(
        "No SPARKL at {Url}".format(
            Url=args.url))


def command(args):
    """
    Opens a new connection if url is specified, otherwise shows
    existing connections if any.
    """
    if args.url:
        return new_connection(args)

    return get_connections(args)
