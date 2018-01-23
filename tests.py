from unittest import TestCase, main
from tree import HuffmanTree
from bitoperations import file_chunks, create_bytes
from comp import encode, compress_one_byte, compress, EmptyFile
from decomp import extract_codes, decode, decompress
from collections import Counter
from io import StringIO, BytesIO


class TestBitMethods(TestCase):
    def test_file_chunks(self):
        # First word - number of bytes, second word - reading size.
        names = ('empty', 'one_one', 'one_two', 'two_one', 'two_two', 'two_three',
                 'three_one', 'three_two', 'three_three',
                 'ten_one', 'ten_four', 'ten_ten')
        cases = (b'', b'a', b'\xff', b'a\x0f', b'\xff\x23', b'\x12\x34',
                 b'abc', b'def', b'ghi',
                 b'1234567890', b'abcdefghio', b'1234567890')
        sizes = (10, 1, 2, 1, 2, 3, 1, 2, 3, 1, 4, 10)
        real_results = (
            (),
            (b'a',),
            (b'\xff',),
            (b'a', b'\x0f'),
            (b'\xff\x23',),
            (b'\x12\x34',),
            (b'a', b'b', b'c'),
            (b'de', b'f'),
            (b'ghi',),
            (b'1', b'2', b'3', b'4', b'5', b'6', b'7', b'8', b'9', b'0'),
            (b'abcd', b'efgh', b'io'),
            (b'1234567890',)
            )
        for name, case, size, real_result in zip(names, cases, sizes, real_results):
            self.assertEqual(tuple(file_chunks(BytesIO(case), size)), real_result,
                                     'Error in test {0}'.format(name))

    def test_create_bytes(self):
        names = ('empty', 'one', 'two', 'seven', 'eight', 'nine', 'sixteen', 'thirty')
        args = (
            '',
            '0',
            '01',
            '0101001',
            '10101010',
            '101010101',
            '1010101010101010',
            30 * '0'
            )
        real_results = (
            (b'', ''),
            (b'', '0'),
            (b'', '01'),
            (b'', '0101001'),
            (b'\xaa', ''),
            (b'\xaa', '1'),
            (b'\xaa\xaa', ''),
            (b'\x00\x00\x00', '000000')
            )

        for name, arg, real_result in zip(names, args, real_results):
            self.assertEqual(create_bytes(arg), real_result,
                             'Error in test {0}.'.format(name))


class TestTreeMethods(TestCase):
    def test_serialize(self):
        names = ('two', 'three', 'four', 'five',
                 'two_rep','three_rep', 'four_rep', 'five_rep')
        args = (
            Counter(b'ab'),
            Counter(b'abc'),
            Counter(b'abcd'),
            Counter(b'\x00\xffabc'),
            Counter(b'aab'),
            Counter(b'aabbbcccc'),
            Counter(b'abcdabcdabcd'),
            Counter(b'aaaabbbbccccddddeeee')
            )
        real_results = (
            ''.join(('00000001', '01100001', '01100010', '110101')),
            ''.join(('00000010', '01100011', '01100001', '01100010',
                     '11101001', '011')),
            ''.join(('00000011', '01100001', '01100010', '01100011',
                     '01100100', '11110010', '11001011')),
            ''.join(('00000100', '01100010', '01100011', '11111111',
                     '00000000', '01100001', '11110010', '11001001', '0111')),
            ''.join(('00000001', '01100010', '01100001', '10101')),
            ''.join(('00000010', '01100011', '01100001', '01100010',
                     '11010010', '11')),
            ''.join(('00000011', '01100001', '01100010', '01100011',
                     '01100100', '11110010', '11001011')),
            ''.join(('00000100', '01100011', '01100100', '01100101',
                     '01100001', '01100010', '00101100', '10010111'))
            )

        for name, arg, real_result in zip(names, args, real_results):
            self.assertEqual(HuffmanTree(arg).serialize(), real_result,
                             'Error in test {0}.'.format(name))


class TestCompressFunctions(TestCase):
    def test_encode(self):
        names = ('empty', 'one', 'another', 'two_diff', 'two_same', 'five')
        args = (
            (b'', {}),
            (b'a', dict(zip(bytearray(b'a'), ['101']))),
            (b'\xff', dict(zip(bytearray(b'\xff'), ['0']))),
            (b'a\xff', dict(zip(bytearray(b'a\xff'), ['0', '1']))),
            (b'aa', dict(zip(bytearray(b'ab'), ['0', '1']))),
            (b'aabbc', dict(zip(bytearray(b'abc'), ['00', '1', '11'])))
            )
        real_results = ('', '101', '0', '01', '00', '00001111')

        for name, arg, real_result in zip(names, args, real_results):
            self.assertEqual(encode(*arg), real_result,
                             'Error in test {0}.'.format(name))

    def test_compress_one_byte(self):
        names = ('one', 'two', 'three', 'ten')
        args = (
            Counter(b'a'),
            Counter(b'\xff\xff'),
            Counter(b'\x00\x00\x00'),
            Counter(b'cccccccccc')
            )
        real_results = (
            bytearray(b'\x00a\x01'),
            bytearray(b'\x00\xff\x02'),
            bytearray(b'\x00\x00\x03'),
            bytearray(b'\x00c\x0a')
            )

        for name, arg, real_result in zip(names, args, real_results):
            self.assertEqual(compress_one_byte(arg), real_result,
                             'Error in test {0}.'.format(name))

    def test_compress(self):
        # Empty file test.
        empty = BytesIO()
        empty.name = 'empty'
        self.assertRaises(EmptyFile, compress, empty, BytesIO())
        
        names = ('one', 'one_repeated', 'one_large', 'two', 'couple', 'large')
        cases = (
            b'a',
            b'aa',
            3*10**6 * b'\xff',
            b'ab',
            b'abcdef\xff',
            10**7 * b'a' + 10**7 * b'\xff' + 10**7 * b'c'
            )
        real_results = (
            b'\x00a\x01',
            b'\x00a\x02',
            b'\x00\xff' + int(3000000).to_bytes(3, 'big'),
            b'\x01ab\xd5',
            b'\x06\xffabcdef\xf2\x5c\x59\x74\xe5\xdc',
            b'\x02\xffac\x4b' + 2500000*b'\xaa' + 1250000*b'\x00' + 2500000*b'\xff'
        )
        
        for name, case, real_result in zip(names, cases, real_results):
            infile, outfile = BytesIO(case), BytesIO()
            compress(infile, outfile)
            outfile.seek(0)
            self.assertEqual(outfile.read(), real_result,
                             'Error in test {0}'.format(name))


class TestDecompressFunctions(TestCase):
    def test_extract_codes(self):
        names = ('two', 'three', 'four', 'five')
        args = (
            '0101',
            '01001011',
            '001011001011',
            '0010110010010111'
            )
        real_results = (
            ['0', '1'],
            ['0', '10', '11'],
            ['00', '01', '10', '11'],
            ['00', '01', '10', '110', '111']
            )

        for name, arg, real_result in zip(names, args, real_results):
            self.assertEqual(extract_codes(arg), real_result,
                             'Error in test {0}'.format(name))

    def test_decode(self):
        names = ('empty', 'one', 'one_rest', 'two', 'two_rest', 'four', 'four_rest')
        args = (
            ('', {'0': 97, '1': 98}),
            ('0', {'0': 97, '1': 98}),
            ('01', {'0': 97, '10': 98, '11': 99}),
            ('01', {'0': 97, '1': 98}),
            ('0101', {'0': 97, '10': 98, '11': 99}),
            ('00011011', {'00': 97, '01': 98, '10': 99, '11': 100}),
            ('000110110', {'00': 97, '01': 98, '10': 99, '11': 100})
            )
        real_results = (
            (b'', ''),
            (b'a', ''),
            (b'a', '1'),
            (b'ab', ''),
            (b'ab', '1'),
            (b'abcd', ''),
            (b'abcd', '0')
            )

        for name, arg, real_result in zip(names, args, real_results):
            self.assertEqual(decode(*arg), real_result,
                             'Error in test {0}'.format(name))

    def test_decompress(self):
        names = ('one', 'one_repeated', 'one_large', 'two', 'couple', 'large')
        cases = (
            b'\x00a\x01',
            b'\x00a\x02',
            b'\x00\xff' + int(3000000).to_bytes(3, 'big'),
            b'\x01ab\xd5',
            b'\x06\xffabcdef\xf2\x5c\x59\x74\xe5\xdc',
            b'\x02\xffac\x4b' + 2500000*b'\xaa' + 1250000*b'\x00' + 2500000*b'\xff'
            )
        real_results = (
            b'a',
            b'aa',
            3*10**6 * b'\xff',
            b'ab',
            b'abcdef\xff',
            10**7 * b'a' + 10**7 * b'\xff' + 10**7 * b'c'
            )

        for name, case, real_result in zip(names, cases, real_results):
            infile, outfile = BytesIO(case), BytesIO()
            decompress(infile, outfile)
            outfile.seek(0)
            self.assertEqual(outfile.read(), real_result,
                             'Error in test {0}'.format(name))


if __name__ == '__main__':
    main()
