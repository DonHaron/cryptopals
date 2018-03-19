import codecs
import base64
import itertools
from functools import reduce


def hex_to_base64(hex):
    str = codecs.decode(hex, 'hex')
    return base64.b64encode(str)


def fixed_xor(input1, input2):
    a = codecs.decode(input1, 'hex')
    b = codecs.decode(input2, 'hex')
    c = bytes([x ^ y for x, y in zip(a, b)])
    return codecs.encode(c, 'hex')

def probably_human_readable(b):
    # ascii codes
    numbers = range(48, 58)
    lowercase = range(97, 123)
    uppercase = range(65, 91)
    space = [32]
    #s = str(b)
    #print(bytes(b)[0])
    common = sum([1 if i in numbers or i in lowercase or i in uppercase or i in space else 0 for i in b])
    #vowels = sum([1 if x.lower() in 'aeiou' else 0 for x in s])
    #whitespaces = sum([1 if x == ' ' else 0 for x in s])
    #slashes = sum([1 if x == '\\' else 0 for x in s])
    #
    return common >= len(b) * 0.7



def find_single_xor(in_bytestring):
    for i in range(256):
        b = bytes([a ^ i for a in in_bytestring])
        string = str(b)
        if probably_human_readable(b):
            print(i, string)
            return i

    raise Exception('no matching byte found')


def xor_with_key(in_string, key):
    encrypted = bytes([a ^ b for a, b in zip(in_string.encode(), itertools.cycle(key.encode()))])
    return codecs.encode(encrypted, 'hex')


def hamming_distance(a, b):
    return sum(bin(x ^ y).count('1') for x, y in zip(a, b))

def break_repeating_key_xor(infile):
    with open(infile) as f:
        filetext = base64.b64decode(f.read())

    lengths_and_distances = []
    for keysize in range(2, 40):
        parts = []
        for i in range(4):
            parts.append(filetext[i * keysize:(i + 1) * keysize])

        distances = []
        for a, b in itertools.combinations(parts, 2):
            distances.append(hamming_distance(a, b) / keysize)

        lengths_and_distances.append((keysize, reduce(lambda x, y: x + y, distances) / len(distances)))

    probable_keysize, distance = min(lengths_and_distances, key=lambda x: x[1])
    blocks = [filetext[i:i + probable_keysize + 1] for i in range(0, len(filetext), probable_keysize)]
    transposed = [[] for _ in range(0, probable_keysize)]
    for block in blocks:
        #print(block)
        for i in range(0, probable_keysize):
            if len(block) > i:
                transposed[i].append(block[i])

    transposed_bytes = [bytes(t) for t in transposed]

    #import pprint; pprint.pprint(transposed_bytes)

    solved = [find_single_xor(b) for b in transposed_bytes]

    print(str(solved))

if __name__ == '__main__':
    break_repeating_key_xor('6.txt')
