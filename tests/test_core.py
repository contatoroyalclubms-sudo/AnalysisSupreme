"""
Testes para componentes core do sistema
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import asyncio
import logging
from datetime import datetime

from src.core.configuracao import Configuracao
from src.core.gerenciador_bots import GerenciadorBots
from src.exchange.gerenciador_exchange import GerenciadorExchange
from src.utils.logger import configurar_logger
from src.utils.metricas import CalculadorMetricas
from src.utils.kpis import GerenciadorKPIs


class TestConfiguracao:
    """Testes para classe Configuracao"""

    def test_inicializacao(self):
        """Testa inicialização da configuração"""
        config = Configuracao()
        assert config is not None
        assert hasattr(config, "_config")

    def test_get_exchange_config(self):
        """Testa obtenção de configuração de exchange"""
        config = Configuracao()
        exchange_config = config.get_exchange_config("binance")
        assert exchange_config is not None
        assert exchange_config.nome == "binance"

    def test_get_bot_config(self):
        """Testa obtenção de configuração de bot"""
        config = Configuracao()
        bot_config = config.get_bot_config("arbitragem")
        assert bot_config is not None
        assert bot_config.nome == "arbitragem"

    def test_paper_mode_property(self):
        """Testa propriedade paper_mode"""
        config = Configuracao()
        assert isinstance(config.paper_mode, bool)
        assert config.paper_mode == True  # Padrão

    def test_max_concurrent_bots_property(self):
        """Testa propriedade max_concurrent_bots"""
        config = Configuracao()
        assert isinstance(config.max_concurrent_bots, int)
        assert config.max_concurrent_bots == 6  # Padrão

    def test_risk_limit_percent_property(self):
        """Testa propriedade risk_limit_percent"""
        config = Configuracao()
        assert isinstance(config.risk_limit_percent, float)
        assert config.risk_limit_percent == 2.0  # Padrão


class TestGerenciadorBots:
    """Testes para GerenciadorBots"""

    @pytest.fixture
    def mock_config(self):
        config = Mock(spec=Configuracao)
        config.get_bot_config.return_value = Mock(ativo=True, parametros={})
        return config

    @pytest.fixture
    def mock_monitor(self):
        return AsyncMock()

    @pytest.fixture
    def mock_motor_ia(self):
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_inicializacao(self, mock_config, mock_monitor, mock_motor_ia):
        """Testa inicialização do gerenciador"""
        gerenciador = GerenciadorBots(mock_config, mock_monitor, mock_motor_ia)
        assert gerenciador is not None
        assert gerenciador.config == mock_config
        assert gerenciador.monitor == mock_monitor
        assert gerenciador.motor_ia == mock_motor_ia

    @pytest.mark.asyncio
    async def test_inicializar(self, mock_config, mock_monitor, mock_motor_ia):
        """Testa inicialização dos bots"""
        gerenciador = GerenciadorBots(mock_config, mock_monitor, mock_motor_ia)
        await gerenciador.inicializar()
        assert len(gerenciador.bots) > 0
        assert "arbitragem" in gerenciador.bots
        assert "grid" in gerenciador.bots


class TestGerenciadorExchange:
    """Testes para GerenciadorExchange"""

    @pytest.fixture
    def mock_config(self):
        config = Mock(spec=Configuracao)
        config.get_exchange_config.return_value = Mock(api_key="test_key", api_secret="test_secret", sandbox=True)
        return config

    def test_inicializacao(self, mock_config):
        """Testa inicialização do gerenciador de exchange"""
        gerenciador = GerenciadorExchange(mock_config)
        assert gerenciador is not None
        assert gerenciador.config == mock_config

    @pytest.mark.asyncio
    async def test_inicializar_exchange(self, mock_config):
        """Testa inicialização do exchange"""
        mock_config.paper_mode = True
        gerenciador = GerenciadorExchange(mock_config)

        await gerenciador.inicializar()
        assert gerenciador.exchange_principal is not None


class TestConfigurarLogger:
    """Testes para sistema de logging"""

    def test_configurar_logger_default(self):
        """Testa configuração padrão do logger"""
        configurar_logger()
        logger = logging.getLogger()
        assert logger.level == logging.INFO

    def test_configurar_logger_debug(self):
        """Testa configuração do logger em modo debug"""
        configurar_logger("DEBUG")
        logger = logging.getLogger()
        assert logger.level == logging.DEBUG

    def test_configurar_logger_error(self):
        """Testa configuração do logger em modo error"""
        configurar_logger("ERROR")
        logger = logging.getLogger()
        assert logger.level == logging.ERROR

    def test_log_funcionando(self):
        """Testa se logging está funcionando"""
        configurar_logger("INFO")
        logger = logging.getLogger("test")

        logger.info("Teste de log info")
        logger.warning("Teste de log warning")
        logger.error("Teste de log error")
        assert True


class TestCalculadorMetricas:
    """Testes para calculador de métricas"""

    def test_inicializacao(self):
        """Testa inicialização do calculador de métricas"""
        calculador = CalculadorMetricas()
        assert calculador is not None

    def test_metricas_vazias(self):
        """Testa métricas vazias"""
        calculador = CalculadorMetricas()
        metricas = calculador.calcular_metricas_finais([])
        assert metricas["total_trades"] == 0
        assert metricas["win_rate"] == 0.0
        assert metricas["total_pnl"] == 0.0

    def test_calcular_metricas_simples(self):
        """Testa cálculo de métricas simples"""
        from src.models.trade import Trade

        calculador = CalculadorMetricas()

        trades = [
            Trade(
                id="1",
                bot="arbitragem",
                symbol="BTC/USDT",
                side="buy",
                amount=0.01,
                price=50000,
                timestamp=datetime.now(),
                caso_uso=1,
                pnl=100,
            ),
            Trade(
                id="2",
                bot="arbitragem",
                symbol="BTC/USDT",
                side="sell",
                amount=0.01,
                price=49000,
                timestamp=datetime.now(),
                caso_uso=1,
                pnl=-50,
            ),
            Trade(
                id="3",
                bot="arbitragem",
                symbol="BTC/USDT",
                side="buy",
                amount=0.01,
                price=51000,
                timestamp=datetime.now(),
                caso_uso=1,
                pnl=200,
            ),
        ]

        metricas = calculador.calcular_metricas_finais(trades)
        assert metricas["total_trades"] == 3
        assert metricas["winning_trades"] == 2
        assert metricas["losing_trades"] == 1
        assert metricas["total_pnl"] == 250
        assert metricas["win_rate"] == 2 / 3

    def test_calcular_sharpe_ratio(self):
        """Testa cálculo de Sharpe ratio"""
        from src.models.trade import Trade

        calculador = CalculadorMetricas()

        trades = [
            Trade(
                id="1",
                bot="grid",
                symbol="BTC/USDT",
                side="buy",
                amount=0.01,
                price=50000,
                timestamp=datetime.now(),
                caso_uso=1,
                pnl=100,
            ),
            Trade(
                id="2",
                bot="grid",
                symbol="BTC/USDT",
                side="sell",
                amount=0.01,
                price=49000,
                timestamp=datetime.now(),
                caso_uso=1,
                pnl=50,
            ),
        ]

        sharpe = calculador._calcular_sharpe_ratio(trades)
        assert isinstance(sharpe, float)
        assert sharpe >= 0

    def test_calcular_drawdown(self):
        """Testa cálculo de drawdown"""
        from src.models.trade import Trade

        calculador = CalculadorMetricas()

        trades = [
            Trade(
                id="1",
                bot="momentum",
                symbol="BTC/USDT",
                side="buy",
                amount=0.01,
                price=50000,
                timestamp=datetime.now(),
                caso_uso=1,
                pnl=100,
            ),
            Trade(
                id="2",
                bot="momentum",
                symbol="BTC/USDT",
                side="sell",
                amount=0.01,
                price=49000,
                timestamp=datetime.now(),
                caso_uso=1,
                pnl=-150,
            ),
            Trade(
                id="3",
                bot="momentum",
                symbol="BTC/USDT",
                side="buy",
                amount=0.01,
                price=51000,
                timestamp=datetime.now(),
                caso_uso=1,
                pnl=50,
            ),
        ]

        max_dd, max_dd_pct = calculador._calcular_drawdown(trades)
        assert isinstance(max_dd, float)
        assert isinstance(max_dd_pct, float)
        assert max_dd >= 0
        assert max_dd_pct >= 0


class TestGerenciadorKPIs:
    """Testes para gerenciador de KPIs"""

    def test_inicializacao(self):
        """Testa inicialização do gerenciador de KPIs"""
        gerenciador = GerenciadorKPIs()
        assert gerenciador is not None
        assert hasattr(gerenciador, "kpis")

    def test_atualizar_kpi_arbitragem(self):
        """Testa atualização de KPI de arbitragem"""
        gerenciador = GerenciadorKPIs()
        gerenciador.atualizar_kpi_arbitragem(0.35, 98.0)

        relatorio = gerenciador.gerar_relatorio_kpis()
        assert "arbitragem" in relatorio["bots"]
        assert relatorio["bots"]["arbitragem"]["kpis"]["spread_capturado"] == 0.35

    def test_atualizar_kpi_grid(self):
        """Testa atualização de KPI de grid trading"""
        gerenciador = GerenciadorKPIs()
        gerenciador.atualizar_kpi_grid(75.0, 8.5, 120.0)

        relatorio = gerenciador.gerar_relatorio_kpis()
        assert "grid" in relatorio["bots"]
        assert relatorio["bots"]["grid"]["kpis"]["range_eficiencia"] == 75.0

    def test_gerar_relatorio_kpis(self):
        """Testa geração de relatório de KPIs"""
        gerenciador = GerenciadorKPIs()
        gerenciador.atualizar_kpi_momentum(68.0, 25.0, 82.0)

        relatorio = gerenciador.gerar_relatorio_kpis()
        assert "momentum" in relatorio["bots"]
        assert relatorio["bots"]["momentum"]["kpis"]["breakout_precisao"] == 68.0
        assert relatorio["bots"]["momentum"]["kpis"]["stop_eficiencia"] == 82.0

    def test_validar_targets(self):
        """Testa validação de targets de KPIs"""
        gerenciador = GerenciadorKPIs()
        gerenciador.atualizar_kpi_scalping(120.0, 95.0)

        validacao = gerenciador.verificar_targets("scalping")
        assert isinstance(validacao, dict)
        assert "throughput_ok" in validacao

    def test_medicao_latencia_sistema(self):
        """Testa medição de latência do sistema"""
        gerenciador = GerenciadorKPIs()

        medicao_id = gerenciador.iniciar_medicao_latencia("arbitragem", "trade")
        import time

        time.sleep(0.001)  # 1ms
        latencia = gerenciador.finalizar_medicao_latencia(medicao_id)

        gerenciador.atualizar_kpi_arbitragem(0.35, 96.0)
        relatorio = gerenciador.gerar_relatorio_kpis()

        assert latencia > 0
        assert relatorio["bots"]["arbitragem"]["kpis"]["spread_capturado"] == 0.35
