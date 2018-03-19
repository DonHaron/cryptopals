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
    most_common = 'etaoin shrdlu'
    special_chars = '*\\{}&~()+^!'
    s = str(bytes(b))
    common = sum([1 if c.lower() in most_common else 0 for c in s])
    special = sum([1 if c in special_chars else 0 for c in s])

    return common >= 0.6 * len(b) and special < 0.1 * len(b)



def find_single_xor(in_bytestring):
    for i in range(256):
        b = bytes([a ^ i for a in in_bytestring])
        string = str(b)
        if probably_human_readable(b):
            # print(i, string)
            return i

    raise Exception('no matching byte found')


def xor_with_key(in_bytestring, key):
    return bytes([a ^ b for a, b in zip(in_bytestring, itertools.cycle(key))])


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

    key = bytes(solved)
    solution = xor_with_key(filetext, key)
    print(str(solution))

if __name__ == '__main__':
    break_repeating_key_xor('6.txt')
