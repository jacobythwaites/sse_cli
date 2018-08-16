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

Undo command implementation.

This performs the HTTP DELETE request and indicates whether
the undo was successful.
"""
from __future__ import print_function

from sparkl_cli.common import (
    sync_request)


def parse_args(_):
    """
    Adds module-specific subcommand arguments.
    """
    return


def command(args):
    """
    Undoes the last configuration change. The undo stack
    is per-user, meaning you can undo a change made in a
    previous session.
    """
    response = sync_request(
        args, "DELETE", "sse_cfg/change")

    return response.json()
