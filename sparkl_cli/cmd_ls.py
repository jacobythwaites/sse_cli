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

List command implementation.
"""
from __future__ import print_function

from sparkl_cli.CliException import (
    CliException)

from sparkl_cli.common import (
    get_current_folder,
    get_object,
    resolve,
    sync_request)


def parse_args(subparser):
    """
    Adds module-specific subcommand arguments.
    """
    subparser.add_argument(
        "folder",
        type=str,
        nargs="?",
        default=".",
        help="folder or service")


def command(args):
    """
    If a folder is specified, lists the folder contents, where each line
    shows the type, id and name of a folder entry.

    If a service is specified, lists the service instances, where each
    line shows an instance with its id.
    """
    path = resolve(
        get_current_folder(args), args.folder)

    record = get_object(args, path)

    if not record:
        raise CliException(
            "No object {Path}".format(
                Path=path))

    result = {
        "tag": "content",
        "attr": {
            record["tag"]: path,
            "count": 0
        },
        "content": []
    }

    response = sync_request(
        args, "GET", "sse_cfg/content/" + path)

    content = response.json().get("content", [])
    result["attr"]["count"] = len(content)

    for item in content:
        item_tag = item["tag"]
        item_id = item["attr"]["id"]
        item_name = item["attr"].get("name", "n/a")
        struct = {
            "tag": item_tag,
            "attr": {
                "id": item_id,
                "name": item_name
            }
        }
        result["content"].append(struct)

    return result
