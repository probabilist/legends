"""Generic utility functions used by the legends package.

"""

from json import load
from csv import DictWriter
from itertools import chain, combinations
from base64 import decodebytes
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

__all__ = [
    'readData', 'writeToCSV', 'fixedSum', 'powerset', 'AESdecrypt',
    'printProgressBar'
]

def readData(fileName, root):
    """Finds a json file in 'legends/data', then parses it and creates a
    dictionary out of it.

    Args:
        fileName (str): The name of the data file (without extension) to
            be read.
        root (str): The full, absolute path of the legends package.

    Returns:
        dict: The file parsed as a dictionary.

    """
    with open(
        root + '/data/' + fileName + '.json'
    ) as f:
        data = load(f)
    return data

def writeToCSV(fields, table, fileName):
    """Writes a table to a CSV file in the current working directory
    with given file name.

    Args:
        fields (iter of immutables): The items to be used in the header
            of the CSV file, ordered from left to right.
        table (iter of dict): The rows of the table, ordered from top to
            bottom. Each row is represented by a dictionary whose keys
            are among the items in `fields`.
        fileName (str): The filename without extension. A '.csv'
            extension is automatically added.

    """
    with open(fileName + '.csv', 'w', newline = '') as f:
        writer = DictWriter(f, fields)
        writer.writeheader()
        writer.writerows(table)

def fixedSum(n, k, s):
    """A generator that iterates through all k-tuples of integers
    between 0 and n - 1, inclusive, whose sum is s. That is, it iterates
    through the set

        {a in {0,...,n-1}^k: a_0 + ... + a_{n-1} = s}.

    Args:
        n (int): The range of the numbers in the yielded k-tuples. More
            specifically, numbers in the yielded tuples are  between 0
            and n - 1, inclusive. Should be a positive integer.
        k (int): The length of the yielded tuples. Should be a positive
            integer.
        s (int): The sum of the yielded tuples. Should be a nonnegative
            integer.

    Yields:
        tuple of int: The next k-tuple that adds up to s.

    Example:
        >>> [a for a in fixedSum(5,2,4)]
        [(0, 4), (1, 3), (2, 2), (3, 1), (4, 0)]

    Raises:
        ValueError: If arguments do not meet requirements described
            above.

    """
    if type(n) != type(0) or n <= 0:
        raise ValueError('range of tuple items must be a positive integer')
    if type(k) != type(0) or k <= 0:
        raise ValueError('length of tuples must be a positive integer')
    if type(s) != type(0) or s < 0:
        raise ValueError('sum of tuples must be a nonnegative integer')
    if k == 1:
        if s >= n:
            return
        else:
            yield (s,)
            return
    for b in range(min(n, s + 1)):
        for L in fixedSum(n, k - 1, s - b):
            yield (b,) + L

def powerset(iterable):
    """powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)
    """
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

def AESdecrypt(cipherText, key, iv):
    """Decrypts the given cipher text, using the provided key and iv.

    Args:
        cipherText (str): The message to be decrypted.
        key (str): The decryption key.
        iv (str): The iv.

    Returns:
        str: The decrypted message.
    """
    keyB = key.encode('ascii')
    ivB = decodebytes(iv.encode('ascii'))
    cipherTextB = decodebytes(cipherText.encode('ascii'))

    cipher = AES.new(keyB, AES.MODE_CBC, ivB)

    return unpad(cipher.decrypt(cipherTextB), AES.block_size).decode('UTF-8')

def printProgressBar(steps, step):
    """Prints a progress bar to the console.

    Args:
        steps (int): The total number of steps in the iteration.
        step (int): The current step in the iteration.

    """
    width = 45
    units = int(width * step / steps)
    percent = int(100 * step / steps)
    print(
        '  Working: |' + chr(9608) * units + '-' * (width - units) + '| '
        + str(percent) + '% ' + str(step) + '/' + str(steps),
        end='\r'
    )
    if step == steps:
        print(' ' * 72, end='\r')