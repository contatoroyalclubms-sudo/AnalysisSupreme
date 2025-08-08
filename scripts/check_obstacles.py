#!/usr/bin/env python3
"""
Script para verificar obstáculos no sistema CRYPTOBOT SUPREMO GLOBAL
"""

import json
import os
from pathlib import Path

def check_obstacles():
    """Verifica obstáculos registrados no sistema"""
    obstacles_file = Path("logs/DIFICULDADES.json")
    
    if obstacles_file.exists():
        with open(obstacles_file, 'r') as f:
            obstacles = json.load(f)
        
        print(f"Found {len(obstacles)} obstacles tracked")
        
        for obstacle in obstacles[-3:]:  # Last 3 obstacles
            print(f"- {obstacle['timestamp']}: {obstacle['etapa']} - {obstacle['resultado']}")
    else:
        print("No obstacles tracked")

if __name__ == "__main__":
    check_obstacles()
