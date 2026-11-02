"""Hamming(7,4) encoder and decoder.

Bit layout (positions are numbered 1 to 7, Python list index = position - 1):

    position:  1   2   3   4   5   6   7
    bit:       p1  p2  d1  p3  d2  d3  d4

Parity bits cover these positions (this is what makes the syndrome work):

    p1 covers positions 1, 3, 5, 7   ->  p1 = d1 ^ d2 ^ d4
    p2 covers positions 2, 3, 6, 7   ->  p2 = d1 ^ d3 ^ d4
    p3 covers positions 4, 5, 6, 7   ->  p3 = d2 ^ d3 ^ d4

All bits are plain ints (0 or 1) stored in lists.
"""


def int_to_bits(value, width=4):
    """Convert an integer to a list of bits, most significant bit first.

    Example: int_to_bits(5) -> [0, 1, 0, 1]
    """
    return [(value >> (width - 1 - i)) & 1 for i in range(width)]


def bits_to_int(bits):
    """Convert a list of bits (most significant first) back to an integer."""
    value = 0
    for bit in bits:
        value = (value << 1) | bit
    return value


def encode(data):
    """Encode 4 data bits [d1, d2, d3, d4] into a 7-bit Hamming codeword."""
    if len(data) != 4:
        raise ValueError("encode() needs exactly 4 data bits")
    d1, d2, d3, d4 = data
    p1 = d1 ^ d2 ^ d4
    p2 = d1 ^ d3 ^ d4
    p3 = d2 ^ d3 ^ d4
    return [p1, p2, d1, p3, d2, d3, d4]


def syndrome(code):
    """Return the syndrome of a 7-bit word as an integer from 0 to 7.

    Each check recomputes one parity group over the received bits.
    A check gives 0 if its group has an even number of ones (all fine).
    Combined, the three checks form a binary number:
      0 -> no error detected
      1..7 -> position (1-based) of the single flipped bit
    """
    if len(code) != 7:
        raise ValueError("syndrome() needs exactly 7 bits")
    c1, c2, c3, c4, c5, c6, c7 = code
    s1 = c1 ^ c3 ^ c5 ^ c7   # checks positions 1, 3, 5, 7
    s2 = c2 ^ c3 ^ c6 ^ c7   # checks positions 2, 3, 6, 7
    s3 = c4 ^ c5 ^ c6 ^ c7   # checks positions 4, 5, 6, 7
    return s1 + 2 * s2 + 4 * s3


def decode(code):
    """Decode a 7-bit word. Returns (data_bits, syndrome_value).

    If the syndrome is non-zero, the bit at that position is flipped back
    before the 4 data bits are read out. This corrects any single-bit error.
    With two or more errors the correction is wrong (a known limitation).
    """
    s = syndrome(code)
    fixed = list(code)               # work on a copy, never modify the input
    if s != 0:
        fixed[s - 1] ^= 1            # flip the faulty position back
    data = [fixed[2], fixed[4], fixed[5], fixed[6]]   # d1, d2, d3, d4
    return data, s