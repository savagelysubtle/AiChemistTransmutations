# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for AiChemist Transmutation Codex

This spec file builds a standalone executable that includes:
- Python runtime
- All dependencies
- Bundled Tesseract OCR
- Configuration files

Usage:
    pyinstaller transmutation_codex.spec --clean
"""

from PyInstaller.utils.hooks import collect_data_files, collect_submodules
import sys
from pathlib import Path

block_cipher = None

# Collect all data files from important packages
datas = []

# Bundle Tesseract (copied by build script)
datas += [
    ('build/resources/tesseract', 'resources/tesseract'),
]

# Bundle Ghostscript (copied by build script)
datas += [
    ('build/resources/ghostscript', 'resources/ghostscript'),
]

# Bundle Pandoc (copied by build script)
datas += [
    ('build/resources/pandoc', 'resources/pandoc'),
]

# Bundle configuration
datas += [
    ('config/default_config.yaml', 'config'),
]

# Bundle any additional resources
# datas += [
#     ('gui/dist', 'gui/dist'),  # If bundling Electron GUI
# ]

# Collect hidden imports (modules not automatically detected)
hiddenimports = [
    'transmutation_codex.plugins.markdown.to_pdf',
    'transmutation_codex.plugins.pdf.to_markdown',
    'transmutation_codex.plugins.pdf.to_html',
    'transmutation_codex.plugins.pdf.to_editable_pdf',
    'transmutation_codex.plugins.txt.to_pdf',
    'transmutation_codex.plugins.html.to_pdf',
    'ocrmypdf',
    'fitz',  # PyMuPDF
    'pdfminer',
    'markdown_pdf',
    'reportlab',
]

# Binary dependencies (DLLs, .so files)
binaries = []

a = Analysis(
    ['src/transmutation_codex/adapters/cli/main.py'],  # Entry point
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['scripts/runtime_hook_paths.py'],  # Auto-configure PATH for bundled executables
    excludes=[
        'tkinter',  # Exclude unused GUI frameworks
        'matplotlib',
        'IPython',
        'jupyter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='aichemist_transmutation_codex',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Set to False for GUI-only application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here: 'resources/icon.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='aichemist_transmutation_codex',
)

# For building a single-file executable (larger, slower startup):
# exe = EXE(
#     pyz,
#     a.scripts,
#     a.binaries,
#     a.zipfiles,
#     a.datas,
#     [],
#     name='aichemist_transmutation_codex',
#     debug=False,
#     bootloader_ignore_signals=False,
#     strip=False,
#     upx=True,
#     upx_exclude=[],
#     runtime_tmpdir=None,
#     console=True,
#     disable_windowed_traceback=False,
#     argv_emulation=False,
#     target_arch=None,
#     codesign_identity=None,
#     entitlements_file=None,
#     icon=None,
# )

