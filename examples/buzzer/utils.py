# pylint: disable=missing-module-docstring,missing-function-docstring,missing-class-docstring
import time


def log(msg):
    print(f"{time.monotonic()} - {msg}")
