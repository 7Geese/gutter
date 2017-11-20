from functools import partial

from .base import Container, argument  # noqa
from .variables import Value, Boolean, String, Integer, Float

Value = partial(argument, Value)
Boolean = partial(argument, Boolean)
String = partial(argument, String)
Integer = partial(argument, Integer)
Float = partial(argument, Float)
