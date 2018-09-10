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

Upload source command implementation.
"""
from __future__ import print_function

import os
import re
import tempfile
import requests


from sparkl_cli.common import (
    get_current_folder,
    resolve,
    sync_request)


def parse_args(subparser):
    """
    Adds module-specific subcommand arguments.
    """
    subparser.add_argument(
        "file",
        type=str,
        help="file path or URL to file containing XML to upload")

    subparser.add_argument(
        "folder",
        type=str,
        nargs="?",
        default=".",
        help="folder id or path, into which the change is placed")


def is_url(path):
    """
    Uses regex to check whether "path" is a URL.
    """
    try:
        _prefix = re.findall(r'^[a-z]+://', path)[0]
        return True

    except IndexError:
        return False


def command(args):
    """
    Uploads SPARKL source or other valid XML change file from local
    file system or the internet.
    """
    to_delete = None
    upload_path = args.file

    try:

        if is_url(upload_path):
            response = requests.get(upload_path)
            _handle, temp_path = tempfile.mkstemp(suffix='.xml')

            with open(temp_path, 'w') as content:
                content.write(response.text)

            upload_path = temp_path
            to_delete = temp_path

        with open(upload_path, "rb") as upload_content:
            path = resolve(
                get_current_folder(args), args.folder)

            response = sync_request(
                args, "POST", "sse_cfg/change/" + path,
                headers={
                    "x-sparkl-transform": "gen_change",
                    "Content-Type": "application/xml"},
                data=upload_content)

            return response.json()

    finally:
        if to_delete:
            os.remove(to_delete)
