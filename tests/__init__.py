from __future__ import unicode_literals


def datapath(*name):
    import os
    path = os.path.dirname(__file__)
    path = os.path.join(path, 'data')
    path = os.path.abspath(path)
    return os.path.join(path, *name)
