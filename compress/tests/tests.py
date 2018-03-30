from unittest import TestCase, main, TestLoader
from ..tree import Node, HuffmanTree
from ..bitoperations import part, int_to_bits, file_chunks, create_bytes, bits_from_bytes
from ..comp import encode, compress_one_byte, compress, EmptyFile
from ..decomp import extract_codes, decode, decompress
from collections import Counter
from io import BytesIO


class TestBitMethods(TestCase):
    def test_part(self):
        bitstrings = (
            '',
            '0',
            '01',
            '010',
        )
        positions = (
            (0,),
            (0, 1),
            (0, 1, 2),
            (0, 1, 2, 3),
        )
        real_results = (
            (('', ''),),
            (('', '0'), ('0', '')),
            (('', '01'), ('0', '1'), ('01', '')),
            (('', '010'), ('0', '10'), ('01', '0'), ('010', '')),
        )

        for bitstring, pos_tuple, result_tuple in zip(bitstrings, positions, real_results):
            for position, real_result in zip(pos_tuple, result_tuple):
                with self.subTest(bitstring=bitstring, position=position, real_result=real_result):
                    self.assertEqual(part(bitstring, position), real_result)


    def test_int_to_bits(self):
        numbers = (
            0,
            1,
            2,
            16,
        )
        lengths = (
            (None, 1, 2),
            (None, 1, 3),
            (None, 3, 5),
            (None, 5, 10),
        )
        real_results = (
            ('0', '0', '00'),
            ('1', '1', '001'),
            ('10', '010', '00010'),
            ('10000', '10000', '0000010000'),
        )

        for number, len_tuple, result_tuple in zip(numbers, lengths, real_results):
            for length, real_result in zip(len_tuple, result_tuple):
                with self.subTest(number=number, length=length, real_result=real_result):
                    self.assertEqual(int_to_bits(number, length), real_result)


    def test_file_chunks(self):
        files = (
            b'',
            b'a',
            b'\xff',
            b'a\x0f',
            b'\xff\x23',
            b'\x12\x34',
            b'abc',
            b'def',
            b'ghi',
            b'1234567890',
            b'abcdefghio',
            b'1234567890'
        )
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
        for file, size, real_result in zip(files, sizes, real_results):
            with self.subTest(file=file, size=size, real_result=real_result):
                self.assertEqual(tuple(file_chunks(BytesIO(file), size)), real_result)

    def test_create_bytes(self):
        bitstrings = (
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

        for bitstring, real_result in zip(bitstrings, real_results):
            with self.subTest(bitstring=bitstring, real_result=real_result):
                self.assertEqual(create_bytes(bitstring), real_result)


    def test_bits_from_bytes(self):
        bytesobjects = (
            b'',
            b'\x00',
            b'\xff\xbb'
        )
        real_results = (
            '0',
            '00000000',
            '1111111110111011'
        )

        for bytesobj, real_result in zip(bytesobjects, real_results):
            with self.subTest(bytesobj=bytesobj, real_result=real_result):
                self.assertEqual(bits_from_bytes(bytesobj), real_result)


class TestTreeMethods(TestCase):
    def test_node_lt(self):
        self.assertLess(Node(2, b'a'), Node(3, b'ab'))
        self.assertLess(Node(2, b'a'), Node(2, b'b'))

    def test_node_eq(self):
        self.assertEqual(Node(2, b'a'), Node(2, b'a'))
        self.assertNotEqual(Node(2, b'a'), Node(2, b'b'))
        self.assertNotEqual(Node(2, b'a'), Node(3, b'a'))
        self.assertNotEqual(Node(2, b'a'), Node(3, b'b'))

    def test_create_tree(self):
        tree = HuffmanTree({b'a': 1, b'b': 1})
        self.assertEqual(tree.root, Node(b'ab', 2))
        self.assertEqual(tree.root.left, Node(b'a', 1))
        self.assertEqual(tree.root.right, Node(b'b', 1))

        tree = HuffmanTree({b'a': 2, b'b': 1, b'c': 1})
        self.assertEqual(tree.root, Node(b'abc', 4))
        self.assertEqual(tree.root.left, Node(b'a', 2))
        self.assertEqual(tree.root.right, Node(b'bc', 2))
        self.assertEqual(tree.root.right.left, Node(b'b', 1))
        self.assertEqual(tree.root.right.right, Node(b'c', 1))

    def test_bytes_codes_and_encoding_length(self):
        tree = HuffmanTree(Counter(b'ab'))
        tree.serialize()
        self.assertEqual(tree.encoding_length, 2)
        self.assertDictEqual(tree.bytes_codes, {ord('a'): '0', ord('b'): '1'})

        tree = HuffmanTree(Counter(b'aabc'))
        tree.serialize()
        self.assertEqual(tree.encoding_length, 6)
        self.assertDictEqual(tree.bytes_codes, {ord('a'): '0', ord('b'): '10', ord('c'): '11'})

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
            with self.subTest(name=name, arg=arg, real_result=real_result):
                self.assertEqual(HuffmanTree(arg).serialize(), real_result)


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


loader = TestLoader()
bit_tests = loader.loadTestsFromTestCase(TestBitMethods)
tree_tests = loader.loadTestsFromTestCase(TestTreeMethods)
compress_tests = loader.loadTestsFromTestCase(TestCompressFunctions)
decompress_tests = loader.loadTestsFromTestCase(TestDecompressFunctions)


if __name__ == '__main__':
    main()