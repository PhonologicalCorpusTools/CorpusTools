# -*- mode: python -*-
import os
import sys

block_cipher = None
pct_path = os.getcwd()
icon_path = os.path.join(pct_path, 'resources', 'favicon32x32.ico')

a = Analysis([os.path.join(pct_path, 'bin', 'pct_qt_debug.py')],
             pathex=[pct_path],
             binaries=None,
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='PCT',
          debug=False,
          strip=False,
          upx=True,
          console=False,
          icon=icon_path)

if sys.platform == 'darwin':
   app = BUNDLE(exe, name='PCT.app', icon=icon_path)