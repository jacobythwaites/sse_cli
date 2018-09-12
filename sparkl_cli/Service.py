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

An instance of this class opens a websocket to an svc_rest
service.

Received request and consume server operation messages are delegated
to the implementation module.

The notify and solicit methods enable the implementation module
to perform client operations.
"""
from __future__ import print_function

import json
import random
import string
import threading

from sparkl_cli.common import (
    get_current_folder,
    get_websocket,
    resolve)

PATH_PREFIX = "svc_rest/websocket/"


class Service(threading.Thread):
    """
    Opens a websocket and installs the implementation module
    which can provide optional main/1, onopen/1 and onclose/1
    callback functions.
    """

    def __init__(self, args, module):
        """
        Initialises the object ready for open. The implementation
        property is empty, usually set by the module.onopen callback.
        """
        threading.Thread.__init__(self)
        self.daemon = True
        self.service = args.service
        self.impl = {}
        self.pending = {}
        self.closed = True
        self.module = module
        self.__open(args)

    def __open(self, args):
        """
        Opens the websocket connection and calls back the module onopen
        function.

        If the onopen callback installs one or more implementation
        functions, then the thread is started which reads events.

        If no implementation functions are installed, no thread is
        started.
        """
        path = resolve(
            get_current_folder(args), args.service)
        ws_path = PATH_PREFIX + path
        self.ws = get_websocket(args, ws_path)
        self.start()

    def close(self):
        """
        Closes the websocket connection if still connected, and calls the
        implementation module onclose callback.
        """
        self.ws.close()

        # Close callback must occur only once.
        if not self.closed:
            self.closed = True

            if hasattr(self.module, "onclose"):
                self.module.onclose(self)

    def run(self):
        """
        Thread that dispatches incoming response, request and consume
        messages.
        """
        try:
            self.closed = False

            if hasattr(self.module, "onopen"):
                self.module.onopen(self)

            for message in self.ws:
                if message:
                    term = json.loads(message)
                    if "consume" in term:
                        self.__consume(term)
                    elif "request" in term:
                        self.__request(term)
                    elif "response" in term:
                        self.__response(term)
        finally:
            self.close()

    def notify(self, notify):
        """
        Sends the notify term on the websocket, in the form:
        {
          "notify": "Some/Notify",
          "data": {
            "field1": 1,
            "field2": "some value"
          }
        }

        Returns immediately.
        """
        self.ws.send(
            json.dumps(notify))

    def solicit(self, solicit, callback=None):
        """
        Sends the solicit term on the websocket, in the form:
        {
            "solicit": "Some/Solicit",
            "data": {
                "field1": 1,
                "field2": "some value"
            }
        }

        When the response is received, if callback is provided then
        the callback is invoked with the response in the form:
        {
            "response": "Ok",
            "data": {
                "field3": "some value",
                "field4": 14
            }
        }

        If the callback is not provided, delegates to sync_solicit.
        """
        if not callback:
            return self.sync_solicit(solicit)

        event_id = random_id()
        solicit["id"] = event_id
        self.pending[event_id] = callback

        self.ws.send(
            json.dumps(solicit))
        return None

    def sync_solicit(self, solicit):
        """
        Synchronous solicit blocks until the response arrives and
        returns it.

        This is done by using a condition variable. The calling thread
        waits until the response is placed into the pending dict in place
        of the callback function closure.
        """
        event_id = random_id()
        solicit["id"] = event_id
        cv = threading.Condition()

        def callback(response):
            cv.acquire()
            self.pending[event_id] = response
            cv.notify()
            cv.release()

        self.pending[event_id] = callback

        cv.acquire()
        self.ws.send(
            json.dumps(solicit))
        cv.wait()
        cv.release()
        response = self.pending.pop(event_id)
        return response

    def __consume(self, consume):
        """
        Handles a consume event, dispatching to the implementation
        function.

        If the consume has an id property, it requires a reply.
        Otherwise, it is simply dispatched direct to the implementation.
        """
        consume_path = consume["consume"]
        impl = self.impl[consume_path]

        if "id" not in consume:
            impl(consume)
            return

        event_id = consume["id"]

        def callback(reply):
            """
            Closure reinstates full reply path if not already present.
            """
            reply["id"] = event_id

            reply_path = reply["reply"]
            if not reply_path.startswith(consume_path):
                reply["reply"] = consume_path + "/" + reply_path

            self.ws.send(
                json.dumps(reply))

        impl(consume, callback)

    def __request(self, request):
        """
        Handles a request event, dispatching to the implementation
        function. The callback closure sends the reply event on
        the websocket.
        """
        request_path = request["request"]
        event_id = request["id"]
        impl = self.impl[request_path]

        def callback(reply):
            """
            Closure reinstates full reply path if not already present.
            """
            reply["id"] = event_id

            reply_path = reply["reply"]
            if not reply_path.startswith(request_path):
                reply["reply"] = request_path + "/" + reply_path

            self.ws.send(
                json.dumps(reply))

        impl(request, callback)

    def __response(self, response):
        """
        Handles a response event, retrieving and invoking the callback.
        """
        response_path = response["response"]
        response["response"] = response_path.split("/")[-1]
        event_id = response["id"]
        callback = self.pending.pop(event_id)
        callback(response)

    def __str__(self):
        return "Service <" + self.service + ">"


def random_id():
    """
    Utility function returns a random string of length 10.
    """
    return ''.join(
        random.choice(
            string.ascii_uppercase + string.digits) for _ in range(10))
