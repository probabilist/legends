"""Generic functions needed in the `legends` package.

"""

from datetime import datetime, timedelta, timezone
from base64 import decodebytes
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

__all__ = [
    'AESdecrypt',
    'camelToSpace',
    'collapse',
    'formatDict',
    'objDict',
    'ticksToTimedelta',
    'ticksToDatetime'
]

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

def camelToSpace(camel):
    """Modifies a camel case string to add spaces.

    Args:
        camel (str): The string in camel case.

    Returns:
        str: The string with spaces added.

    """
    space = camel[0]
    for char in camel[1:]:
        if char.isupper():
            space += ' '
        space += char
    return space

def collapse(iterable):
    """Collapses an iterable of immutable objects to a single object. If
    there are no objects in the iterable, returns `None`. If all objects
    in the iterable are the same, returns that common object. Otherwise,
    returns the string, 'Mixed'.

    """
    objSet = set(iterable)
    if len(objSet) == 0:
        return None
    if len(objSet) > 1:
        return 'Mixed'
    return objSet.pop()

def formatDict(D):
    """Formats the given dictionary for display, putting each key-value
    pair on its own line.

    Args:
        D (dict): The dictionary to format.

    Returns:
        str: The formatted string.

    """
    lines = [repr(k) + ': ' + repr(v) for k, v in D.items()]
    display = '{' + lines[0] + ',\n'
    for line in lines[1:-1]:
        display += ' ' + line + ',\n'
    display += ' ' + lines[-1] + '}'
    return display

def objDict(obj):
    """Constructs and returns a dictionary of object attributes.

    Args:
        obj (obj): The object from which to build the dictionary.

    Returns:
        dict: {`str`:`obj`} A dictionary mapping attribute names to
            their values. Omits names that start with '_' and values
            that are callable.

    """
    return {
        k:v for k,v in obj.__dict__.items()
        if k[0] != '_' and not callable(v)
    }

def ticksToDatetime(ticks):
    """Converts a .NET timestamp to a Python `datetime` object. A .NET
    timestamp returns the number of "ticks" since 1/1/0001. There are 10
    "ticks" in a microsecond. (For comparison, a POSIX timestamp returns
    the number of seconds since 1/1/1970.)

    Args:
        ticks (int): A timestamp in the .NET format.

    Returns:
        datetime: The converted timestamp.

    """
    return (
        datetime(1, 1, 1, tzinfo=timezone.utc)
        + timedelta(microseconds=ticks//10)
    )

def ticksToTimedelta(ticks):
    """Converts a duration measured in "ticks" to a Python `timedelta`
    object. There are 10 "ticks" in a microsecond. The .NET framework
    uses ticks to mark time.

    Args:
        ticks (int): The number of tenths of a microsecond.

    Returns:
        timedelta: The converted duration.

    """
    return timedelta(microseconds=ticks//10)
