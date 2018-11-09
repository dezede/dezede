import json
import os.path
import sys
from django.db.models.query import QuerySet


SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))


def script_iterator(l):
    if isinstance(l, QuerySet):
        count = l.count()
    else:
        l = list(l)
        count = len(l)
    for i, obj in enumerate(l):
        yield obj
        sys.stdout.write(('\r\x1b[K%s %%' % (100 * i / count)).ljust(10))
        sys.stdout.flush()
    print


def load_or_dump_json(json_name):
    def wrapped_wrapped(fn):
        def wrapped():
            path = os.path.join(SCRIPT_PATH, json_name)
            if os.path.exists(path):
                with open(path) as f:
                    return json.loads(f.read())

            result = fn()

            with open(path, 'w') as f:
                f.write(json.dumps(result))
            return result

        return wrapped

    return wrapped_wrapped
