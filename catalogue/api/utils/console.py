# coding: utf-8

from __future__ import unicode_literals
from difflib import SequenceMatcher
import subprocess
from django.utils.encoding import smart_text


def notify_send(msg):
    subprocess.call(['notify-send', msg])


PRINT_COLORS = {
    'normal':            '\033[0m',
    'red':               '\033[91m',
    'green':             '\033[92m',
    'yellow':            '\033[93m',
    'blue':              '\033[94m',
    'purple':            '\033[95m',
    'red_background':    '\033[41m',
    'green_background':  '\033[42m',
    'yellow_background': '\033[43m',
    'blue_background':   '\033[44m',
    'purple_background': '\033[45m',
}


def colored(msg, color):
    if not msg:
        return ''
    return ''.join(smart_text(s) for s in (
        PRINT_COLORS[color],
        msg,
        PRINT_COLORS['normal']
    ))


def red_bg(msg):
    return colored(msg, 'red_background')


def green_bg(msg):
    return colored(msg, 'green_background')


def yellow_bg(msg):
    return colored(msg, 'yellow_background')


def blue_bg(msg):
    return colored(msg, 'blue_background')


def purple_bg(msg):
    return colored(msg, 'purple_background')


def error(msg):
    return colored(msg, 'red')


def warning(msg):
    return colored(msg, 'yellow')


def success(msg):
    return colored(msg, 'green')


def info(msg):
    return colored(msg, 'blue')


def print_error(msg):
    print(error(smart_text(msg)))


def print_warning(msg):
    print(warning(smart_text(msg)))


def print_success(msg):
    print(success(smart_text(msg)))


def print_info(msg):
    print(info(smart_text(msg)))


def colored_diff(a, b):
    s = SequenceMatcher(lambda x: x == ' ', a, b)
    new_a = ''
    new_b = ''
    end_a = 0
    end_b = 0
    for ia, ib, l in s.get_matching_blocks():
        new_a += blue_bg(a[end_a:ia])
        new_b += blue_bg(b[end_b:ib])
        end_a = ia + l
        end_b = ib + l
        new_a += a[ia:end_a]
        new_b += b[ib:end_b]
    new_a += blue_bg(a[end_a:])
    new_b += blue_bg(b[end_b:])
    return new_a, new_b
