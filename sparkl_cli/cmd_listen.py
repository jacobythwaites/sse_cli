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

Listen command implementation.
"""
from __future__ import print_function

import json

from sparkl_cli.common import (
    get_current_folder,
    get_websocket,
    resolve)

PATH_PREFIX = "sse_listen/websocket/"


def parse_args(subparser):
    """
    Adds module-specific subcommand arguments.
    """
    subparser.add_argument(
        "subject",
        type=str,
        nargs='?',
        default='.',
        help="path or id of configuration object. By default: /")


def listener(connected_ws):
    """
    Generator that yields the structured data received on the opened
    websocket.
    """
    try:
        for message in connected_ws:
            term = json.loads(message)
            yield term

    # Socket close or keyboard interrupt stop the generator.
    except BaseException:
        pass


def command(args):
    """
    Opens a websocket listening to the configuration subject, and
    returns a generator that yields the structured data received
    on the websocket.
    """
    path = resolve(
        get_current_folder(args), args.subject)

    ws_path = PATH_PREFIX + path
    ws = get_websocket(args, ws_path)
    generator = listener(ws)
    return generator
