class Equals(object):

    label = 'equals'
    description = 'Applies of the candidate equals the specified values.'

    def __init__(self, value):
        self.value = value

    def applies_to(self, argument):
        return argument == self.value


class Between(object):

    label = 'between'
    description = 'Applies if argument is between the upper and lower bounds'

    def __init__(self, lower, higher):
        self.lower = lower
        self.higher = higher

    def applies_to(self, argument):
        return argument > self.lower and argument < self.higher


class LessThan(object):

    label = 'before'
    description = 'Applies if argument is before value'

    def __init__(self, upper_limit):
        self.upper_limit = upper_limit

    def applies_to(self, argument):
        return argument < self.upper_limit


class LessThanOrEqualTo(LessThan):

    label = 'less_than_or_equal_to'
    descripion = 'Applies if argument is less than or equal to value'

    def applies_to(self, argument):
        return argument <= self.upper_limit


class MoreThan(object):

    label = 'more_than'
    description = 'Applies if argument is more than value'

    def __init__(self, lower_limit):
        self.lower_limit = lower_limit

    def applies_to(self, argument):
        return argument > self.lower_limit


class MoreThanOrEqualTo(MoreThan):

    label = 'more_than_or_equal_to'
    description = 'Applies if argument is more than or equal to value'

    def applies_to(self, argument):
        return argument >= self.lower_limit
