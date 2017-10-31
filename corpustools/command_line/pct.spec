# -*- mode: python -*-

block_cipher = None


a = Analysis(['pct.py'],
             pathex=['C:\\Users\\Scott\\Documents\\GitHub\\CorpusTools\\corpustools\\command_line'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['ttk', 'tkinter', 'matplotlib'],
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
          icon='favicon.ico',
          console=False )
