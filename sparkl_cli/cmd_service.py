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

Service command implementation, connects to svc_rest instance.

The implementation module can have the following callbacks which are
all optional:

    main(service)
        This is executed in the main thread, after creation of
        the service object. You can use this for blocking
        operations such as a Tk gui and is most useful when the
        command line invocation is `sparkl service`.

    onopen(service)
        This is called back when the service object websocket
        opens, from the worker thread.

    onclose(service)
        This is called back when the service object closes,
        from the worker thread.
"""
from __future__ import print_function

import sys
import importlib
import types

from sparkl_cli.CliException import CliException
from sparkl_cli.Service import Service


def parse_args(subparser):
    """
    Adds module-specific subcommand arguments.
    """
    subparser.add_argument(
        "service",
        type=str,
        help="path or id of rest service")

    subparser.add_argument(
        "module",
        type=str,
        help="python module, or name of module (see --path)")

    subparser.add_argument(
        "-p", "--path",
        type=str,
        default=".",
        help="path to python module directory, default is '.'")


def command(args):
    """
    Opens a websocket against the specified rest service and installs the
    specified implementation module. This can provide any of the
    callback functions main/1, onopen/1 and onclose/1 where the argument
    in all cases is the service instance.
    """
    if isinstance(args.module, str):
        sys.path.append(args.path)
        module = importlib.import_module(args.module)
    elif isinstance(args.module, types.ModuleType):
        module = args.module
    else:
        raise CliException("module must be module object or module name")

    service = Service(args, module)

    if hasattr(module, "main"):
        module.main(service)

    return service
