from heapq import heapify, heappop, heappush
from functools import total_ordering
from itertools import chain
from collections import OrderedDict

@total_ordering
class Node:
    def __init__(self, byte, freq):
        self.byte = byte
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq
    
    def __eq__(self, other):
        return self.freq == other.freq

class HuffmanTree:
    def __init__(self, frequencies):
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
        self.bytes_codes = OrderedDict()
        tree_bits = []
        encoding_length = 0

        # Creating tree structure representation.
        def traverse(node, code):
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
