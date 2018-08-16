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

List active services command implementation.
"""
from __future__ import print_function

from sparkl_cli.common import (
    get_object,
    sync_request)


def parse_args(subparser):
    """
    Adds module-specific subcommand arguments.
    """
    subparser.add_argument(
        "folder",
        type=str,
        nargs="?",
        default="/",
        help="folder or service id or path")


def list_services(args):
    """
    Lists the active services under the specified folder.
    """
    result = {
        "tag": "active",
        "attr": {
            "count": 0
        },
        "content": []
    }

    response = sync_request(
        args, "GET", "sse_svc/status/" + args.folder)

    term = response.json()
    if not term.get("tag") == "active":
        return term

    service_ids = term["attr"]["services"].split()
    result["attr"]["count"] = len(service_ids)

    for service_id in service_ids:
        service = get_object(args, service_id)
        if service:
            entry = {
                "tag": "service",
                "attr": {
                    "id": service["attr"]["id"],
                    "path": service["attr"]["path"]
                }
            }
            result["content"].append(entry)

    return result


def command(args):
    """
    Lists active services under the specified folder. If no folder
    is provided, lists active services under the user's root folder.
    """
    return list_services(args)
