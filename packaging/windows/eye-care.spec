from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

project_root = Path(SPECPATH).resolve().parents[1]
backend_root = project_root / "backend"

datas = [
    (str(backend_root / "knowledge"), "knowledge"),
    (str(backend_root / "migrations"), "migrations"),
    (str(backend_root / "static"), "static"),
]
datas += collect_data_files("reportlab")

analysis = Analysis(
    [str(backend_root / "app" / "launcher.py")],
    pathex=[str(backend_root)],
    binaries=[],
    datas=datas,
    hiddenimports=["logging.config", *collect_submodules("app")],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pytest"],
    noarchive=False,
)
pyz = PYZ(analysis.pure)

exe = EXE(
    pyz,
    analysis.scripts,
    [],
    exclude_binaries=True,
    name="EyeCareConsultation",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)

collection = COLLECT(
    exe,
    analysis.binaries,
    analysis.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="EyeCareConsultation",
)
