#!/usr/bin/env python3
"""
Script para otimizar configurações de cache
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.core.configuracao import Configuracao
from src.cache.redis_cache import RedisCache


async def main():
    print("🗄️  OTIMIZANDO CONFIGURAÇÕES DE CACHE")
    print("=" * 40)

    config = Configuracao()
    cache = RedisCache(config.get_cache_config() if hasattr(config, "get_cache_config") else {})

    await cache.initialize()

    print("✅ Cache Redis inicializado")
    print(f"📊 Estatísticas: {cache.get_stats()}")

    await cache.clear_expired()
    print("🧹 Cache limpo")

    await cache.close()
    print("✅ Otimização concluída")


if __name__ == "__main__":
    asyncio.run(main())
