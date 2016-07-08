import sys
dprint = print
debug = 0


def print(*args, sep=' ', end='\n'):
    if debug:
        dprint("ST_DB: ", *args)
