# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

add_files=[('myimages.py','module')]

a = Analysis(['AustinPlans.py'],
             pathex=['C:\\LandDev\\'],
             binaries=[],
             datas=[],
             hiddenimports=['tkinter', 'tkinter.filedialog', 'tkinter.messagebox', 'requests', 'bs4', 'urllib', 'PyPDF2', 'img2pdf', 'PyPDF2.PdfFileMerger'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='AustinPlans',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False , icon='Get_Plans_256.ico')
