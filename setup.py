import platform
from cx_Freeze import setup, Executable
import os
from setuptools import setup as setup_linux
from setuptools import find_packages

# 从环境变量中读取版本号
def get_version():
    return os.getenv('PACKAGE_VERSION', "0.1.0")  # 默认版本号为 0.0.1
# 从 requirements.txt 读取依赖
def parse_requirements(filename):
    with open(filename) as f:
        return f.read().splitlines()

base = None
app_name = 'emalioss'
if platform.system() == 'Win32': 
    base = 'Win32GUI'
    app_name = 'emalioss.exe'


executables = [
    Executable(
        "main.py",
        target_name=app_name,
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

if platform.system() == 'Win32': 
    print("win")
    setup(
        name="emalioss",
        version=get_version(),
        description="轻量资源管理!",
        executables=executables,
        options={
            "build_exe": build_exe_options,
            # "bdist_msi": bdist_msi_options,
        },
    )
else:
    print("linux")
    setup_linux(
        name="emalioss",
        version=get_version(),
        description="轻量资源管理!",
        author='hyaline',
        author_email='hhhyaline_hao@outlook.com',
        install_requires=parse_requirements('requirements.txt'),
        entry_points={
        'console_scripts': [
            'emalioss=emalioss.main:main',  # 命令名=模块:函数
        ],
        },
        packages=['emalioss'],  # 包含模块
        include_package_data=True,
    )