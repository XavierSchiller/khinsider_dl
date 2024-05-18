import sys


def printerr(error: str):
    print(error, file=sys.stderr)


def printerrors(errors: list[str]):
    for error in errors:
        printerr(error)
