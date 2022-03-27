# -*- mode: python ; coding: utf-8 -*-

import python_minifier
import os

with open("deverser.py", "r") as f, open("deverser.min.py", "w") as f2:
    f2.write(python_minifier.minify(f.read(), remove_literal_statements=True))
with open("pyimg4.py", "r") as f, open("pyimg4.min.py", "w") as f2:
    f2.write(python_minifier.minify(f.read(), remove_literal_statements=True))

block_cipher = None

a = Analysis(
    ["deverser.min.py", "pyimg4.min.py"],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "setuptools",
        "pytest",
        "IPython",
        "csv",
        "Tkinter",
        "tcl",
        "Tkconstants",
        "pywin.debugger",
        "pywin.debugger.dbgcon",
        "pywin.dialogs",
        "_gtkagg",
        "_tkagg",
        "curses",
        "black",
        "python_minifier",
        "_codecs_cn",
        "_codecs_jp",
        "_codecs_kr",
        "_codecs_tw",
        "_codecs_hk",
        "_datetime",
        "_decimal",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

excluded_files = [
    "cryptography-36.0.2.dist-info/LICENSE",
    "cryptography-36.0.2.dist-info",
    "cryptography-36.0.2.dist-info/INSTALLER",
    "cryptography-36.0.2.dist-info/REQUESTED",
    "cryptography-36.0.2.dist-info/LICENSE.APACHE",
    "cryptography-36.0.2.dist-info/direct_url.json",
    "cryptography-36.0.2.dist-info/LICENSE.PSF",
    "cryptography-36.0.2.dist-info/LICENSE",
    "cryptography-36.0.2.dist-info/RECORD",
    "cryptography-36.0.2.dist-info/top_level.txt",
    "cryptography-36.0.2.dist-info/WHEEL",
    "cryptography-36.0.2.dist-info/METADATA",
    "cryptography-36.0.2.dist-info/LICENSE.BSD",
    "nacl/py.typed",
]

a.binaries = TOC([x for x in a.binaries if x[0] not in excluded_files])
a.datas = TOC([x for x in a.datas if x[0] not in excluded_files])

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="deverser",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False if os.name == 'nt' else True,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)