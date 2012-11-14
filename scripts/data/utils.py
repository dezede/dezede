import os.path


def open_relative_file(file_name):
    return open(os.path.join(os.path.dirname(__file__), file_name))

def open_relative_files(file_names):
    return [open_relative_file(file_name) for file_name in file_names]
