"""
Testes para modelos de dados
"""

import pytest
from datetime import datetime

from src.models.trade import Trade


class TestTrade:
    """Testes para modelo Trade"""

    def test_inicializacao_trade_completo(self):
        """Testa inicialização completa de um trade"""
        timestamp = datetime.now()

        trade = Trade(
            id="trade_123",
            bot="arbitragem",
            symbol="BTC/USDT",
            side="buy",
            amount=0.01,
            price=50000.0,
            timestamp=timestamp,
            caso_uso=1,
            pnl=100.0,
            status="fechado",
        )

        assert trade.id == "trade_123"
        assert trade.bot == "arbitragem"
        assert trade.symbol == "BTC/USDT"
        assert trade.side == "buy"
        assert trade.amount == 0.01
        assert trade.price == 50000.0
        assert trade.timestamp == timestamp
        assert trade.caso_uso == 1
        assert trade.pnl == 100.0
        assert trade.status == "fechado"

    def test_inicializacao_trade_minimo(self):
        """Testa inicialização com campos mínimos"""
        timestamp = datetime.now()

        trade = Trade(
            id="trade_456",
            bot="grid",
            symbol="ETH/USDT",
            side="sell",
            amount=0.1,
            price=3000.0,
            timestamp=timestamp,
            caso_uso=2,
        )

        assert trade.id == "trade_456"
        assert trade.bot == "grid"
        assert trade.symbol == "ETH/USDT"
        assert trade.side == "sell"
        assert trade.amount == 0.1
        assert trade.price == 3000.0
        assert trade.timestamp == timestamp
        assert trade.caso_uso == 2
        assert trade.pnl == 0.0  # Valor padrão
        assert trade.status == "aberto"  # Valor padrão

    def test_trade_buy_positivo(self):
        """Testa trade de compra com PnL positivo"""
        trade = Trade(
            id="buy_win",
            bot="momentum",
            symbol="BTC/USDT",
            side="buy",
            amount=0.005,
            price=48000.0,
            timestamp=datetime.now(),
            caso_uso=1,
            pnl=250.0,
            status="fechado",
        )

        assert trade.side == "buy"
        assert trade.pnl > 0
        assert trade.status == "fechado"

    def test_trade_sell_negativo(self):
        """Testa trade de venda com PnL negativo"""
        trade = Trade(
            id="sell_loss",
            bot="scalping",
            symbol="ETH/USDT",
            side="sell",
            amount=0.2,
            price=2950.0,
            timestamp=datetime.now(),
            caso_uso=3,
            pnl=-75.0,
            status="fechado",
        )

        assert trade.side == "sell"
        assert trade.pnl < 0
        assert trade.status == "fechado"

    def test_trade_diferentes_bots(self):
        """Testa trades de diferentes bots"""
        bots = ["arbitragem", "grid", "momentum", "scalping", "mean_reversion", "swing"]

        for i, bot in enumerate(bots):
            trade = Trade(
                id=f"trade_{bot}_{i}",
                bot=bot,
                symbol="BTC/USDT",
                side="buy" if i % 2 == 0 else "sell",
                amount=0.01,
                price=50000.0 + i * 100,
                timestamp=datetime.now(),
                caso_uso=(i % 3) + 1,
                pnl=float(i * 10 - 25),
                status="fechado",
            )

            assert trade.bot == bot
            assert trade.caso_uso in [1, 2, 3]
            assert isinstance(trade.pnl, float)

    def test_trade_diferentes_casos_uso(self):
        """Testa trades com diferentes casos de uso"""
        for caso_uso in [1, 2, 3]:
            trade = Trade(
                id=f"trade_caso_{caso_uso}",
                bot="arbitragem",
                symbol="BTC/USDT",
                side="buy",
                amount=0.01,
                price=50000.0,
                timestamp=datetime.now(),
                caso_uso=caso_uso,
                pnl=100.0 * caso_uso,
            )

            assert trade.caso_uso == caso_uso
            assert trade.pnl == 100.0 * caso_uso

    def test_trade_diferentes_simbolos(self):
        """Testa trades com diferentes símbolos"""
        simbolos = ["BTC/USDT", "ETH/USDT", "ADA/USDT", "DOT/USDT", "LINK/USDT"]

        for i, symbol in enumerate(simbolos):
            trade = Trade(
                id=f"trade_{symbol.replace('/', '')}",
                bot="grid",
                symbol=symbol,
                side="buy",
                amount=0.01,
                price=1000.0 + i * 500,
                timestamp=datetime.now(),
                caso_uso=1,
                pnl=50.0 + i * 25,
            )

            assert trade.symbol == symbol
            assert "/" in trade.symbol
            assert trade.price > 0

    def test_trade_status_diferentes(self):
        """Testa trades com diferentes status"""
        status_list = ["aberto", "fechado", "cancelado"]

        for i, status in enumerate(status_list):
            trade = Trade(
                id=f"trade_status_{i}",
                bot="swing",
                symbol="BTC/USDT",
                side="buy",
                amount=0.01,
                price=50000.0,
                timestamp=datetime.now(),
                caso_uso=1,
                status=status,
            )

            assert trade.status == status

    def test_trade_valores_extremos(self):
        """Testa trades com valores extremos"""
        trade_pequeno = Trade(
            id="trade_pequeno",
            bot="scalping",
            symbol="BTC/USDT",
            side="buy",
            amount=0.00001,
            price=50000.0,
            timestamp=datetime.now(),
            caso_uso=1,
            pnl=0.01,
        )

        assert trade_pequeno.amount == 0.00001
        assert trade_pequeno.pnl == 0.01

        trade_grande = Trade(
            id="trade_grande",
            bot="swing",
            symbol="BTC/USDT",
            side="sell",
            amount=10.0,
            price=50000.0,
            timestamp=datetime.now(),
            caso_uso=3,
            pnl=5000.0,
        )

        assert trade_grande.amount == 10.0
        assert trade_grande.pnl == 5000.0

    def test_trade_timestamp_precisao(self):
        """Testa precisão do timestamp"""
        timestamp1 = datetime.now()
        timestamp2 = datetime.now()

        trade1 = Trade(
            id="trade_time1",
            bot="momentum",
            symbol="BTC/USDT",
            side="buy",
            amount=0.01,
            price=50000.0,
            timestamp=timestamp1,
            caso_uso=1,
        )

        trade2 = Trade(
            id="trade_time2",
            bot="momentum",
            symbol="BTC/USDT",
            side="sell",
            amount=0.01,
            price=50000.0,
            timestamp=timestamp2,
            caso_uso=1,
        )

        assert trade1.timestamp == timestamp1
        assert trade2.timestamp == timestamp2
        assert trade1.timestamp <= trade2.timestamp
