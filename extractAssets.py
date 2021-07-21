from os import getcwd
from pathlib import Path
import UnityPy
from shutil import copyfile

def getAssetList():
    """writes an alphabetized list of Star Trek: Legends text assets to
    a file named 'assetList.txt' in the current working directory. The
    text is formatted in a way so that it can be directly copied into
    the 'LegendsData' project inside the Asset Studios C# solution.

    """
    bindataPath = (
        '/Applications/Star Trek.app/Contents/'
        + 'Resources/Data/StreamingAssets/AssetBundles/OSX/OSXRed/bindata'
    )
    env = UnityPy.load(bindataPath)
    assetList = []
    for obj in env.objects:
        if not obj.type == 'TextAsset':
            continue
        data = obj.read()
        assetList.append('convertBytesToJson("' + data.name + '");')
    assetList.sort()
    with open(getcwd() + '/assetList.txt', 'w') as f:
        for line in assetList:
            f.write(line + '\n')

def getAssets():
    """Makes a folder named 'assets' in the current working directory.
    Copies the 'data' folder that is inside the legends package to a new
    folder named 'data-old' in the current working directory. Then
    copies 'bindata' and 'Assembly-CSharp.dll' from the contents of the
    Star Trek app. Using UnityPy, the text assets of the game are
    extracted from 'bindata' and placed in the assets folder. Finally,
    an alphabetized list of these assets is written to a file named
    'assetList.txt' in the current working directory.

    The extracted assets are C# binary serialized bytes files, and must
    be deserialized with the 'decodeAssets' project.

    Raises:
        IOError: If the 'assets' folder exists.

    """
    if Path(getcwd() + '/assets').is_dir():
        raise IOError("a folder named 'assets' already exists")
    Path(getcwd() + '/assets').mkdir()
    Path(getcwd() + '/data-new').mkdir(exist_ok=True)
    copyfile(
        '/Applications/Star Trek.app/Contents/'
        + 'Resources/Data/StreamingAssets/AssetBundles/OSX/OSXRed/bindata',
        getcwd() + '/bindata'
    )
    copyfile(
        '/Applications/Star Trek.app/Contents/'
        + 'Resources/Data/Managed/Assembly-CSharp.dll',
        getcwd() + '/Assembly-CSharp.dll'
    )
    env = UnityPy.load(getcwd() + '/bindata')
    assetList = []
    for obj in env.objects:
        if not obj.type == 'TextAsset':
            continue
        data = obj.read()
        with open(getcwd() + '/assets/' + data.name + '.bytes', 'wb') as f:
            f.write(bytes(data.script))
        assetList.append('convertBytesToJson("' + data.name + '");')
    assetList.sort()
    with open(getcwd() + '/assetList.txt', 'w') as f:
        for line in assetList:
            f.write(line + '\n')

