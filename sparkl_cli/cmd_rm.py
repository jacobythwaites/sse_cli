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

Delete command implementation.

This works by creating a change file that deletes the
specified object.
"""
from __future__ import print_function

import posixpath

from sparkl_cli.common import (
    get_current_folder,
    resolve,
    sync_request)


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
    Deletes the specified configuration object.
    """
    path = resolve(
        get_current_folder(args), args.object)

    folder = posixpath.dirname(path)
    name = posixpath.basename(path)

    change = """
      <change>
        <delete name="{Name}"/>
      </change>
      """.format(
          Name=name)

    response = sync_request(
        args, "POST", "sse_cfg/change/" + folder,
        headers={
            "x-sparkl-transform": "gen_change",
            "Content-Type": "application/xml"},
        data=change)

    return response.json()
