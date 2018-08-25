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

Change folder command implementation.
"""
from __future__ import print_function

import posixpath

from sparkl_cli.CliException import (
    CliException)

from sparkl_cli.common import (
    get_current_folder,
    get_object,
    get_connection,
    put_connection)


def parse_args(subparser):
    """
    Module-specific subcommand arguments.
    """
    subparser.add_argument(
        "folder",
        nargs="?",
        type=str,
        help="folder to move into relative to current folder")


def command(args):
    """
    Shows the current folder if no argument supplied, otherwise
    changes to the specified folder.
    """
    current = get_current_folder(args)
    if args.folder:
        cwd = posixpath.normpath(
            posixpath.join(current, args.folder))
    else:
        cwd = current

    folder = get_object(args, cwd)
    if folder and folder["tag"] in ["folder", "mix"]:
        connection = get_connection(args)
        connection["cwd"] = cwd

        if cwd != current:
            put_connection(args, connection)

        return {
            "tag": folder["tag"],
            "attr": {
                "path": cwd}}

    raise CliException(
        "No folder {Folder}".format(
            Folder=cwd))
