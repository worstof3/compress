"""
Module defines functions for decompressing files.

Functions:
extract_codes() -- Extract codes used for encoding.
decode() -- Decode sequence of bits.
decompress() -- Decompress given file.
"""


from .bitoperations import file_chunks, default_size, bits_from_bytes, part
from math import ceil


def extract_codes(tree_bits):
    """
    Extract codes used for encoding.

    Each 01 in tree representation means leaf, 00 means moving left in the
    tree, 10 means going right and 11 means going up.
    Args:
    tree_bits -- Binary representation of a tree structure.
    """
    codes = []
    code = []
    prev = '0'
    for cur in tree_bits:
        if prev == '0':
            # 01 in representation means leaf.
            if cur == '1':
                codes.append(''.join(code))
                code.pop()
            # 00 in representation means we are going left in a tree.
            else:
                code.append('0')
        # 10 in representation means we are going right in a tree.
        elif cur == '0':
            code.append('1')
        # 11 in representation means we are just going up in a tree.
        else:
            code.pop()
        prev = cur
    return codes


def decode(encoded, codes_bytes):
    """
    Decode sequence of bits.

    Args:
    encoded -- Bits to be decoded.
    codes_bytes -- Mapping codes->bytes.

    Returns:
    decoded -- Decoded part.
    code -- Part of a next code (from other chunk).
    """
    code = ''
    decoded = bytearray()
    for bit in encoded:
        code += bit
        if code in codes_bytes:
            decoded.append(codes_bytes[code])
            code = ''
    return decoded, code


def decompress(infile, outfile):
    """
    Decompress given file.

    Args:
    infile -- Path to file to be decompressed.
    outfile -- Path to save decompressed file.
    """
    bytes_num = ord(infile.read(1)) + 1
    # Different compression for file containing only one byte.
    if bytes_num == 1:
        byte = infile.read(1)
        freq = int.from_bytes(infile.read(), 'big')
        outfile.write(freq * byte)
    else:
        # Reading tree representation.
        leaf_bytes = infile.read(bytes_num)
        # Length of tree structure representation with l leaves is 4*l - 4.
        length = ceil((4*bytes_num - 4)/8) + 1
        tree_bytes = infile.read(length)
        tree_bits = bits_from_bytes(tree_bytes)

        # Ignoring align, extracting representation and codes.
        start = tree_bits.find('0')
        tree_bits, rest = part(tree_bits[start:], 4*bytes_num - 4)
        codes = extract_codes(tree_bits)
        codes_bytes = dict(zip(codes, leaf_bytes))

        # Decoding file.
        for chunk in file_chunks(infile, default_size):
            encoded = rest + bits_from_bytes(chunk)
            decoded, rest = decode(encoded, codes_bytes)
            outfile.write(decoded)

        # It's possible that entire encoding is readed with tree representation.
        if rest:
            outfile.write(decode(rest, codes_bytes)[0])
