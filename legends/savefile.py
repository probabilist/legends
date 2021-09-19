"""Tools for processing the STL save file.

"""

from json import loads
from plistlib import load
from base64 import decodebytes
from getpass import getuser
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

__all__ = ['saveFilePath', 'AESdecrypt', 'decryptSaveFile']

def saveFilePath():
    """Creates and return the complete path of the STL save file.

    Returns:
        str: The complete path of the save file.

    """
    return (
        '/Users/' + getuser() + '/Library/Containers/'
        + 'com.tiltingpoint.startrek/Data/Library/Preferences/'
        + 'com.tiltingpoint.startrek.plist'
    )

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

def decryptSaveFile():
    """Finds the STL save file on the local hard drive, then decrypts
    and parses it into a dictionary.

    Returns:
        dict: The decrypted save file as a dictionary.

    """
    with open(saveFilePath(), 'rb') as f:
        saveFile = load(f)
    saveFile.pop('CloudKitAccountInfoCache', None)
    for i in range(3):
        key = str(i) + ' data'
        if len(saveFile.get(key, '')) == 0:
            saveFile[key] = {}
            continue
        saveFile[key] = loads(AESdecrypt(
            saveFile[key],
            'K1FjcmVkc2Vhc29u',
            'LH75Qxpyf0prVvImu4gqxg=='
        ))
    return saveFile
