# -*- mode: python ; coding: utf-8 -*-

from sys import platform

block_cipher = None

icon = 'command.icns' if platform == 'darwin' else 'command.ico'

a = Analysis(
    ['stlplannerapp.py'],
    binaries=[],
    datas=[('legends/data', 'legends/data'), ('legends/help.txt', 'legends')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,  
    [],
    name='STL Planner',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon
)

app = BUNDLE(
    exe,
    name='STL Planner.app',
    icon=icon,
    bundle_identifier=None,
    version='0.26.2'
)
