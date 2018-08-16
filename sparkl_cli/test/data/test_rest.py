"""
Copyright (c) 2018 SPARKL Limited. All Rights Reserved.
Author <jacoby@sparkl.com> Jacoby Thwaites.

Implementation module for primes provides the mandatory onopen and
optional onclose functions.

"""
import math


def onopen(service):
    """
    This mandatory function installs the implementation
    dict in the service on open.
    """
    service.impl = {
        "Mix/FirstDivisor": first_divisor,
        "Mix/Test":         test,
        "Mix/Iterate":      iterate,
        "Mix/Consume":      consume}

    print("Open")


def onclose(service):
    print("Close")


def first_divisor(request, callback):
    """
    Returns the first divisor for testing.
    """
    callback({
        "reply": "Ok",
        "data": {
          "div": 2
        }
    })


def test(request, callback):
    """
    Returns No or Iterate.
    """
    n = request["data"]["n"]
    div = request["data"]["div"]
    if n % div == 0:
        callback({
            "reply": "No"})
    else:
        callback({
            "reply": "Iterate"})


def iterate(request, callback):
    """
    Returns the next n, div pair or stop if div > sqrt(n).
    """
    (n, div) = (request["data"]["n"], request["data"]["div"])
    if div > math.sqrt(n):
        callback({
            "reply": "Stop"
        })
    else:
        next_div = 3 if div == 2 else div + 2
        callback({
            "reply": "Next",
            "data": {
                "n": n,
                "div": next_div
            }
        })


consumes = []


def consume(consume):
    """
    Adds the consume event to the module consumes list.
    """
    consumes.append(consume)
