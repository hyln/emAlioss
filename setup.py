import platform
from cx_Freeze import setup, Executable

if platform.system() == "Windows":
    base = "Win32GUI" 
elif platform.system() == "Linux":
    base = None

executables = [
    Executable(
        "main.py",
        target_name="emalioss.exe",
        copyright="Copyright (C) 2024 emnavi",
        # base="gui",
        base=base,
        # base="Win32GUI",
        icon="./assets/icon.ico",
        
        shortcut_name="Em Alioss",
        shortcut_dir="DesktopFolder",
        # 注意 格式
    )
]
build_exe_options = {
    "excludes": ["tkinter"], 
    "include_msvcr": True,
    "include_files": ["./assets/icon.ico","./assets/icon.svg"], 
}


directory_table = [
    ("ProgramMenuFolder", "TARGETDIR", "."),
    ("MyProgramMenu", "ProgramMenuFolder", "MYPROG~1|My Program"),
]
msi_data = {
    "Directory": directory_table,
    "ProgId": [
        ("Prog.Id", None, None, "This is a description", "IconId", None),
    ],
    "Icon": [
        ("IconId", "./assets/icon.svg"),
    ],
}

bdist_msi_options = {
    "add_to_path": True,
    "upgrade_code": "{12345678-1234-1234-1234-1234567890AB}",  # Optional: GUID for upgrades
    "data": msi_data,
}



setup(
    name="emalioss",
    version="0.1",
    description="轻量资源管理!",
    executables=executables,
    options={
        "build_exe": build_exe_options,
        # "bdist_msi": bdist_msi_options,
    },
)
