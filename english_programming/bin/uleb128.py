def write_uleb128(n: int) -> bytes:
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        if n:
            out.append(b | 0x80)
        else:
            out.append(b)
            break
    return bytes(out)


def write_sleb128(n: int) -> bytes:
    out = bytearray()
    more = True
    while more:
        b = n & 0x7F
        n >>= 7
        sign = b & 0x40
        if (n == 0 and sign == 0) or (n == -1 and sign != 0):
            more = False
        else:
            b |= 0x80
        out.append(b)
    return bytes(out)


def read_uleb128(buf: bytes, i: int):
    result = 0
    shift = 0
    while True:
        b = buf[i]
        i += 1
        result |= (b & 0x7F) << shift
        if (b & 0x80) == 0:
            return result, i
        shift += 7


def read_sleb128(buf: bytes, i: int):
    result = 0
    shift = 0
    size = 64
    while True:
        b = buf[i]
        i += 1
        result |= (b & 0x7F) << shift
        cont = b & 0x80
        shift += 7
        if not cont:
            if (shift < size) and (b & 0x40):
                result |= - (1 << shift)
            return result, i


