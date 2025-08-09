"""
Configuração global para pytest - CRYPTOBOT SUPREMO GLOBAL
Garante resolução de paths antes da coleta de testes
"""
import sys
import os
from pathlib import Path

project_root = Path(__file__).parent
src_path = project_root / "src"

paths_to_add = [str(project_root), str(src_path)]
for path in paths_to_add:
    if path not in sys.path:
        sys.path.insert(0, path)

if str(src_path) not in sys.modules:
    sys.path.insert(0, str(src_path))

import pytest
import asyncio

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
