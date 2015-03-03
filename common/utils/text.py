# coding: utf-8


def remove_windows_newlines(text):
    return text.replace('\r\n', '\n').replace('\r', '\n')