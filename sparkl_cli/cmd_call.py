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

Invoke operation command implementation.

This uses the sse_svc_dispatcher API, which requires that
we construct the event and data client-side.

It would be very much easier to change sse_svc_dispatcher to
support params!
"""
from __future__ import print_function

import os
import sys
import json
import base64

from sparkl_cli.CliException import (
    CliException)

from sparkl_cli.common import (
    get_current_folder,
    get_object,
    resolve,
    sync_request)

from sparkl_cli.cmd_vars import (
    get_vars)


def parse_args(subparser):
    """
    Adds module-specific subcommand arguments.
    """
    subparser.add_argument(
        "-s", "--save",
        action="store_true",
        help="save result values as vars")

    subparser.add_argument(
        "operation",
        help="operation path or id")


def sparkl_type(field_type, string_value):
    """
    Uses the field type to coerce the string value to the
    json-compatible python equivalent. Binary and term are
    left as string.
    """
    value = string_value
    if field_type == "integer":
        value = int(string_value)
    elif field_type == "boolean":
        value = bool(string_value)
    elif field_type == "float":
        value = float(string_value)
    return value


def vars_to_data(args, operation):
    """
    Builds the list of datum required by the operation event,
    built using the current var values.

    Returns a 2-tuple whose first element is True if the data is
    complete and therefore the event can be dispatched.
    """
    vars_dict = get_vars(args)
    data = []
    can_dispatch = True

    for field_id in operation["attr"]["fields"].split():
        field = get_object(args, field_id)
        field_type = field["attr"]["type"]
        if field_type:
            field_name = field["attr"]["name"]
            field_value = vars_dict.get(field_name)
            datum = var_to_datum(
                field_id, field_name, field_type, field_value)
            if datum:
                data.append(datum)
            else:
                can_dispatch = False

    return (can_dispatch, data)


def var_to_datum(field_id, field_name, field_type, field_value):
    """
    Returns the datum built using data from a var's literal value
    or value read from file.

    The field type determines how the value is interpreted:

    TYPE             LITERAL EXAMPLE.      READ FROM FILE
    -------------    -------------------   -------------------------------
    boolean          String, "true"        File read as string
    float            String, "3.14"        File read as string
    integer          String, "314"         File read as string
    utf8             String, "Hello"       File read as string
    json             JSON,   "\"hi\""      File read as string
    binary           Base64, "SGk="        Binary file converted to base64
    erlang string    String, "Hello"       File read as string
    erlang term      String, "{a,b}"       File read as string

    Prints a message and returns None if there is no field value,
    or the "read" method cannot populate the value.
    """
    if not field_value:
        print("Missing {Type} var: {Var}".format(
            Var=field_name,
            Type=field_type), file=sys.stderr)
        return None

    [method, string_value] = field_value

    if method == "read":
        if os.path.isfile(string_value) and field_type == "binary":
            with open(string_value, "rb") as value_file:
                string_value = base64.b64encode(
                    value_file.read())

                if sys.version_info[0] == 3:
                    string_value = string_value.decode('utf-8')

        elif os.path.isfile(string_value):
            with open(string_value, "r") as value_file:
                string_value = value_file.read()
        else:
            print("Cannot read {File} for {Var}".format(
                File=string_value,
                Var=field_name), file=sys.stderr)
            return None

    value = sparkl_type(field_type, string_value)

    datum = {
        "tag": "datum",
        "attr": {
            "field": field_id
        },
        "content": [value]}
    return datum


def simplify(args, data_event):
    """
    Returns a struct corresponding to the data event with ids
    resolved to names.
    """
    result = {
        "tag": None,
        "attr": {},
        "content": []
    }

    subject = get_object(
        args, data_event["attr"]["subject"])
    result["tag"] = subject["tag"]
    result["attr"]["id"] = data_event["attr"]["subject"]
    result["attr"]["name"] = subject["attr"]["name"]

    for datum in data_event.get("content", []):
        field = get_object(args, datum["attr"]["field"])
        datum["attr"]["type"] = field["attr"]["type"]
        datum["attr"]["name"] = field["attr"]["name"]
        result["content"].append(datum)

    return result


def command(args):
    """
    Invoked the named operation. Existing vars are used to populate
    the field values, where needed.
    In the case of a solicit or notify, this causes a transaction to
    be executed.
    In the case of a request or consume, the individual operation
    is executed.
    """
    pathname = resolve(
        get_current_folder(args), args.operation)

    operation = get_object(args, pathname)
    if not operation:
        raise CliException(
            "No operation {Operation}".format(
                Operation=args.operation))

    tag = operation["tag"]
    subject = operation["attr"]["id"]

    (can_dispatch, data) = vars_to_data(args, operation)

    if not can_dispatch:
        raise CliException(
            "Cannot dispatch {Operation}".format(
                Operation=args.operation))

    outbound_event = json.dumps({
        "tag": "data_event",
        "attr": {
            "subject": subject
        },
        "content": data})

    response = sync_request(
        args, "POST", "sse_svc_dispatcher/" + tag,
        headers={
            "Content-Type": "application/json"},
        data=outbound_event,
        timeout=0)

    return_event = response.json()

    if return_event.get("tag") == "data_event":
        result = simplify(args, return_event)
        return result

    return return_event
