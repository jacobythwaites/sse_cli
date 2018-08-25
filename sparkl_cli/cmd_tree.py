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
import tempfile
import subprocess


from sparkl_cli.common import get_source


def parse_args(subparser):
    """
    Adds module-specific subcommand arguments.
    """
    subparser.add_argument(
        "-i", "--include",
        type=str,
        default="folder,mix,service,field,notify,solicit,response,request,reply,consume",
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
    xsl_path = os.path.join(
        os.path.dirname(__file__),
        "resources/tree.xsl")
    subprocess.check_call([
        "xsltproc",
        "--stringparam", "include", args.include,
        xsl_path,
        src_path])


def command(args):
    """
    Gets the SPARKL source specified by path and renders
    it as an abbreviated ASCII tree.
    """
    (_handle, temp_file) = tempfile.mkstemp()
    try:
        # Get content of tempfile from local file.
        get_source(args, temp_file)
        render(args, temp_file)

    # Remove tempfile.
    finally:
        os.remove(temp_file)
