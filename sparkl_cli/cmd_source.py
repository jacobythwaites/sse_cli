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

Get source command implementation.
"""
from __future__ import print_function

import os

from sparkl_cli.common import get_source, mktemp


def parse_args(subparser):
    """
    Adds module-specific subcommand arguments.
    """
    subparser.add_argument(
        "-o", "--output",
        help="write output to named local file")

    subparser.add_argument(
        "source",
        type=str,
        nargs="?",
        default=".",
        help="source path or id")


def show_source_as(args):
    """
    Retrieves the source code of a configuration either
    from the local file system or from a SPARKL instance.

    Creates a temp file to store the source code and
    optionally transforms its content into html.

    The temp file is deleted once the source code is returned.
    """

    # Create a temporary file.
    temp_file = mktemp()
    try:
        # Get content of tempfile from local file.
        get_source(args, temp_file)

        # Return content of tempfile.
        with open(temp_file, 'r') as data:
            return data.read()

    # Get rid of tempfile.
    finally:
        os.remove(temp_file)


def command(args):
    """
    Gets the SPARKL source XML specified by path. Use
    --output to have the XML output saved to a file.
    """

    # Handle -o flag
    if args.output:
        get_source(args, args.output)
        return None

    return show_source_as(args)
