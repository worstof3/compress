from tree import HuffmanTree
from collections import Counter
from math import ceil
from itertools import chain
from functools import partial
from bitbuffer import default_size, OutBitBuffer
from argparse import ArgumentParser, SUPPRESS

# Todo: handling empty file and file with just one byte.
# Todo: tests.
# Todo: documentation.

def encode(text, bytes_codes):
    codes = map(lambda x: bytes_codes[x], text)
    return ''.join(codes)

def file_chunks(infileobj, size):
    return iter(partial(infileobj.read, size), b'')

def calc_freqs(infileobj):
    freqs = Counter()
    for chunk in file_chunks(infileobj, default_size):
        freqs.update(chunk)

    # We need to move file pointer to the beginning, because we will be traversing file once more.
    infileobj.seek(0)
    return freqs

def compress(infile, outfile):
    with open(infile, 'rb') as infileobj, \
         OutBitBuffer(outfile) as outbuffer:
        freqs = calc_freqs(infileobj)
        tree = HuffmanTree(freqs)
        # Creating binary representation of a tree.
        serialized = tree.serialize()

        # Encoding and writing to file.
        outbuffer.write(serialized)
        for chunk in file_chunks(infileobj, default_size):
            encoded = encode(chunk, tree.bytes_codes)
            outbuffer.write(encoded)

def extract_codes(tree_bits):
    codes = []
    code = []
    for prev, cur in zip(chain('0', tree_bits), tree_bits):
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
    return codes
            
        
def read_header(infileobj):
    # Reading tree representation.
    bytes_num = ord(infileobj.read(1)) + 1
    leaf_bytes = infileobj.read(bytes_num)
    # Tree with l leaves is written with 4*l - 4 bits.
    tree_bytes = infileobj.read( ceil( (4*bytes_num - 4)/8 ) + 1 )

    # Removing align from the representation.
    if tree_bytes[0].bit_length() == 8:
        first_byte = bin(tree_bytes[0])[2:].lstrip('1')
    else:
        first_byte = bin(tree_bytes[0])[2:].zfill(8)

    # Extracting codes from the tree representation.
    tree_bits = ''.join(chain(first_byte, map(lambda x: bin(x)[2:].zfill(8), tree_bytes[1:])))
    codes = extract_codes(tree_bits[ : 4*bytes_num - 4])

    # Mapping codes on bytes.
    codes_bytes = {code: byte for code, byte in zip(codes, leaf_bytes)}
    rest = tree_bits[4*bytes_num - 4 : ]
    return codes_bytes, rest

def decode(encoded, codes_bytes):
    code = ''
    decoded = bytearray()
    for bit in encoded:
        code += bit
        if code in codes_bytes:
            decoded.append(codes_bytes[code])
            code = ''
    return decoded, code

def decompress(infile, outfile):
    with open(infile, 'rb') as infileobj, \
         open(outfile, 'wb') as outbuffer:
        # Extracting codes from file header and mapping on bytes.
        codes_bytes, rest = read_header(infileobj)

        # Decoding file.
        for chunk in file_chunks(infileobj, default_size):
            encoded = ''.join(chain(rest, map(lambda x: bin(x)[2:].zfill(8), chunk)))
            decoded, rest = decode(encoded, codes_bytes)
            outbuffer.write(decoded)

if __name__ == '__main__':
    # Adding arguments.
    parser = ArgumentParser(description='Compression tool.')
    parser.add_argument('infile', default=SUPPRESS, help='Input file.')
    parser.add_argument('-o', '--outfile', default=None,
                        help="Output file. If this option is omitted outfile name\
                        is set to infile.comp, if infile is compressed, infile.decomp,\
                        if infile is decompressed and it doesn't end with .comp. \
                        If infile is decompressed and its like name.comp, outfile \
                        is set to name.")
    parser.add_argument('-d', '--decompress', action='store_const', dest='operation',
                        default=compress, const=decompress, help='Decompress file.')

    args = parser.parse_args()
    # Setting default output file name.
    if args.outfile is None:
        if args.operation == decompress:
            if args.infile.endswith('.comp') and len(args.infile) > 5:
                args.outfile = args.infile[:-5]
            else:
                args.outfile = args.infile + '.decomp'
        else:
            args.outfile = args.infile + '.comp'

    args.operation(args.infile, args.outfile)
