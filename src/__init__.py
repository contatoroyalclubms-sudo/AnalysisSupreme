"""
CRYPTOBOT SUPREMO GLOBAL - Package Initialization
Garante imports funcionem em qualquer ambiente
"""

import sys
import os
from pathlib import Path

current_dir = Path(__file__).parent
project_root = current_dir.parent

for path in [str(project_root), str(current_dir)]:
    if path not in sys.path:
        sys.path.insert(0, path)

current_pythonpath = os.environ.get("PYTHONPATH", "")
new_pythonpath = f"{project_root}:{current_dir}:{current_pythonpath}"
os.environ["PYTHONPATH"] = new_pythonpath

__all__ = ["models", "bots", "core", "ia", "exchange", "utils", "observabilidade"]

__version__ = "1.0.0"
__author__ = "AnalysisSupreme Team"
__description__ = "Sistema completo de trading automatizado com 6 bots e IA avançada"
