from django.template import Library
import math


register = Library()


@register.filter
def absolute(x):
    return abs(x)


@register.filter
def subtract(x, y):
    return x - y


@register.filter
def multiply(x, y):
    return x * y


@register.filter
def divide(x, y):
    return x / y


@register.filter
def idivide(x, y):
    return x // y


@register.filter
def log_ratio(x, y, z=math.e):
    if x == 0:
        return 0

    def log(n):
        if n > 0:
            return pow(n, 1 / z)
        return -pow(-n, 1 / z)

    return log(x) / log(y)


@register.filter
def modulo(x, y):
    return x % y

