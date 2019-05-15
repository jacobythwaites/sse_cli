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

Main module implementing CLI for managing running SPARKL nodes.

This must be invoked as a package, to allow the relative import
of the command files to work:

  python[3] -m sparkl_cli <cmd> <arg..>

Client state between invocations is maintained in the filesystem.
"""

# Uncomment the following two lines for trace debug.
# import pdb
# pdb.set_trace()
from __future__ import print_function

import os
import sys
import argparse
import types
import threading
import pkg_resources


from sparkl_cli.common import (
    get_default_session,
    garbage_collect,
    show_struct)

from sparkl_cli.CliException import (
    CliException)

from sparkl_cli import (
    cmd_active,
    cmd_call,
    cmd_cd,
    cmd_close,
    cmd_connect,
    cmd_elastic,
    cmd_listen,
    cmd_login,
    cmd_logout,
    cmd_ls,
    cmd_mkdir,
    cmd_node,
    cmd_object,
    cmd_put,
    cmd_render,
    cmd_rm,
    cmd_service,
    cmd_session,
    cmd_source,
    cmd_start,
    cmd_stop,
    cmd_tree,
    cmd_undo,
    cmd_user,
    cmd_vars)


MODULES = (
    ("active", cmd_active,
     "list active services"),

    ("call", cmd_call,
     "invoke a transaction or individual operation"),

    ("cd", cmd_cd,
     "show or change current folder"),

    ("close", cmd_close,
     "close connection"),

    ("connect", cmd_connect,
     "create or show connections"),

    ("elastic", cmd_elastic,
     "push JSON to Elasticsearch"),

    ("listen", cmd_listen,
     "listen for events on any configuration object"),

    ("login", cmd_login,
     "login or register user"),

    ("logout", cmd_logout,
     "logout user"),

    ("ls", cmd_ls,
     "list content of folder or service"),

    ("mkdir", cmd_mkdir,
     "create new folder"),

    ("node", cmd_node,
     "show node info (administrator only)"),

    ("object", cmd_object,
     "get object JSON by name or id"),

    ("put", cmd_put,
     "upload XML source [or change] file"),

    ("render", cmd_render,
     "transform source configuration or local file into html"),

    ("rm", cmd_rm,
     "remove object"),

    ("service", cmd_service,
     "start service implementation module"),

    ("session", cmd_session,
     "show current session info"),

    ("source", cmd_source,
     "view [and download] source configuration"),

    ("start", cmd_start,
     "start a service"),

    ("stop", cmd_stop,
     "stop one or more services"),

    ("tree", cmd_tree,
     "show source in tree-like format"),

    ("undo", cmd_undo,
     "undo last change"),

    ("user", cmd_user,
     "show current user details"),

    ("vars", cmd_vars,
     "set field variables"))


def get_version():
    """
    Returns the content of the version.txt compile-time file.
    """
    filepath = pkg_resources.resource_filename(
        __package__, "version.txt")
    version = "Unknown"
    with open(filepath, "r") as version_file:
        version = version_file.read().replace("\n", "")
    return __package__ + " " + version


def build_parser():
    """
    Returns the parsed command and command arguments using the
    supplied argument list or sys.argv if none.

    This calls out to each submodule to parse the command line
    arguments.
    """
    prog_name = os.environ.get("SPARKL_PROG_NAME")
    if not prog_name:
        prog_name = __package__

    epilog = "Use '{ProgName} <cmd> -h' for subcommand help".format(
        ProgName=prog_name)

    parser = argparse.ArgumentParser(
        prog=prog_name,
        description="SPARKL command line utility.",
        epilog=epilog)

    parser.add_argument(
        "-v", "--version",
        action="version",
        version=get_version())

    parser.add_argument(
        "-a", "--alias",
        type=str,
        default="default",
        help="optional alias for multiple connections in local session")

    parser.add_argument(
        "-s", "--session",
        type=int,
        default=get_default_session(),
        help="optional local session id, defaults to ancestor shell pid")

    parser.add_argument(
        "-t", "--timeout",
        type=int,
        default=0,
        help="request timeout in seconds, default 0 means no timeout")

    subparsers = parser.add_subparsers()

    for (cmd, submodule, help_text) in MODULES:
        subparser = subparsers.add_parser(
            cmd,
            description=submodule.command.__doc__,
            help=help_text,
            epilog="(Choose connection with toplevel option -a/--alias)")
        subparser.set_defaults(
            fun=submodule.command)
        submodule.parse_args(subparser)

    return parser


def sparkl(*cmd_args, **kwargs):
    """
    Allow invocation from external Python scripts by providing command
    name positional and long-name args

    e.g. sparkl("get", "Scratch/Primes", format="xml").

    Default arg values are set using the parse_args function, and
    are overridden by the supplied kwargs.
    """
    parser = build_parser()
    args = parser.parse_args(cmd_args)

    for arg in kwargs:
        value = kwargs.get(arg)
        setattr(args, arg, value)

    command = cmd_args[0]

    for (cmd, submodule, _help_text) in MODULES:
        if cmd == command:
            result = submodule.command(args)
            return result

    raise CliException("Bad command: " + command)


def main():
    """
    Main function parses arguments.

    If the --version arg is specified, shows version and returns.

    Otherwise, it parses arguments into the common namespace object,
    performs a garbage collection to clean outdated sessions,
    and finally dispatches the specified command.
    """
    parser = build_parser()
    args = parser.parse_args()

    garbage_collect()

    try:
        result = args.fun(args)

        if isinstance(result, types.GeneratorType):
            for chunk in result:
                show_struct(chunk)

        elif isinstance(result, threading.Thread):
            try:
                while result.isAlive():
                    result.join(5)
            except KeyboardInterrupt:
                result.close()

        else:
            show_struct(result)

        sys.exit(0)

    except AttributeError:
        parser.print_usage()
        sys.exit(1)

    except CliException as exception:
        print(exception, file=sys.stderr)
        sys.exit(1)


# Allow invocation using `python -m sparkl_cli.main`
if __name__ == "__main__":
    main()
