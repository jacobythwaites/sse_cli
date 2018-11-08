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

Login command implementation.
"""
from __future__ import print_function

import getpass

from sparkl_cli.CliException import (
    CliException)

from sparkl_cli.common import (
    get_connection,
    del_current_folder,
    sync_request)


def parse_args(subparser):
    """
    Adds module-specific subcommand arguments.
    """
    subparser.add_argument(
        "-r", "--register",
        action="store_true",
        help="register the user, creating if necessary")
    subparser.add_argument(
        "-t", "--token",
        help="token name, if previously created by user")
    subparser.add_argument(
        "user",
        nargs="?",
        type=str,
        help="email of user to be logged in")
    subparser.add_argument(
        "password",
        nargs="?",
        type=str,
        help="user password or access token secret")


def login(args):
    """
    Logs in the specified user, prompting for password
    if necessary.
    """
    connection = get_connection(args)
    data = {}
    if not connection["cert"]:
        if not args.password:
            args.password = getpass.getpass("Password: ")

        data = {
            "email": args.user,
            "password": args.password}

    if args.token:
        data["token"] = args.token

    response = sync_request(
        args, "POST", "sse_cfg/user",
        data=data)

    if response:
        return response.json()

    raise CliException(
        "Failed to login {User}".format(
            User=args.user))


def register(args):
    """
    Registers the specified user, prompting twice for
    password if necessary.
    """
    if not args.password:
        args.password = getpass.getpass("Password: ")
        check = getpass.getpass("Repeat: ")
        if args.password != check:
            raise CliException(
                "Passwords do not match")

    response = sync_request(
        args, "POST", "sse_cfg/register",
        data={
            "email": args.user,
            "password": args.password})

    if response:
        return response.json()

    raise CliException(
        "Failed to register {User}".format(
            User=args.user))


def command(args):
    """
    Logs in or registers the user. If the connection was established
    with a TLS client certificate (using the --cert option), it provides
    the credentials and no username or password should be specified.
    """
    del_current_folder(args)

    if args.register:
        return register(args)

    return login(args)
