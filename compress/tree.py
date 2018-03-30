"""
Module defines class representing Huffman tree.

Classes:

Node -- Node in Huffman tree.
HuffmanTree -- Huffman tree.
"""


from heapq import heapify, heappop, heappush
from functools import total_ordering
from .bitoperations import int_to_bits
from itertools import chain


@total_ordering
class Node:
    """
    Class representing node in Huffman tree.

    Magic methods:
    __init__() -- Initialize attributes.
    __lt__() -- (Frequency, byte) comparison.
    __eq__() -- (Frequency, byte) comparison.
    __repr__() -- Return 'Node(byte, freq)'.

    Instance attributes:
    byte -- Byte(s) associated with node, for leaf it's one byte, for inner
            node it's left.byte + right.byte.
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
        """(Frequency, byte) comparison."""
        return (self.freq, self.byte) < (other.freq, other.byte)

    def __eq__(self, other):
        """(Frequency, byte) comparison."""
        return (self.freq, self.byte) == (other.freq, other.byte)

    def __repr__(self):
        """Return 'Node(byte, freq)'"""
        return 'Node(' + repr((self.byte, self.freq)) + ')'


class HuffmanTree:
    """
    Class representing Huffman tree.

    Methods:
    serialize() -- Create binary representation of a tree.
    __traverse() -- Traverse the tree, calculate length of encoding and codes.

    Magic methods:
    __init__() -- Create Huffman tree from given byte frequencies.

    Instance attributes:
    leaves_num -- Number of leaves in the tree.
    root -- Root of the tree.
    encoding_length -- Length of file encoding.
    bytes_codes -- Mapping bytes in file on their codes (binary strings).
    header -- Binary representation of tree (bytes + structure).
    Last three attributes are calculated when calling serialize().
    """

    def __init__(self, frequencies):
        """
        Create Huffman tree from given byte frequencies.

        First we create heap from all nodes with frequency as priority.
        Then we take two elements from heap with minimal priority and we
        create a node with priority equal to sum of priorities of the two
        elements. The created node has the two elements as its children.
        We do this until there is only one node, which is a root of a tree.
        To ensure that order of bytes written in file header is always the
        same, we associate with each node concatenated bytes of its
        children.

        Args:
        frequencies -- Mapping bytes -> frequencies.
        """
        heap = [Node(byte, freq) for (byte, freq) in frequencies.items()]
        heapify(heap)
        self.leaves_num = len(heap)
        for _ in range(self.leaves_num - 1):
            left = heappop(heap)
            right = heappop(heap)
            new_node = Node(left.byte + right.byte, left.freq + right.freq)
            new_node.left = left
            new_node.right = right
            heappush(heap, new_node)
        self.root = heap[0]
        self.encoding_length = 0
        self.bytes_codes = {}
        self.header = []

    def __traverse(self, node, code):
        """
        Traverse the tree and create it's structure representation.

        We create tree structure representation in the following way.
        We start from the tree root and write 0, then we recursively
        traverse left subtree and write 1, next we write 0 and traverse
        right subtree and write 1 at the end. In other words, we write 0,
        if we are going down in the tree, and 1 if we are going up.
        In addition during traversing tree we are calculating code for
        each byte and total encoding length.

        Args:
        node -- Node in the tree.
        code -- Code created so far.
        """
        if node.left is None:
            self.bytes_codes[node.byte] = code
            self.header.append(int_to_bits(node.byte, 8))
            self.encoding_length += node.freq * len(code)
        else:
            self.tree_bits.append('0')
            self.__traverse(node.left, code + '0')
            self.tree_bits.extend(('1', '0'))
            self.__traverse(node.right, code + '1')
            self.tree_bits.append('1')

    def serialize(self):
        """
        Create binary representation of a Huffman tree.

        Binary representation of a tree is in following form:
        First byte is number of distinct bytes in file minus one.
        It's followed by these bytes and align, to ensure whole
        file length in bits in divisible by 8. After that is binary
        representation of tree structure.

        Returns:
        header - Binary representation of the tree.
        """
        # Writing number of bytes - 1, so we can fit 256, 0 bytes won't be compressed.
        self.tree_bits = []
        self.header.append(int_to_bits(self.leaves_num - 1, 8))

        # Creating tree structure representation.
        self.__traverse(self.root, '')

        # Align, so total number of bits is divisible by 8.
        align_length = (8 - (len(self.tree_bits) + self.encoding_length) % 8) % 8
        align = align_length * '1'

        # Joining all pieces.
        self.header = ''.join(chain(self.header, (align,), self.tree_bits))
        del self.tree_bits
        return self.header
