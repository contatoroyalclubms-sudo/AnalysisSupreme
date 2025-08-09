"""
Trade model for AnalysisSupreme trading system
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Trade:
    """Modelo de trade para o sistema de trading"""
    
    id: str
    bot: str
    symbol: str
    side: str  # "buy" or "sell"
    amount: float
    price: float
    timestamp: datetime
    caso_uso: int
    pnl: float = 0.0
    status: str = "aberto"  # "aberto", "fechado", "cancelado"
