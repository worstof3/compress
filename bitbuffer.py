"""
Module defines class for writing bits to files.

Classes:

OutBitBuffer -- Class for writing bits to files.

Constants:

default_size -- Default size of a buffer used for writing to files.
"""


# Default size of a buffer.
default_size = 1024 * 1024


class OutBitBuffer:
    """
    Class for writing bits to files.

    Methods:
    flush() -- Writing content of a buffer to file.
    write() -- Writing bits to the buffer.

    Attributes:
    filename -- Path to file to write to.
    pieces -- A list of string bit pieces.
    length -- Sum of lengths of pieces elements.
    buffsize -- When length become greater than this value pieces are joined
                and part of them is written to a file.

    Special methods:
    __init__() -- Initialize class attributes.
    __len__() -- Return length.
    __enter__() -- Open a file for binary writing.
    __exit__() -- Flush remaining bits and close the file.
    """

    def __init__(self, filename, size=default_size):
        """
        Initialize class attributes.

        Args:
        filename -- Path to file to write to.
        size -- Size of a buffer.
        """
        self.filename = filename
        self.pieces = []
        self.length = 0
        # Size in bits, so multiplied by 8.
        self.buffsize = 8 * size

    def __len__(self):
        """Return length of bits in a buffer."""
        return self.length

    def __enter__(self):
        """Open file for binary writing."""
        self.fileobj = open(self.filename, 'wb')
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Flush remaining bits and close the file."""
        if self:
            self.flush()
        self.fileobj.close()

    def flush(self):
        """
        Join all bits pieces and write a part of them to a file.

        An ending piece of bits is cut off, so length of a remainging bits
        is buffsize (that ensures writing whole bytes). When bits are
        flushed before writing to file length of remaining bits may be
        lesser than buffsize, but that's ok, because length will still be
        dividable by 8.
        """
        buff = ''.join(self.pieces)
        # Cutting rest of bits.
        buffbits, rest = buff[:self.buffsize], buff[self.buffsize:]
        buffbytes = int(buffbits, 2).to_bytes(len(buffbits) // 8, 'big')
        self.fileobj.write(buffbytes)

        self.pieces = [rest]
        self.length = len(rest)

    def write(self, bits):
        """
        Write bits to a buffer or a file, if the buffer is full.

        Args:
        bits -- String of bits to be written.
        """
        self.pieces.append(bits)
        self.length += len(bits)
        if len(self) > self.buffsize:
            self.flush()
