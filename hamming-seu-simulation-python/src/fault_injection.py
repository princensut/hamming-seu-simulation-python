"""Fault injection: flip bits to emulate single-event upsets (SEUs).

Every function returns a NEW list and leaves the input untouched.
A numpy random generator (rng) is passed in so that runs are repeatable.
"""


def flip_bit(bits, index):
    """Flip the bit at a 0-based index."""
    out = list(bits)
    out[index] ^= 1
    return out


def flip_random_bit(bits, rng):
    """Flip exactly one randomly chosen bit."""
    index = int(rng.integers(0, len(bits)))
    return flip_bit(bits, index)


def flip_random_bits(bits, count, rng):
    """Flip `count` different randomly chosen bits."""
    indices = rng.choice(len(bits), size=count, replace=False)
    out = list(bits)
    for index in indices:
        out[int(index)] ^= 1
    return out


def flip_each_bit(bits, probability, rng):
    """Flip every bit independently with the given probability."""
    return [bit ^ int(rng.random() < probability) for bit in bits]