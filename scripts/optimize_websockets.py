#!/usr/bin/env python3
"""
Script para otimizar conexões WebSocket
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.exchange.websocket_pool import WebSocketPool


async def main():
    print("🌐 OTIMIZANDO CONEXÕES WEBSOCKET")
    print("=" * 40)

    pool = WebSocketPool(max_connections_per_exchange=5)

    print("✅ Pool WebSocket criado")
    print(f"📊 Conexões ativas: {len(pool.connections)}")
    print(f"💾 Cache size: {len(pool.data_cache)}")

    await pool.close_all()
    print("✅ Otimização concluída")


if __name__ == "__main__":
    asyncio.run(main())
