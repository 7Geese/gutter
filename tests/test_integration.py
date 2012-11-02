import unittest
from nose.tools import *

from gargoyle.client.operators.comparable import *
from gargoyle.client.operators.identity import *
from gargoyle.client.operators.misc import *
from gargoyle.client.models import Switch, Condition, Manager
from gargoyle.client.inputs.arguments import Value, Boolean, String
from gargoyle.client import signals

from exam.decorators import fixture, before, after
from exam.cases import Exam


class User(object):

    def __init__(self, name, age, location='San Francisco', married=False):
        self._name = name
        self._age = age
        self._location = location
        self._married = married

    def name(self):
        return String(self._name)

    def age(self):
        return Value(self._age)

    def location(self):
        return String(self._location)

    def married(self):
        return Boolean(self._married)


class TestIntegration(Exam, unittest.TestCase):

    @fixture
    def manager(self):
        return Manager(storage=dict())

    @before
    def build_objects(self):
        self.setup_inputs()
        self.setup_conditions()
        self.setup_switches()

    @after
    def reset_objects(self):
        signals.switch_registered.reset()
        signals.switch_unregistered.reset()
        signals.switch_updated.reset()

    def setup_inputs(self):
        self.jeff = User('jeff', 21)
        self.frank = User('frank', 10, location="Seattle")
        self.larry = User('bill', 70, location="Yakima", married=True)
        self.timmy = User('timmy', 12)
        self.steve = User('timmy', 19)

    def setup_conditions(self):
        self.age_65_and_up = Condition(User.age, MoreThanOrEqualTo(65))
        self.age_under_18 = Condition(User.age, LessThan(18))
        self.age_not_under_18 = Condition(User.age, LessThan(18), negative=True)
        self.age_21_plus = Condition(User.age, MoreThanOrEqualTo(21))
        self.age_between_13_and_18 = Condition(User.age, Between(13, 18))

        self.in_sf = Condition(User.location, Equals('San Francisco'))
        self.has_location = Condition(User.location, Truthy())

        self.three_quarters_married = Condition(User.married, Percent(75))
        self.ten_percent = Condition(User.name, Percent(10))
        self.upper_50_percent = Condition(User.name, PercentRange(50, 100))

    def setup_switches(self):
        self.add_switch('can drink', condition=self.age_21_plus)
        self.add_switch('can drink in europe', condition=self.age_21_plus, state=Switch.states.GLOBAL)
        self.add_switch('can drink:wine', condition=self.in_sf, concent=True)
        self.add_switch('retired', condition=self.age_65_and_up)
        self.add_switch('can vote', condition=self.age_not_under_18)
        self.add_switch('teenager', condition=self.age_between_13_and_18)
        self.add_switch('SF resident', condition=self.in_sf)
        self.add_switch('teen or in SF', self.age_between_13_and_18, self.in_sf)
        self.add_switch('teen and in SF', self.age_between_13_and_18,
                        self.has_location, compounded=True)
        self.add_switch('10 percent', self.ten_percent)
        self.add_switch('Upper 50 percent', self.upper_50_percent)

    def add_switch(self, name, condition=None, *conditions, **kwargs):
        switch = Switch(name, compounded=kwargs.get('compounded', False))
        switch.state = kwargs.get('state', Switch.states.SELECTIVE)
        conditions = list(conditions)

        if condition:
            conditions.append(condition)

        [switch.conditions.append(c) for c in conditions]
        kwargs.get('manager', self.manager).register(switch)
        return switch

    class inputs(object):

        def __init__(self, manager, *inputs):
            self.manager = manager
            self.manager.input(*inputs)

        def __enter__(self):
            return self

        def active(self, *args, **kwargs):
            return self.manager.active(*args, **kwargs)

        def __exit__(self, type, value, traceback):
            self.manager.flush()

    def test_basic_switches_work_with_conditions(self):

        with self.inputs(self.manager, self.larry) as context:
            ok_(context.active('can drink') is True)
            ok_(context.active('can drink in europe') is True)
            ok_(context.active('can vote') is True)
            ok_(context.active('SF resident') is False)
            ok_(context.active('retired') is True)
            ok_(context.active('10 percent') is False)
            ok_(context.active('Upper 50 percent') is True)

        with self.inputs(self.manager, self.jeff) as context:
            ok_(context.active('can drink') is True)
            ok_(context.active('can drink in europe') is True)
            ok_(context.active('can vote') is True)
            ok_(context.active('SF resident') is True)
            ok_(context.active('teenager') is False)
            ok_(context.active('teen or in SF') is True)
            ok_(context.active('teen and in SF') is False)
            ok_(context.active('10 percent') is False)
            ok_(context.active('Upper 50 percent') is True)

        with self.inputs(self.manager, self.frank) as context:
            ok_(context.active('can drink') is False)
            ok_(context.active('can drink in europe') is True)
            ok_(context.active('can vote') is False)
            ok_(context.active('teenager') is False)
            ok_(context.active('10 percent') is True)
            ok_(context.active('Upper 50 percent') is False)

    def test_can_use_extra_inputs_to_active(self):
        with self.inputs(self.manager, self.frank) as context:
            ok_(context.active('can drink') is False)
            ok_(context.active('can drink', self.larry) is True)

        with self.inputs(self.manager, self.larry) as context:
            ok_(context.active('can drink') is True)
            ok_(context.active('can drink', self.frank, exclusive=True) is False)

    def test_switches_with_multiple_inputs(self):

        with self.inputs(self.manager, self.larry, self.jeff) as context:
            ok_(context.active('can drink') is True)
            ok_(context.active('can drink in europe') is True)
            ok_(context.active('SF resident') is True)
            ok_(context.active('teenager') is False)
            ok_(context.active('10 percent') is False)
            ok_(context.active('Upper 50 percent') is True)

        with self.inputs(self.manager, self.frank, self.jeff) as context:
            ok_(context.active('can drink') is True)
            ok_(context.active('can drink in europe') is True)
            ok_(context.active('SF resident') is True)
            ok_(context.active('teenager') is False)
            ok_(context.active('10 percent') is True)
            ok_(context.active('Upper 50 percent') is True)

    def test_switches_can_concent_top_parent_switch(self):
        with self.inputs(self.manager, self.jeff) as context:
            ok_(context.active('can drink') is True)
            ok_(context.active('can drink in europe') is True)
            ok_(context.active('SF resident') is True)
            ok_(context.active('can drink:wine') is True)
        with self.inputs(self.manager, self.timmy) as context:
            ok_(context.active('can drink') is False)
            ok_(context.active('can drink in europe') is True)
            ok_(context.active('SF resident') is True)
            ok_(context.active('can drink:wine') is False)

    def test_switches_can_be_deregistered_and_then_autocreated(self):
        with self.inputs(self.manager, self.jeff) as context:
            ok_(context.active('can drink') is True)

            context.manager.unregister('can drink')
            assert_raises(ValueError, context.manager.active, 'can drink')

            context.manager.autocreate = True
            ok_(context.active('can drink') is False)

    class Callback(object):

        register_calls = []
        unregister_calls = []
        update_calls = []

        @classmethod
        def switch_added(klass, switch):
            klass.register_calls.append(switch)

        @classmethod
        def switch_removed(klass, switch):
            klass.unregister_calls.append(switch)

        @classmethod
        def switch_updated(klass, switch):
            klass.update_calls.append((switch, switch.changes))

    def test_can_register_signals_and_get_notified(self):
        signals.switch_registered.connect(self.Callback.switch_added)
        signals.switch_unregistered.connect(self.Callback.switch_removed)
        signals.switch_updated.connect(self.Callback.switch_updated)

        eq_(self.Callback.register_calls, [])
        eq_(self.Callback.unregister_calls, [])
        eq_(self.Callback.update_calls, [])

        switch = Switch('foo')

        self.manager.register(switch)
        eq_(self.Callback.register_calls, [switch])

        self.manager.unregister(switch.name)
        eq_(self.Callback.unregister_calls, [switch])

        self.manager.register(switch)
        eq_(self.Callback.register_calls, [switch, switch])

        switch.name = 'a new name'
        switch.state = Switch.states.GLOBAL
        self.manager.update(switch)

        change = self.Callback.update_calls[0]
        eq_(change[0], switch)
        changes = change[1]
        eq_(changes['name'], dict(current='a new name', previous='foo'))
        eq_(changes['state'], dict(current=Switch.states.GLOBAL, previous=Switch.states.DISABLED))

        switch.name = 'from save() call'
        switch.save()

        change = self.Callback.update_calls[1]
        eq_(change[0], switch)
        changes = change[1]
        eq_(changes['name'], dict(current='from save() call', previous='a new name'))

    def test_namespaes_keep_switches_isloated(self):
        germany = self.manager.namespaced('germany')
        usa = self.manager.namespaced('usa')

        self.add_switch('booze', condition=self.age_21_plus, manager=usa)
        self.add_switch('booze', condition=self.age_not_under_18, manager=germany)

        eq_(len(germany.switches), 1)
        eq_(len(usa.switches), 1)

        eq_(usa.switches[0].conditions, [self.age_21_plus])
        eq_(germany.switches[0].conditions, [self.age_not_under_18])

        with self.inputs(usa, self.jeff) as context:
            ok_(context.active('booze') is True)

        with self.inputs(usa, self.jeff, self.timmy) as context:
            ok_(context.active('booze') is True)  # Jeff is 21, so he counts
            ok_(context.active('booze', self.timmy, exclusive=True) is False)  # Timmy is 10

        with self.inputs(usa, self.timmy) as context:
            ok_(context.active('booze') is False)

        with self.inputs(usa, self.timmy, self.steve) as context:
            ok_(context.active('booze') is False)

        with self.inputs(germany, self.timmy) as context:
            ok_(context.active('booze') is False)  # 10 is still too young

        with self.inputs(germany, self.steve) as context:
            ok_(context.active('booze') is True)  # 19 is old enough!

        with self.inputs(germany, self.timmy, self.steve) as context:
            ok_(context.active('booze') is True)  # Cause steve is 19

        with self.inputs(germany, self.jeff, self.timmy) as context:
            ok_(context.active('booze') is True)  # Cause jeff is 21

        with self.inputs(germany, self.jeff) as context:
            ok_(context.active('booze', self.timmy, exclusive=True) is False)  # exclusive timmy is 10

    def test_namespace_switches_not_shared_with_parent(self):
        base = self.manager
        daughter = self.manager.namespaced('daughter')
        son = self.manager.namespaced('son')

        ok_(base.switches is not daughter.switches)
        ok_(base.switches is not son.switches)
        ok_(daughter.switches is not son.switches)

        daughter_switch = self.add_switch('daughter only', manager=daughter)
        son_switch = self.add_switch('son only', manager=son)

        eq_(daughter.switches, [daughter_switch])
        eq_(son.switches, [son_switch])

        ok_(daughter_switch not in base.switches)
        ok_(son_switch not in base.switches)
