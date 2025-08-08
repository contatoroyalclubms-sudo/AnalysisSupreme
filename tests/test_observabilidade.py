"""
Testes para sistema de observabilidade
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import json
from datetime import datetime

from src.observabilidade.monitor import Monitor


class TestMonitor:
    """Testes para sistema de monitoramento"""

    @pytest.fixture
    def mock_config(self):
        config = Mock()
        config.get_config_observabilidade.return_value = {
            "prometheus_enabled": True,
            "grafana_enabled": True,
            "log_level": "INFO",
        }
        return config

    @pytest.mark.asyncio
    async def test_inicializacao(self, mock_config):
        """Testa inicialização do monitor"""
        monitor = Monitor(mock_config)
        assert monitor is not None
        assert monitor.config == mock_config

    @pytest.mark.asyncio
    async def test_inicializar(self, mock_config):
        """Testa inicialização do sistema de monitoramento"""
        monitor = Monitor(mock_config)
        await monitor.inicializar()
        assert monitor.inicializado

    @pytest.mark.asyncio
    async def test_registrar_trade(self, mock_config):
        """Testa registro de trade"""
        monitor = Monitor(mock_config)
        await monitor.inicializar()

        trade_data = {
            "id": "trade_123",
            "symbol": "BTC/USDT",
            "side": "buy",
            "amount": 0.01,
            "price": 50000,
            "timestamp": datetime.now(),
            "bot": "arbitragem",
        }

        await monitor.registrar_trade(trade_data)
        assert len(monitor.trades) == 1
        assert monitor.trades[0]["id"] == "trade_123"

    @pytest.mark.asyncio
    async def test_registrar_metrica(self, mock_config):
        """Testa registro de métrica"""
        monitor = Monitor(mock_config)
        await monitor.inicializar()

        await monitor.registrar_metrica("arbitragem", "latencia_ms", 45.5)
        assert "arbitragem" in monitor.metricas
        assert "latencia_ms" in monitor.metricas["arbitragem"]

    @pytest.mark.asyncio
    async def test_gerar_alerta(self, mock_config):
        """Testa geração de alerta"""
        monitor = Monitor(mock_config)
        await monitor.inicializar()

        alerta = {
            "tipo": "latencia_alta",
            "bot": "arbitragem",
            "valor": 150,
            "threshold": 50,
            "severidade": "high",
        }

        await monitor.gerar_alerta(alerta)
        assert len(monitor.alertas) == 1
        assert monitor.alertas[0]["tipo"] == "latencia_alta"

    @pytest.mark.asyncio
    async def test_calcular_metricas_performance(self, mock_config):
        """Testa cálculo de métricas de performance"""
        monitor = Monitor(mock_config)
        await monitor.inicializar()

        trades = [
            {"pnl": 100, "bot": "arbitragem", "timestamp": datetime.now()},
            {"pnl": -50, "bot": "arbitragem", "timestamp": datetime.now()},
            {"pnl": 200, "bot": "grid", "timestamp": datetime.now()},
        ]

        for trade in trades:
            monitor.trades.append(trade)

        metricas = await monitor.calcular_metricas_performance()
        assert "pnl_total" in metricas
        assert "win_rate" in metricas
        assert "total_trades" in metricas
        assert metricas["pnl_total"] == 250
        assert metricas["total_trades"] == 3

    @pytest.mark.asyncio
    async def test_gerar_relatorio_bot(self, mock_config):
        """Testa geração de relatório por bot"""
        monitor = Monitor(mock_config)
        await monitor.inicializar()

        monitor.trades.append(
            {
                "bot": "momentum",
                "pnl": 150,
                "symbol": "BTC/USDT",
                "timestamp": datetime.now(),
            }
        )

        monitor.metricas["momentum"] = {
            "breakout_precisao": [0.65, 0.70, 0.68],
            "stop_eficiencia": [0.80, 0.85, 0.82],
        }

        relatorio = await monitor.gerar_relatorio_bot("momentum")
        assert relatorio is not None
        assert "bot" in relatorio
        assert "metricas" in relatorio
        assert "trades" in relatorio
        assert relatorio["bot"] == "momentum"

    @pytest.mark.asyncio
    async def test_gerar_relatorio_completo(self, mock_config):
        """Testa geração de relatório completo"""
        monitor = Monitor(mock_config)
        await monitor.inicializar()

        monitor.trades.extend(
            [
                {"bot": "arbitragem", "pnl": 100, "timestamp": datetime.now()},
                {"bot": "grid", "pnl": 50, "timestamp": datetime.now()},
                {"bot": "momentum", "pnl": -25, "timestamp": datetime.now()},
            ]
        )

        monitor.alertas.append(
            {
                "tipo": "performance_baixa",
                "bot": "momentum",
                "severidade": "medium",
                "timestamp": datetime.now(),
            }
        )

        relatorio = await monitor.gerar_relatorio_completo()
        assert relatorio is not None
        assert "timestamp" in relatorio
        assert "sistema" in relatorio
        assert "bots" in relatorio
        assert "performance" in relatorio
        assert "alertas_ativos" in relatorio

    @pytest.mark.asyncio
    async def test_verificar_alertas_sistema(self, mock_config):
        """Testa verificação de alertas do sistema"""
        monitor = Monitor(mock_config)
        await monitor.inicializar()

        monitor.metricas["arbitragem"] = {
            "latencia_ms": [150, 160, 155]
        }  # Acima do threshold de 50ms

        await monitor.verificar_alertas_sistema()

        alertas_latencia = [a for a in monitor.alertas if a["tipo"] == "latencia_alta"]
        assert len(alertas_latencia) > 0

    @pytest.mark.asyncio
    async def test_exportar_metricas_prometheus(self, mock_config):
        """Testa exportação de métricas para Prometheus"""
        monitor = Monitor(mock_config)
        await monitor.inicializar()

        monitor.metricas["scalping"] = {
            "throughput_ops": [120, 115, 125],
            "latencia_ms": [25, 30, 28],
        }

        metricas_prometheus = await monitor.exportar_metricas_prometheus()
        assert metricas_prometheus is not None
        assert isinstance(metricas_prometheus, str)
        assert "scalping_throughput_ops" in metricas_prometheus
        assert "scalping_latencia_ms" in metricas_prometheus

    @pytest.mark.asyncio
    async def test_salvar_relatorio_arquivo(self, mock_config):
        """Testa salvamento de relatório em arquivo"""
        monitor = Monitor(mock_config)
        await monitor.inicializar()

        relatorio = {
            "timestamp": datetime.now().isoformat(),
            "sistema": {"status": "ativo"},
            "bots": {"arbitragem": {"trades": 5}},
        }

        with patch("builtins.open", create=True) as mock_open:
            mock_file = Mock()
            mock_open.return_value.__enter__.return_value = mock_file

            await monitor.salvar_relatorio_arquivo(relatorio, "test_relatorio.json")

            mock_open.assert_called_once()
            mock_file.write.assert_called_once()
