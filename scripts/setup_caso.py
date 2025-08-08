#!/usr/bin/env python3
"""
Script para configurar casos de uso específicos dos bots
"""

import argparse
import json
import sys
from pathlib import Path


def setup_caso_uso(bot: str, regime: str, par: str = "BTC/USDT"):
    """Configura caso de uso específico"""
    print(f"🔧 Configurando caso de uso: {bot} - {regime} - {par}")

    regime_mapping = {
        "alta_vol": 1,
        "baixa_vol": 2,
        "lateral": 3,
        "breakout": 1,
        "continuacao": 2,
        "volume": 3,
    }

    caso_uso = regime_mapping.get(regime, 1)

    config_path = Path("config/config.json")
    if not config_path.exists():
        config_path = Path("config/config.example.json")

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    if bot not in config.get("bots", {}):
        print(f"❌ Bot {bot} não encontrado")
        return False

    bot_config = config["bots"][bot]
    caso_config = bot_config["casos_uso"].get(str(caso_uso), {})

    print(f"✅ Bot: {bot}")
    print(f"✅ Regime: {regime} (caso de uso {caso_uso})")
    print(f"✅ Par: {par}")
    print(f"✅ Tipo: {caso_config.get('tipo', 'N/A')}")

    caso_especifico = {
        "bot": bot,
        "regime": regime,
        "par": par,
        "caso_uso": caso_uso,
        "configuracao": caso_config,
        "parametros": bot_config.get("parametros", {}),
        "paper_mode": True,
        "objetivo": f"Executar {bot} em regime {regime} para {par}",
        "ambiente": "paper",
        "latencia_alvo": "120ms" if bot != "arbitragem" else "50ms",
    }

    casos_dir = Path("logs/casos_uso")
    casos_dir.mkdir(parents=True, exist_ok=True)

    caso_file = casos_dir / f"{bot}_{regime}_{par.replace('/', '')}.json"
    with open(caso_file, "w", encoding="utf-8") as f:
        json.dump(caso_especifico, f, indent=2, ensure_ascii=False)

    print(f"✅ Configuração salva: {caso_file}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Configurar caso de uso específico")
    parser.add_argument(
        "--bot",
        required=True,
        choices=[
            "arbitragem",
            "grid",
            "momentum",
            "scalping",
            "mean_reversion",
            "swing",
        ],
    )
    parser.add_argument(
        "--regime",
        required=True,
        choices=[
            "alta_vol",
            "baixa_vol",
            "lateral",
            "breakout",
            "continuacao",
            "volume",
        ],
    )
    parser.add_argument(
        "--par", default="BTC/USDT", help="Par de trading (default: BTC/USDT)"
    )

    args = parser.parse_args()

    if setup_caso_uso(args.bot, args.regime, args.par):
        print("🎯 Setup do caso de uso concluído com sucesso!")
    else:
        print("❌ Erro no setup do caso de uso")
        sys.exit(1)


if __name__ == "__main__":
    main()
