"""
Module defines functions for compressing files.

Classes:
EmptyFile -- Exception.

Functions:
encode() -- Encode bytes using given codes.
compress_one_byte() -- Compress file with only one byte (possibly repeated).
compress() -- Compress given file using Huffman coding.
"""


from math import ceil
from collections import Counter
from bitoperations import file_chunks, default_size, create_bytes
from tree import HuffmanTree


class EmptyFile(BaseException):
    """Exception raised when input file is empty."""


def encode(text, bytes_codes):
    """
    Encode bytes using given codes.

    Args:
    text -- Bytes to be encoded.
    bytes_codes -- Mapping bytes->codes.
    """
    codes = map(lambda x: bytes_codes[x], text)
    return ''.join(codes)


def compress_one_byte(freqs):
    """Compress file with only one byte (possibly repeated)."""
    pieces = [b'\x00']
    for byte, freq in freqs.items():
        pieces.append(byte.to_bytes(1, 'big'))
        pieces.append(freq.to_bytes(ceil(freq.bit_length()/8), 'big'))
    return b''.join(pieces)


def compress(infile, outfile):
    """
    Compress given file using Huffman coding.

    Empty file is not compressed. If file contains only one byte it's
    compressed to form ZeroByte_ByteInFile_RepeatNumber. If it contains
    at least two different bytes, Huffman tree is created. After compression
    file is in form TreeRepresentation_Encoding, TreeRepresentation
    is described in help to method serialize of clas HuffmanTree.

    Args:
    infile -- Fileobj of file to be compressed.
    outfile -- Fileobj to save compressed file.
    """
    # Calculating frequencies of each byte in an input file.
    freqs = Counter()
    for chunk in file_chunks(infile, default_size):
        freqs.update(chunk)
    infile.seek(0)

    if not freqs:
        raise EmptyFile('File "{0}" is empty.'.format(infile.name))
    # File with only one byte is compressed differently.
    elif len(freqs) == 1:
        repres = compress_one_byte(freqs)
        outfile.write(repres)
    else:
        tree = HuffmanTree(freqs)
        # Creating binary representation of a tree.
        serialized = tree.serialize()

        # Encoding and writing to file.
        outbytes, rest = create_bytes(serialized)
        outfile.write(outbytes)
        for chunk in file_chunks(infile, default_size):
            encoded = encode(chunk, tree.bytes_codes)
            outbytes, rest = create_bytes(rest + encoded)
            outfile.write(outbytes)
