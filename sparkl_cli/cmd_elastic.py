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

Elasticsearch event push implementation.

This is designed to read stdin from a pipe such as:

  sparkl listen | sparkl event | sparkl elastic http://localhost:9200

where elasticsearch is listening on port 9200.
"""
from __future__ import print_function

from elasticsearch import (
    Elasticsearch)

from elasticsearch.helpers import (
    streaming_bulk)

from sparkl_cli.common import (
    read_terms)


def parse_args(subparser):
    """
    Adds module-specific subcommand arguments.
    """
    subparser.add_argument(
        "-i", "--index",
        type=str,
        default="sparkl",
        help="elasticsearch index, default 'sparkl'")

    subparser.add_argument(
        "-u", "--url",
        type=str,
        default="http://localhost:9200",
        help="elasticsearch url, default http://localhost:9200")

    subparser.add_argument(
        "-d", "--delete",
        action="store_true",
        help="delete the specified index and its documents")

    subparser.add_argument(
        "-b", "--bulk",
        type=int,
        help="use bulk API, specify number of documents per chunk")


def command(args):
    """
    Reads JSON terms, one per line, from stdin and streams
    them to Elasticsearch. Any lines that are not JSON are passed through
    to stdout.

    Note the url can incorporate user and password, such as
    'http://user:pass@localhost:9200'.
    """
    instance = elastic_instance(args)

    if args.delete:
        delete_index(instance, args.index)
        return None

    check_index(instance, args.index)

    if args.bulk:
        (good, bad) = send_bulk(args, instance)
    else:
        (good, bad) = send_singly(args, instance)

    result = {
        "tag": "elastic",
        "attr": {
            "good": good,
            "bad": bad
        }
    }

    return result


def send_singly(args, instance):
    """
    Sends documents one at a time.
    Returns the number of terms indexed on exit.
    """
    good = bad = 0
    for term in read_terms():
        result = instance.create(
            args.index,
            doc_type=term["tag"],
            id=term["id"],
            body=term,
            refresh=True)

        if result.get("created", False):
            good += 1
        else:
            bad += 1

    return (good, bad)


def send_bulk(args, instance):
    """
    Sends documents in bulk, -b/--bulksize at a time.
    Returns the number of documents indexed on exit.

    Note that this doesn't send a chunk when full, only
    when the next document arrives that can't fit.

    It's tedious behaviour that means we need separate logic
    to send documents singly.
    """
    good = bad = 0
    actions = actions_generator(args.index)
    stream = streaming_bulk(
        instance, actions,
        chunk_size=args.bulk)

    for (ok, result) in stream:
        if ok:
            good += 1
        else:
            bad += 1
            print("Document not indexed:", result)

    return (good, bad)


def actions_generator(index):
    """
    Yields an action per line containing a JSON term.
    All non-JSON lines are printed.
    """
    for term in read_terms():
        action = make_action(index, term)
        yield action


def make_action(index, term):
    """
    Makes an action from the term.

    See also:
    http://elasticsearch-py.readthedocs.io/en/master/helpers.html#bulk-helpers
    """
    action = {
        "_op_type": "create",
        "_index": index,
        "_type": term["tag"],
        "_id": term["id"],
        "_source": term
    }

    return action


def elastic_instance(args):
    """
    Creates an elasticsearch instance using the args.
    """
    es = Elasticsearch(args.url)
    return es


def delete_index(instance, index):
    """
    Deletes the index on the instance and all documents in it.
    """
    if instance.indices.exists(index):
        instance.indices.delete(index)
        print("Index {Index} deleted".format(
            Index=index))
    else:
        print("No index {Index}".format(
            Index=index))


def check_index(instance, index):
    """
    Checks the index on the instance, creating it if not already present.
    """
    if not instance.indices.exists(index):
        print("New index {Index}".format(
            Index=index))
        create_index(instance, index)
    else:
        print("Existing index {Index}".format(
            Index=index))


def create_index(instance, index):
    """
    Creates the index with the SPARKL event mappings including
    timestamp and 'nested' type for cause and data lists.
    """
    config = {
        "settings": {
        },
        "mappings": {
            "_default_": {
                "dynamic_templates": [
                    {
                        "timestamp": {
                            "match": "timestamp",
                            "mapping": {
                                "type": "date"
                            }
                        }
                    }
                ]
            }
        }
    }
    instance.indices.create(
        index, config,
        update_all_types=False)
