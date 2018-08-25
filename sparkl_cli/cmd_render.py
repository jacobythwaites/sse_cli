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

Get source command implementation.
"""
from __future__ import print_function

from shutil import copyfile
import os
import subprocess
import tempfile
from time import sleep

from sparkl_cli.common import get_source

DEFAULT_INTERVAL = 3


def parse_args(subparser):
    """
    Adds module-specific subcommand arguments.
    """
    subparser.add_argument(
        "-f", "--file",
        action="store_true",
        help="source path refers to local file not SPARKL object")

    subparser.add_argument(
        "-o", "--output",
        help="write output to named local file")

    subparser.add_argument(
        "-w", "--watch",
        action="store_true",
        help="monitor local source file for changes")

    subparser.add_argument('-i', '--interval',
                           default=DEFAULT_INTERVAL,
                           type=int,
                           help="interval the source file "
                                "is checked for changes")

    subparser.add_argument(
        "source",
        type=str,
        nargs="?",
        default=".",
        help="source path or id")


def render(src_path, dst_path):
    """
    Applies the render.xsl transform on src_path to
    generate the content of dst_path.
    """
    xsl_path = os.path.join(
        os.path.dirname(__file__),
        "resources/render.xsl")
    subprocess.check_call([
        "xsltproc",
        "--xincludestyle",
        "--output", dst_path,
        "--stringparam", "mode", "page",
        xsl_path,
        src_path])


def get_html_content(src_file, temp_file):
    """
    Renders the source file as HTML, saves its content
    into a temporary file and returns the content
    of the temporary file.
    """
    render(src_file, temp_file)

    with open(temp_file, 'r') as data:
        return data.read()


def show_html(args, local=False):
    """
    Retrieves the source code of a configuration either
    from the local file system or from a SPARKL instance.

    Creates a temp file to store the source code and
    optionally transforms its content into html.

    The temp file is deleted once the source code is returned.
    """
    _handle, temp_file = tempfile.mkstemp('.html')

    try:
        # Get content of tempfile from local file.
        if local:
            return get_html_content(args.source, temp_file)

        # Get content of tempfile from SPARKL instance.
        get_source(args, temp_file)
        return get_html_content(temp_file, temp_file)

    finally:
        subprocess.check_call(['rm', temp_file])


def save_local_as_html(src, dest):
    """
    Saves a local file - 'src' - on the file system as 'dest' and
    transforms it into html.
    """
    _handle, temp_file = tempfile.mkstemp('.html')
    copyfile(src, temp_file)
    render(temp_file, dest)
    subprocess.check_call(['rm', temp_file])


def download_as_html(args):
    """
    Downloads a configuration from a running SPARKL instance.
    The configuration is transformed into html.
    """
    _handle, temp_file = tempfile.mkstemp('.html')
    get_source(args, temp_file)
    render(temp_file, args.output)
    subprocess.check_call(['rm', temp_file])


def get_latest_mod(src_file):
    """
    Gets the last modification date of
    the specified file.
    """
    # Get date of latest modification
    stats = os.stat(src_file)
    latest_mod = stats[8]
    return latest_mod


def html_generator(src_file, previous_change, interval):
    """
    A generator function that periodically checks an XML source file
    for changes. On every change it transforms the XML source into HTML,
    writes it into a temporary file and yields the temp file's content.

    When first called, unconditionally yields the
    content of the source file as HTML.

        - 'src_file':
            The path to the XML source file on the local file system
        - 'previous_change':
            The last known date the XML source file was modified
        - 'interval':
            The rate of frequency the XML source file is checked for changes
    """
    # Create a temporary file for storing the changes.
    _handle, temp_file = tempfile.mkstemp('.html')
    try:
        # Render the file on first call of the generator.
        yield get_html_content(src_file, temp_file)

        # On successive calls only render if there was a change.
        while True:
            try:
                latest_change = get_latest_mod(src_file)

                if previous_change != latest_change:
                    yield get_html_content(src_file, temp_file)
                    previous_change = latest_change

                sleep(interval)

            # Break loop on ctrl-C
            except KeyboardInterrupt:
                print('Stop monitoring.')
                break

    # Only delete temporary file when generator is terminated.
    finally:
        subprocess.check_call(['rm', temp_file])


def start_monitoring(src_file, interval):
    """
    Starts monitoring a local file for changes.
    Hands down a temporary file for the generator to
    write changes into.
    """
    if interval <= 0:
        print('Invalid interval. Using default: {}'.format(DEFAULT_INTERVAL))
        interval = DEFAULT_INTERVAL

    previous_change = get_latest_mod(src_file)

    generator = html_generator(src_file, previous_change, interval)
    return generator


def write_on_change(output_file, my_generator):
    """
    Writes the generator's results into the
    output file on receiving them.

        - 'output_file':
            The output file that stores the results
        - 'my_generator:
            A generator instance that periodically sends
            HTML content
    """
    for content in my_generator:
        with open(output_file, 'w') as html_output:
            html_output.write(content)
            print('Updated {}.'.format(output_file))


def command(args):
    """
    Transforms either a SPARKL configuration or
    a local file (--file) into html.

    Either saves the html to the file system (--output)
    or returns its content.

    If the --watch flag is specified, the source file is
    checked periodically and re-rendered on changes.
    """

    # Create generator instance if both watch and file flags used.
    if args.file and args.watch:
        watcher = start_monitoring(args.source, args.interval)

        # Use generator to update file.
        if args.output:
            write_on_change(args.output, watcher)
            return None

        # Or just return generator.
        return watcher

    # The --watch flag must be combined with the --file flag.
    if args.watch:
        print('--watch flag ignored. Use a local source file.')

    # Render local XML file as HTML and save it to output file.
    if args.output and args.file:
        save_local_as_html(args.source, args.output)
        return None

    # Save SPARKL mix as HTML into output file.
    if args.output:
        download_as_html(args)
        return None

    # Print local or SPARKL XML as rendered HTML.
    return show_html(args, local=args.file)
