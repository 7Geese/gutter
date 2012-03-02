import unittest
from mock import MagicMock, Mock
from nose.tools import *
from gargoyle.client.inputs.arguments import *


class BaseArgument(object):

    def setUp(self):
        self.argument = self.klass(self.valid_comparison_value)

    @property
    def interface_functions(self):
        return ['__cmp__', '__hash__', '__nonzero__']

    @property
    def interface_methods(self):
        return [getattr(self.argument, f) for f in self.interface_functions]

    def test_implements_comparison_methods(self):
        map(ok_, self.interface_methods)


class DelegateToValue(object):

    def test_delegates_all_interface_function_to_the_value_passed_in(self):
        value_passed_in = MagicMock()
        value_passed_in.__cmp__ = Mock()
        argument = self.klass(value_passed_in)

        for function in self.interface_functions:
            values_function = getattr(value_passed_in, function)
            arguments_function = getattr(argument, function)

            arguments_function(self.valid_comparison_value)
            values_function.assert_called_once_with(self.valid_comparison_value)


class ValueTest(BaseArgument, DelegateToValue, unittest.TestCase):

    klass = Value

    @property
    def valid_comparison_value(self):
        return 'marv'


class BooleanTest(BaseArgument, DelegateToValue, unittest.TestCase):

    klass = Boolean

    @property
    def valid_comparison_value(self):
        return True

    @property
    def interface_functions(self):
        return ['__cmp__', '__nonzero__']

    def test_hashes_its_hash_value_instead_of_value(self):
        boolean = Boolean(True, hash_value='another value')
        assert_not_equals(hash(True), hash(boolean))
        assert_equals(hash('another value'), hash(boolean))

    def test_creates_random_hash_value_if_not_provided(self):
        boolean = Boolean(True)
        assert_not_equals(hash(True), hash(boolean))
        assert_not_equals(hash(None), hash(boolean))

        assert_not_equals(hash(boolean), hash(Boolean(True)))


class StringTest(BaseArgument, DelegateToValue, unittest.TestCase):

    klass = String

    @property
    def valid_comparison_value(self):
        return 'foobazzle'

    @property
    def interface_functions(self):
        return ['__hash__']

    def test_cmp_compares_with_other_value(self):
        eq_(self.argument.__cmp__('zebra'), -1)
        eq_(self.argument.__cmp__('aardvark'), 1)
        eq_(self.argument.__cmp__('foobazzle'), 0)

    def test_nonzero_returns_if_truthy(self):
        ok_(String('hello').__nonzero__() is True)
        ok_(String('').__nonzero__() is False)
        ok_(String('0').__nonzero__() is True)
