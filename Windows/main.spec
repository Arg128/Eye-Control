# -*- mode: python ; coding: utf-8 -*-

import os

a = Analysis(
    ['main.py'],
    pathex=[os.path.abspath(SPECPATH)],
    binaries=[],
    datas=[],
    hiddenimports=['src', 'EyeGesturesLite', 'assets', 
        'pkg_resources.py2_warn', 'dependency_injector.errors', 'six',
        'setuptools._distutils._log', 'setuptools._distutils._modified',
        'setuptools._distutils.compat','setuptools._distutils.compat.numpy',
        'setuptools._distutils.compat.py39','setuptools._distutils.zosccompiler'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
