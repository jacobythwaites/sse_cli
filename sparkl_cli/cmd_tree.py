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

Show text tree command implementation.
"""
from __future__ import print_function

import os

from sparkl_cli.common import get_source, mktemp_pathname, transform


def parse_args(subparser):
    """
    Adds module-specific subcommand arguments.
    """
    subparser.add_argument(
        "-a", "--all",
        action="store_true",
        help="additional information is shown for each subject line")

    subparser.add_argument(
        "-f", "--file",
        action="store_true",
        help="source path refers to local file not SPARKL object")

    subparser.add_argument(
        "-p", "--props",
        action="store_true",
        help="include props in the tree output")

    subparser.add_argument(
        "-i", "--include",
        type=str,
        default="service,field,notify,solicit,"
                "response,request,reply,consume",
        help="comma separated tags to include")

    subparser.add_argument(
        "source",
        type=str,
        nargs="?",
        default=".",
        help="source path or id")


def render(args, src_path):
    """
    Applies the tree.xsl transform on src_path to
    generate the text tree output.
    """
    tags = "mix,folder," + args.include
    if args.props:
        tags += ",prop"
    tags = "\"" + tags + "\""

    detail = "false()"
    if args.all:
        detail = "true()"

    transform(
        "resources/tree.xsl", src_path, None,
        tags=tags,
        detail=detail)


def command(args):
    """
    Renders the configuration or file source as an ASCII tree with
    optional detail. You can limit which tags are rendered, such
    as only services or fields.
    """
    if args.file:
        render(args, args.source)
        return

    temp_file = mktemp_pathname(".xml")
    try:
        get_source(args, temp_file)
        render(args, temp_file)

    # Remove tempfile.
    finally:
        os.remove(temp_file)
