# -*- mode: python -*-
import os
dir = os.path.dirname(__file__)
a = Analysis(['main.py'],
             pathex=[dir],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='main.exe',
          debug=False,
          strip=None,
          upx=True,
          console=False )
