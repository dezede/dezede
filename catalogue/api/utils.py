# coding: utf-8

from __future__ import unicode_literals
import os
from django.utils.encoding import smart_unicode


def notify_send(msg):
    os.system('notify-send "%s"' % msg)


PRINT_COLORS = {
    'normal': '\033[0m',
    'red': '\033[91m',
    'green': '\033[92m',
    'yellow': '\033[93m',
    'blue':'\033[94m',
    'purple': '\033[95m',
}


def colored_print(msg, color='red'):
    print PRINT_COLORS[color] + smart_unicode(msg) + PRINT_COLORS['normal']


def print_error(msg):
    colored_print(msg, color='red')


def print_warning(msg):
    colored_print(msg, color='yellow')


def print_success(msg):
    colored_print(msg, color='green')


def print_info(msg):
    colored_print(msg, color='blue')
