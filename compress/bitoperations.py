"""
Module defines functions to help with operations on binary data.

Functions:
part() -- Partition string on given position and return parts.
int_to_bits() -- Change int to binary string.
file_chunks() -- Return iterator to read file chunk by chunk.
create_bytes() -- Create bytes object from binary string.
bits_from_bytes() -- Create binary string from bytes.

Data:
default_size -- Default size of one file read.
"""


from functools import partial


# Default size of one file read.
default_size = 1024 * 1024


def part(string, pos):
    """
    Partition string on given position and return parts.

    Args:
    string -- String to be partitioned.
    pos -- Position of partition. Character at pos position will be in second part.
    """
    return string[:pos], string[pos:]


def int_to_bits(num, length=None):
    """
    Change non-negative int to binary string.

    Args:
    num -- Number to be changed into binary string.
    length -- Length of created binary string. If argument is omitted, length
              of binary string will be equal to length of binary representation
              of num.
    """
    bin_repr = bin(num)[2:]
    if length is None:
        length = num.bit_length()
    binstring = bin_repr.zfill(length)
    return binstring


def file_chunks(infile, size):
    """
    Return iterator to read file chunk by chunk.

    Args:
    infile -- File object to read from.
    size -- Size of a chunk.
    """
    return iter(partial(infile.read, size), b'')


def create_bytes(bits):
    """
    Create bytes object from binary string.

    Function creates as many bytes as possible from binary string. Rest of
    it is also returned.

    Args:
    bits -- Binary string.

    Returns:
    outbytes -- Created bytes object.
    rest -- Rest of binary string (might be empty).
    """
    out_length = len(bits)//8
    # Cutting longest part, which length is divisible by 8.
    outbits, rest = part(bits, 8 * out_length)
    outbytes = int(outbits, 2).to_bytes(out_length, 'big') if outbits else b''
    return outbytes, rest


def bits_from_bytes(bytesobj):
    """
    Create binary string from bytes.

    Args:
    bytesobj -- Bytes to create binary string from.
    """
    return bin(int.from_bytes(bytesobj, 'big'))[2:].zfill(8 * len(bytesobj))
