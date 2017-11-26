# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import jsonpickle as pickle
from durabledict.encoding import PickleEncoding


class JsonPickleEncoding(PickleEncoding):
    @staticmethod
    def encode(data):
        return pickle.dumps(data)

    @staticmethod
    def decode(data):
        try:
            return pickle.loads(data)
        except Exception:
            return PickleEncoding.decode(data)
