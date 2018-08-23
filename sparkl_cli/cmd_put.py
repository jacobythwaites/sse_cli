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

import requests
import tempfile
import subprocess

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
        help="file name containing XML to upload")

    subparser.add_argument(
        "folder",
        type=str,
        help="folder id or path, into which the change is placed")


def is_url(path):
    prefixes = ['www', 'http://', 'https://', 'file://', 'ftp://']
    return any(path.startswith(prefix) for prefix in prefixes)


def command(args):
    """
    Uploads SPARKL source or other valid XML change file.
    """
    to_delete = False
    upload_file = args.file
    print('Path at start: {}'.format(upload_file))

    if is_url(args.file):
        response = requests.get(args.file)
        _handle, temp_path = tempfile.mkstemp(suffix='.xml')
        upload_file = temp_path
        print('Temp path: {}'.format(upload_file))
        to_delete = True
        with open(upload_file, 'w') as content:
            content.write(response.text)

    with open(upload_file, "rb") as upload_content:
        path = resolve(
            get_current_folder(args), args.folder)

        response = sync_request(
            args, "POST", "sse_cfg/change/" + path,
            headers={
                "x-sparkl-transform": "gen_change",
                "Content-Type": "application/xml"},
            data=upload_content)

        if to_delete:
            subprocess.call(['rm', upload_file])

        return response.json()
