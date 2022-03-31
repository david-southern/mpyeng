import board

def safeString(thingy, defaultString):
    return str(thingy) if thingy is not None else defaultString

def format_hex(val):
    return f"0x{int(val):02X}"

def format_hex_list(listVal, delimiter = ", "):
    return delimiter.join(f"{format_hex(val)}" for val in listVal)