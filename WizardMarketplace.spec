# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['wizard_primera_vez.py'],
    pathex=[],
    binaries=[],
    datas=[('compartido', 'compartido'), ('config_global.txt', '.')],
    hiddenimports=['selenium', 'webdriver_manager', 'requests', 'pyperclip', 'schedule'],
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
    name='WizardMarketplace',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
