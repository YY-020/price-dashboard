"""
Streamlit Cloud 入口文件
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
BUILD_DIR = PROJECT_ROOT / "01_Build"

if str(BUILD_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_DIR))

import runpy
runpy.run_path(str(BUILD_DIR / "app.py"), run_name="__main__")
