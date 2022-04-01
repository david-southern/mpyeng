from collections import namedtuple
import adafruit_logging as logging

logger = logging.getLogger("utils")


def safeString(thingy, defaultString):
    return str(thingy) if thingy is not None else defaultString


def shortString(string, maxLen=200):
    if (string is None) or (len(string) == 0):
        return ""
    if len(string) > maxLen:
        return string[:maxLen] + "..."
    return string


def format_hex(val):
    return f"0x{int(val):02X}"


def format_hex_list(listVal, delimiter=", "):
    return delimiter.join(f"{format_hex(val)}" for val in listVal)


class User(object):
    def __init__(self, name, username):
        self.name = name
        self.username = username


import json

j = json.loads('{"name": "John Smith", "username": "bobber"}')
u = User(**j)

logger.info(f"Json test: User: {u.name}, {u.username}")
