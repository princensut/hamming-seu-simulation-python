"""pytest tests for the Hamming(7,4) code. Run with:  pytest"""
from itertools import combinations

from hamming import bits_to_int, decode, encode, int_to_bits, syndrome
from fault_injection import flip_bit

ALL_WORDS = [int_to_bits(v, 4) for v in range(16)]


def test_int_bit_conversion_roundtrip():
    for value in range(16):
        assert bits_to_int(int_to_bits(value, 4)) == value


def test_clean_roundtrip_all_16_words():
    for data in ALL_WORDS:
        decoded, s = decode(encode(data))
        assert decoded == data
        assert s == 0


def test_syndrome_is_zero_for_every_codeword():
    for data in ALL_WORDS:
        assert syndrome(encode(data)) == 0


def test_corrects_every_single_bit_error():
    # 16 words x 7 positions = 112 cases, checked exhaustively
    for data in ALL_WORDS:
        code = encode(data)
        for position in range(7):
            corrupted = flip_bit(code, position)
            decoded, s = decode(corrupted)
            assert decoded == data
            assert s == position + 1          # syndrome points at the flipped bit


def test_double_bit_errors_are_not_corrected():
    # Known limitation: any two errors give a wrong result (miscorrection).
    # 16 words x 21 position pairs = 336 cases, checked exhaustively.
    for data in ALL_WORDS:
        code = encode(data)
        for a, b in combinations(range(7), 2):
            corrupted = flip_bit(flip_bit(code, a), b)
            decoded, _ = decode(corrupted)
            assert decoded != data


def test_decode_does_not_modify_input():
    code = flip_bit(encode([1, 0, 1, 1]), 2)
    snapshot = list(code)
    decode(code)
    assert code == snapshot