from __future__ import absolute_import, division, print_function, unicode_literals

from gutter.client.operators import Base
from gutter.client.registry import operators


class Truthy(Base):

    name = 'true'
    group = 'identity'
    preposition = 'true'

    def applies_to(self, argument):
        return bool(argument)

    def __str__(self):
        return 'true'


operators.register(Truthy)
