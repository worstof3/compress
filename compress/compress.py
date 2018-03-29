from .comp import compress, EmptyFile
from .decomp import decompress
from argparse import ArgumentParser, SUPPRESS


def main():
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

    try:
        with open(args.infile, 'rb') as infile,\
             open(args.outfile, 'wb') as outfile:
            args.operation(infile, outfile)
    except EmptyFile as error:
        print('Error:', error)
    except FileNotFoundError as error:
        print('Error:', error)


if __name__ == '__main__':
    main()