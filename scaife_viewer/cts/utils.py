import re
from itertools import zip_longest


def atoi(s):
    return int(s) if s.isdigit() else s


def natural_keys(s):
    return tuple([atoi(c) for c in re.split(r"(\d+)", s)])


def chunker(iterable, n):
    args = [iter(iterable)] * n
    for chunk in zip_longest(*args, fillvalue=None):
        yield [item for item in chunk if item is not None]
