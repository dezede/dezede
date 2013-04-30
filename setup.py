# Imports, sorted alphabetically.

# Python packages
from Cython.Distutils import build_ext
from distutils.core import setup
from distutils.extension import Extension
import os

# Third-party packages
# Nothing for now...

# Modules from this project
# Nothing for now...


excluded_modules = (
)


def path_to_module(path):
    return '.'.join(s for s in path.split('.')[0].split('/')
                    if s != '__init__')


def get_modules(path=None):
    first = False
    if path is None:
        path = os.path.abspath(os.path.dirname(__file__))
        first = True
    for f_or_d in os.listdir(path):
        if not first:
            f_or_d = os.path.join(path, f_or_d)
        if os.path.isdir(f_or_d):
            d = f_or_d
            if path_to_module(d) + '.*' in excluded_modules:
                continue
            for name, f in get_modules(d):
                yield name, f
        else:
            f = f_or_d
            if f.endswith(('.py', 'pyx')):
                if not(f[-3:] == '.py' and os.path.exists(f[:-3] + '.pxd')):
                    continue
                name = path_to_module(f)
                if name and name not in excluded_modules:
                    yield name, f

ext_modules = [Extension(name, [f]) for name, f in get_modules()]

setup(
    name='libretto',
    cmdclass={'build_ext': build_ext},
    ext_modules=ext_modules,
)