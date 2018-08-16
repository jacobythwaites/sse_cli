"""
Copyright (c) 2018 SPARKL Limited. All Rights Reserved.
Author <jacoby@sparkl.com> Jacoby Thwaites.

Test service whose close function must be invoked.
"""


def onopen(service):
    service.properly_closed = False


def onclose(service):
    service.properly_closed = True
