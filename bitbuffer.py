default_size = 1024 * 1024

class OutBitBuffer:
    def __init__(self, filename, size=default_size):
        self.filename = filename
        self.pieces = []
        self.length = 0
        # Size in bits, so multiplied by 8.
        self.buffsize = 8 * size

    def __len__(self):
        return self.length
        
    def __enter__(self):
        self.fileobj = open(self.filename, 'wb')
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self:
            self.flush()
        self.fileobj.close()

    def flush(self):
        buff = ''.join(self.pieces)
        # Cutting rest of bits.
        buffbits, rest = buff[:self.buffsize], buff[self.buffsize:]
        buffbytes = int(buffbits, 2).to_bytes(len(buffbits) // 8, 'big')
        self.fileobj.write(buffbytes)

        self.pieces = [rest]
        self.length = len(rest)

    def write(self, bits):
        self.pieces.append(bits)
        self.length += len(bits)
        if len(self) > self.buffsize:
            self.flush()
