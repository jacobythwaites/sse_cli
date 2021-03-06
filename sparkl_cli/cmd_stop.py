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

Service stop command implementation.
"""
from __future__ import print_function

from sparkl_cli.common import (
    get_current_folder,
    resolve,
    sync_request)


def parse_args(subparser):
    """
    Adds module-specific subcommand arguments.
    """
    subparser.add_argument(
        "service",
        type=str,
        help="service, instance or folder")


def command(args):
    """
    Stops the specified service or instance. If a folder is specified,
    then stops all services under that folder.
    """
    path = resolve(
        get_current_folder(args), args.service)

    response = sync_request(
        args, "POST", "sse_svc/stop/" + path)

    return response.json()
