"""
Module defines class for representing Huffman tree.

Classes:

Node -- Node in Huffman tree.
HuffmanTree -- Huffman tree.
"""


from heapq import heapify, heappop, heappush
from functools import total_ordering
from itertools import chain
from collections import OrderedDict


@total_ordering
class Node:
    """
    Class representing node in Huffman tree.

    Special methods:
    __init__() -- Initialize attributes.
    __lt__() -- Frequencies comparison.
    __eq__() -- Frequencies comparison.

    Attributes:
    byte -- Byte associated with node, only in leaves it's not empty.
    freq -- Frequency of a byte.
    left -- Left son of a node.
    right -- Right son of a node.
    """

    def __init__(self, byte, freq):
        """
        Initialize attributes.

        Args:
        byte -- Byte associated with node.
        freq -- Frequency of a byte.
        """
        self.byte = byte
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        """Frequency comparison."""
        return self.freq < other.freq

    def __eq__(self, other):
        """Frequency comparison."""
        return self.freq == other.freq


class HuffmanTree:
    """
    Class representing Huffman tree.

    Methods:
    serialize() -- Create binary representation of a tree.

    Special methods:
    __init__() -- Create Huffman tree from given byte frequencies.
    """

    def __init__(self, frequencies):
        """
        Create Huffman tree from given byte frequencies.

        First we create heap from all nodes with frequency as priority.
        Then we take two elements from heap with minimal priority and we
        create a node with priority equal to sum of priorities of the two
        elements. The created node has the two elements as its children.
        We do this until there is only one node, which is a root of a tree.
        Args:
        frequencies -- Dictionary mapping bytes -> frequencies.
        """
        heap = [Node(byte, freq) for (byte, freq) in frequencies.items()]
        heapify(heap)
        for _ in range(len(heap) - 1):
            left = heappop(heap)
            right = heappop(heap)
            new_node = Node(b'', left.freq + right.freq)
            new_node.left = left
            new_node.right = right
            heappush(heap, new_node)
        self.root = heap[0]

    def serialize(self):
        """
        Create binary representation of a Huffman tree.

        During traversing the tree we build codes and store them in
        OrderedDict when we reach a leaf.
        Binary representation of a tree is in following form:
        First byte is number of distinct bytes in file minus one.
        It's followed by these bytes and align, to ensure whole
        file length in bits in divisible by 8.
        Last part of the header is a tree structure. We start from
        the tree root and traverse it starting to the left and if we
        reach a leaf we are going back up. Each edge of the tree is
        traversed twice. If we are going down we write 0, if we
        are going up we write 1.

        Returns:
        header - Binary representation of the tree.
        """
        self.bytes_codes = OrderedDict()
        tree_bits = []
        encoding_length = 0

        # Creating tree structure representation.
        def traverse(node, code):
            """
            Traverse the tree and create it's structure representation.

            Args:
            node -- Node in the tree.
            code -- Code created so far
            """
            nonlocal self, tree_bits, encoding_length
            if node.left is None:
                self.bytes_codes[node.byte] = code
                encoding_length += node.freq * len(code)
                tree_bits.append('1')
            else:
                tree_bits.append('0')
                traverse(node.left, code + '0')
                tree_bits.append('0')
                traverse(node.right, code + '1')
                tree_bits.append('1')
        traverse(self.root, '')

        # Creating other pieces of tree representation and joining together.
        # Writing number of bytes - 1, so we can fit 256, 0 bytes won't be compressed.
        header = [bin(len(self.bytes_codes) - 1)[2:].zfill(8)]
        # Writing bytes used in file.
        for byte in self.bytes_codes:
            header.append(bin(byte)[2:].zfill(8))
        # Align, so total number of bits is divisible by 8.
        align_length = (8 - (len(tree_bits) - 1 + encoding_length) % 8) % 8
        align = align_length * '1'
        # We use tree_bits without the last one, because it's redundant.
        header = ''.join(chain(header, align, tree_bits[:-1]))

        return header
