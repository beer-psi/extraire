# -*- mode: python ; coding: utf-8 -*-
# type: ignore

import python_minifier
import os

for files in ["deverser", "pyimg4"]:
    with open(f"{files}.py", "r") as f, open(f"{files}.min.py", "w") as f2:
        lines = [x for x in f.readlines() if 'from typing import' not in x]
        f2.write(python_minifier.minify('\n'.join(lines), remove_literal_statements=True))


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
        "_codecs_iso2022",
        "_datetime",
        "_decimal",
        "_statistics",
        "_uuid",
        "_multibytecodec",
        "_lzma",
        "_bz2",
        "_heapq",
        "_multiprocessing",
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
    "libintl.8.dylib",
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
