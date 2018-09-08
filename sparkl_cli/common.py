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

Utility module for common functions.
"""
from __future__ import print_function

import os
import platform
import sys
import time
import shutil
import tempfile
import json
import posixpath
import subprocess
from http.cookiejar import LWPCookieJar
import websocket
import psutil

import requests
from requests.compat import urljoin, urlsplit, urlunparse
from requests.utils import dict_from_cookiejar

from sparkl_cli.CliException import (
    CliException)

SESSION_COOKIE = "ipaas_session"
STATE_FILE = "state.json"
RETRY_BACK_OFF_SECS = 0.1
MAX_TRIES = 5

ANSI_TAG = "\033[1m"
ANSI_END = "\033[0m"


def get_default_session():
    """
    Locates the first ancestor process which is a shell. Returns
    its pid if found.

    Otherwise returns the pid of the invoking process.
    """
    if psutil.POSIX:
        def predicate(name):
            return name.endswith("sh")

    elif psutil.WINDOWS:
        def predicate(name):
            return name in ("cmd.exe", "powershell.exe")

    else:
        raise CliException("Unsupported platform")

    this_proc = psutil.Process()
    proc = this_proc
    while proc.parent().pid:
        proc = proc.parent()
        if predicate(proc.name()):
            return proc.pid

    return this_proc.pid


def get_object(args, object_id):
    """
    Returns the object with the given pathname or id.
    Maintains a cache of object keyed by id (*not* name).

    That's because the id is unique even if the object is
    changed, whereas a path can refer to an object that has
    now changed.

    Thus if this function is called with an id, the returned
    object may come directly from cache.
    """
    connection = get_connection(args)
    connection_cache = connection.get("cache", {})
    sparkl_object = connection_cache.get(object_id)
    if sparkl_object:
        return sparkl_object

    response = sync_request(
        args, "GET", "sse_cfg/object/" + object_id)

    if response:
        sparkl_object = response.json()
        object_id = sparkl_object["attr"].get("id")
        if object_id:
            connection_cache[object_id] = sparkl_object
            connection["cache"] = connection_cache
            put_connection(args, connection)

        return sparkl_object

    return None


def get_working_root():
    """
    Returns the working root under which a working directory
    is created for each process invoking the cli.

    Creates the working root if not already present.
    """
    working_root = os.path.join(
        tempfile.gettempdir(),
        "sse_cli")

    if not os.path.exists(working_root):
        os.makedirs(working_root)

    return working_root


def get_working_dir(args):
    """
    Returns the working directory for this invocation, using the
    common session id.

    The directory is created if necessary.
    """
    working_dir = os.path.join(
        get_working_root(),
        str(args.session))

    if not os.path.exists(working_dir):
        os.makedirs(working_dir)

    return working_dir


def garbage_collect():
    """
    Performs a garbage collection of temp dirs not associated with
    a running process.
    """
    for working_dir in os.listdir(get_working_root()):
        pid = int(working_dir)
        if not psutil.pid_exists(pid):
            obsolete_dir = os.path.join(
                get_working_root(),
                working_dir)
            shutil.rmtree(obsolete_dir)


def get_state(args):
    """
    Gets the current state dictionary, or empty dictionary
    if none.

    Since there's no inter-process mutex over state, a pipeline can
    have a write and a read clash.

    So we catch any exception caused by failing to fully read state,
    and retry after a short back-off.
    """
    name = os.path.join(
        get_working_dir(args), STATE_FILE)

    if os.path.isfile(name):
        retry = True
        try_count = 1
        while retry and try_count <= MAX_TRIES:
            try:
                with open(name, "r") as state_file:
                    state = json.load(state_file)
                    retry = False
            except (IOError, EOFError, ValueError):
                time.sleep(RETRY_BACK_OFF_SECS)
                try_count += 1

        if try_count == MAX_TRIES:
            raise CliException(
                "Read state failed after {Tries} tries".format(
                    Tries=MAX_TRIES))

    else:
        state = {}

    return state


def set_state(args, state):
    """
    Saves the new state dictionary.
    """
    name = os.path.join(
        get_working_dir(args), STATE_FILE)

    with open(name, "w") as state_file:
        json.dump(state, state_file)


def get_connection(args):
    """
    Gets the current connection from the state object, or
    the named alias if provided.

    Throws an exception if no such connection alias exists.
    """
    state = get_state(args)
    connections = state.get("connections", {})
    connection = connections.get(args.alias)
    if not connection:
        raise CliException(
            "No connection {Alias}".format(
                Alias=args.alias))

    return connection


def put_connection(args, connection):
    """
    Puts the connection dict into the state object under the
    given alias name.
    """
    state = get_state(args)
    connections = state.get("connections", {})
    connections[args.alias] = connection
    set_state(args, state)


def pickle_cookies(cookies):
    """
    Pickles the cookies object for the given alias into
    a file for later retrieval.
    """
    cookies.save(
        ignore_discard=True)


def unpickle_cookies(args, alias=None):
    """
    Unpickles the cookies file for the given alias and
    returns the original object.

    If no file exists, then an empty cookies object is
    returned.
    """
    if alias is None:
        alias = args.alias

    cookie_file = os.path.join(
        get_working_dir(args),
        alias + ".cookies")

    cookies = LWPCookieJar(cookie_file)

    if os.path.isfile(cookie_file):
        cookies.load(
            ignore_discard=True)

    return cookies


def delete_cookies(args, alias=None):
    """
    Deletes the cookie jar for the given alias, or
    the args alias if not specified.
    """
    if alias is None:
        alias = args.alias

    cookie_file = os.path.join(
        get_working_dir(args),
        alias + ".cookies")

    if os.path.isfile(cookie_file):
        os.remove(cookie_file)


def sync_request(
        args, method, href,
        params=None,
        data=None,
        accept="json",
        headers=None,
        timeout=0):
    """
    Makes a request on the specified connection, using
    the connection session state including session cookies.

    Method can be 'GET' or 'POST' upper or lower case.
    Href is relative to the base url, e.g. 'sse_cfg/user'.
    Params is a dict, or None.
    Body is a string, or None, used in POST request only.

    Returns the response object. If a timeout occurs, an
    exception is raised. Otherwise None is returned.

    Note that an HTTP status code other than 2xx is false-y
    in Python.
    """
    connection = get_connection(args)

    if timeout == 0:
        timeout = None

    session = requests.Session()
    session.cookies = unpickle_cookies(args)

    base = connection.get("url")
    request_url = urljoin(base, href)
    if not headers:
        headers = {}
    headers["Accept"] = "application/" + accept

    if method.upper() == "GET":
        response = session.get(
            request_url,
            headers=headers,
            params=params,
            timeout=timeout)

    elif method.upper() == "POST":
        response = session.post(
            request_url,
            headers=headers,
            params=params,
            data=data,
            timeout=timeout)

    elif method.upper() == "DELETE":
        response = session.delete(
            request_url,
            headers=headers,
            params=params,
            timeout=timeout)

    pickle_cookies(session.cookies)
    return response


def get_current_folder(args):
    """
    Convenience function returns the full path of the
    current folder.
    """
    connection = get_connection(args)
    return connection.get("cwd", "/")


def del_current_folder(args):
    """
    Convenience function clears the current folder. This
    should be done on sign in and sign out.
    """
    connection = get_connection(args)
    if "cwd" in connection:
        del connection["cwd"]
        put_connection(args, connection)


def resolve(base, href):
    """
    Resolves a path against the base. A SPARKL absolute path
    can either start with / or with user@domain.com/.
    """
    (base_user, base_path) = split_path(base)
    (href_user, href_path) = split_path(href)

    if href_user:
        result_user = href_user
    else:
        result_user = base_user

    result_path = posixpath.normpath(
        posixpath.join(base_path, href_path))

    if result_user:
        return posixpath.join(result_user, result_path.strip("/"))

    return result_path


def split_path(path):
    """
    Splits a path into the user and path portions.
    The user can be None if not specified, and the
    path is always absolute if the user is specified.
    """
    steps = path.split("/")
    if "@" in steps[0]:
        user = steps[0]
        if len(steps) == 1:
            path = "/"
        else:
            path = "/" + "/".join(steps[1:])
        return (user, path)
    else:
        return (None, path)


def get_websocket(args, ws_path):
    """
    Convenience function to return a websocket client
    connection with session cookie using the supplied
    path.
    """
    connection = get_connection(args)
    http_url = connection.get("url")
    (scheme, netloc, _, _, _) = urlsplit(http_url)

    if scheme == "http":
        ws_scheme = "ws"
    else:
        ws_scheme = "wss"

    ws_url = urlunparse((ws_scheme, netloc, ws_path, "", "", ""))
    cookies = unpickle_cookies(args)
    cookiedict = dict_from_cookiejar(cookies)

    cookie = None
    if SESSION_COOKIE in cookiedict:
        session = cookiedict[SESSION_COOKIE]
        cookie = SESSION_COOKIE + "=" + session

    ws = websocket.WebSocket()
    ws.connect(ws_url, cookie=cookie)
    return ws


def show_struct(json_object, indent=0):
    """
    Renders line-based display of json struct content
    suitable for command-line use.

    If json_object is None, nothing is output.

    Indent is increased in recursive calls.
    """
    def indent_print(*args):
        """
        Indents and prints the text.
        """
        for _ in range(0, indent):
            print("\t", end="")
        print(*args, sep="\t")

    if json_object is None:
        return

    if isinstance(json_object, dict) and "tag" in json_object:
        if indent > 0:
            print()

        tag = json_object["tag"]
        if platform.system() == "Windows":
            indent_print(tag)
        else:
            indent_print(ANSI_TAG + tag + ANSI_END)

        if "attr" in json_object:
            keys = json_object["attr"].keys()
            for key in sorted(keys):
                indent_print(
                    key + ":",
                    json_object["attr"][key])

        if "content" in json_object:
            for content_object in json_object["content"]:
                show_struct(content_object, indent + 1)

        return

    raw = json_object
    if isinstance(json_object, dict):
        raw = json.dumps(json_object, indent=4)

    # If not nested in a struct, just output the content.
    if indent == 0:
        print(raw)

    # If nested in a struct, output separator lines.
    else:
        print("~~~~")
        print(raw)
        print("~~~~")


def read_terms():
    """
    Generates successive terms, one per line on stdin.
    Non-JSON lines are printed but do not yield a result.

    The readline() function buffers line input better than
    the 'for line in sys.stdin:' pattern which seems to rely
    on some input bufsize.
    """
    line = None
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break

            if not line.isspace():
                term = json.loads(line)
                yield term

        except ValueError:
            print(
                "Cannot read JSON term:\n""~~~~\n"
                "{Line}\n"
                "~~~~\n".format(
                    Line=line), file=sys.stderr)

        except KeyboardInterrupt:
            break


def get_source(args, src_path):
    """
    Gets the XML source from SPARKL and saves it in the
    supplied src_path file.
    """
    path = resolve(
        get_current_folder(args), args.source)

    response = sync_request(
        args, "GET", "sse_cfg/source/" + path,
        accept="xml")
    with open(src_path, "w") as output_file:
        output_file.write(response.text)


def transform(xsl, src, dst=None, **params):
    """
    Wraps xsltproc to transform the src file using xsl and args
    into the dst file (stdout if None).

    The xsl file is resolved relative to our package directory,
    but that doesn't apply to src or dst.

    The params are passed to the processor. Each value must be
    a valid xpath value, i.e. a string MUST be literally quoted.
    """
    xsl = os.path.join(
        os.path.dirname(__file__),
        xsl)

    if platform.system() == "Windows":
        msxsl(xsl, src, dst, **params)
    else:
        xsltproc(xsl, src, dst, **params)


def msxsl(xsl, src, dst, **params):
    """
    Invokes the msxsl wrapper around msxml for
    Windows systems.
    """
    args = []
    if dst:
        args += ["-o", dst]

    for key, value in params.items():
        args += [key + "=" + value]

    cmd = ["msxsl"] + [src, xsl] + args

    subprocess.check_call(cmd)


def xsltproc(xsl, src, dst, **params):
    """
    Invokes the xsltproc wrapper around libxml for
    Darwin and Linux systems.
    """
    args = ["--xincludestyle"]
    if dst:
        args += ["--output", dst]

    for key, value in params.items():
        args += ["--param", key, value]

    cmd = ["xsltproc"] + args + [xsl, src]

    subprocess.check_call(cmd)
