# -*- mode: python -*-
import os
import sys
sys.setrecursionlimit(5000)

block_cipher = None
pct_path = os.getcwd()
icon_path = os.path.join(pct_path, 'resources', 'favicon32x32.ico')
if sys.platform == 'win32':
    icon_path = os.path.join(pct_path, 'resources', '48x48_win.ico')
if sys.platform == 'darwin':
    icon_path = os.path.join(pct_path, 'resources', 'favicon.icns')

a = Analysis([os.path.join(pct_path, 'bin', 'pct_qt_debug.py')],
             pathex=[pct_path],
             binaries=None,
             datas=[('resources', 'resources')],
             hiddenimports=['PyQt5', 'urllib',
                            'scipy.spatial.transform._rotation_groups',
                            'scipy.special.cython_special'],
             hookspath=[],
             runtime_hooks=[],
             excludes=['matplotlib'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='Phonological CorpusTools',
          debug=False,
          strip=False,
          upx=True,
          console=False,
          icon=icon_path)

if sys.platform == 'darwin':
   app = BUNDLE(exe, name='Phonological CorpusTools.app', icon=icon_path)