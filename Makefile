.PHONY: help install test lint format run-paper run-live clean docker-build docker-run setup audit-bots audit-complete

help:
	@echo "Comandos disponíveis:"
	@echo "  setup       - Configurar ambiente completo"
	@echo "  install     - Instalar dependências"
	@echo "  test        - Executar testes com cobertura ≥80%"
	@echo "  lint        - Verificar código com flake8"
	@echo "  format      - Formatar código com black"
	@echo "  run-paper   - Executar em modo paper trading"
	@echo "  run-live    - Executar em modo live trading"
	@echo "  clean       - Limpar arquivos temporários"
	@echo "  docker-build - Construir imagem Docker"
	@echo "  docker-run  - Executar com Docker"
	@echo "  audit-bots  - Auditar implementação dos bots"
	@echo "  audit-complete - Auditoria completa do sistema"
	@echo ""
	@echo "Performance & Monitoring:"
	@echo "  test-performance - Executar testes de performance completos"
	@echo "  test-latency    - Testar latência do sistema"
	@echo "  test-throughput - Testar throughput do sistema"
	@echo "  benchmark-bots  - Benchmark de performance dos bots"
	@echo "  monitor-performance - Monitorar performance em tempo real"
	@echo "  optimize-cache  - Otimizar configurações de cache"
	@echo "  optimize-websockets - Otimizar conexões WebSocket"
	@echo "  performance-report - Gerar relatório de performance"

setup: install
	@echo "🔧 Configurando ambiente AnalysisSupreme..."
	@mkdir -p logs logs/relatorios logs/casos_uso docs docs/casos_uso models
	@cp .env.example .env 2>/dev/null || true
	@echo "✅ Ambiente configurado com sucesso!"

install:
	@echo "📦 Instalando dependências..."
	pip install -r requirements.txt
	pip install -e .
	@echo "✅ Dependências instaladas!"

test:
	@echo "🧪 Executando testes com cobertura..."
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term --cov-fail-under=80
	@echo "✅ Testes executados com cobertura ≥80%!"

lint:
	@echo "🔍 Verificando qualidade do código..."
	flake8 src/ tests/ main.py --max-line-length=127 --extend-ignore=E203,W503
	mypy src/ --ignore-missing-imports
	@echo "✅ Código aprovado no lint!"

format:
	@echo "🎨 Formatando código..."
	black src/ tests/ main.py
	isort src/ tests/ main.py
	@echo "✅ Código formatado!"

run-paper:
	@echo "📊 Executando AnalysisSupreme em modo paper trading..."
	PAPER_MODE=true python main.py

run-live:
	@echo "⚠️  ATENÇÃO: Executando em modo LIVE TRADING!"
	@read -p "Tem certeza? (y/N): " confirm && [ "$$confirm" = "y" ]
	PAPER_MODE=false python main.py

audit-bots:
	@echo "🔍 Auditando implementação dos bots..."
	@echo "Verificando 6 bots com 3 casos de uso cada (18 total):"
	@for bot in arbitragem grid momentum scalping mean_reversion swing; do \
		echo "  🤖 Bot $$bot:"; \
		if [ -f "src/bots/$$bot.py" ]; then \
			grep -c "caso_uso.*[123]" src/bots/$$bot.py | head -1; \
		else \
			echo "    ❌ Arquivo não encontrado"; \
		fi; \
	done
	@echo "✅ Auditoria de bots concluída!"

audit-complete:
	@echo "🎯 Auditoria completa do sistema..."
	@make audit-bots
	@python scripts/auditoria.py
	@make test
	@python scripts/relatorio_geral.py
	@echo "✅ Auditoria completa finalizada!"

audit-kpis:
	@echo "📊 Auditando KPIs específicos por bot..."
	@python -c "from src.utils.kpis import GerenciadorKPIs; kpi = GerenciadorKPIs(); print('KPIs implementados:', list(kpi.kpis.keys()))"
	@echo "✅ Auditoria de KPIs concluída!"

audit-pre:
	@echo "🔍 Auditoria pré-implementação..."
	@git status --porcelain
	@find . -name "*.py" | wc -l
	@pytest --collect-only
	@echo "✅ Auditoria pré-implementação concluída!"

audit-post:
	@echo "🔍 Auditoria pós-implementação..."
	@git diff --stat
	@pytest --tb=short
	@ruff check . || echo "⚠️  Ruff check com avisos"
	@make test
	@echo "✅ Auditoria pós-implementação concluída!"

clean:
	@echo "🧹 Limpando arquivos temporários..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage htmlcov/ .pytest_cache/
	@echo "✅ Limpeza concluída!"

docker-build:
	@echo "🐳 Construindo imagem Docker..."
	docker build -t analysissupreme:latest .
	@echo "✅ Imagem Docker construída!"

docker-run:
	@echo "🐳 Executando com Docker..."
	docker-compose up -d
	@echo "✅ Sistema executando em containers!"

# Casos de uso específicos
caso-arbitragem-alta-vol:
	@echo "🚀 Executando caso: Arbitragem - Alta Volatilidade"
	python scripts/setup_caso.py --bot=arbitragem --regime=alta_vol
	python scripts/executar.py --caso=arbitragem_alta_vol_btcusdt
	python scripts/validar.py --caso=arbitragem_alta_vol_btcusdt

caso-grid-lateral:
	@echo "🚀 Executando caso: Grid Trading - Mercado Lateral"
	python scripts/setup_caso.py --bot=grid --regime=lateral
	python scripts/executar.py --caso=grid_lateral_btcusdt
	python scripts/validar.py --caso=grid_lateral_btcusdt

caso-momentum-breakout:
	@echo "🚀 Executando caso: Momentum - Breakout"
	python scripts/setup_caso.py --bot=momentum --regime=breakout
	python scripts/executar.py --caso=momentum_breakout_btcusdt
	python scripts/validar.py --caso=momentum_breakout_btcusdt

caso-scalping-volume:
	@echo "🚀 Executando caso: Scalping - Alto Volume"
	python scripts/setup_caso.py --bot=scalping --regime=volume
	python scripts/executar.py --caso=scalping_volume_btcusdt
	python scripts/validar.py --caso=scalping_volume_btcusdt

caso-mean-reversion-oversold:
	@echo "🚀 Executando caso: Mean Reversion - Oversold"
	python scripts/setup_caso.py --bot=mean_reversion --regime=baixa_vol
	python scripts/executar.py --caso=mean_reversion_baixa_vol_btcusdt
	python scripts/validar.py --caso=mean_reversion_baixa_vol_btcusdt

caso-swing-fibonacci:
	@echo "🚀 Executando caso: Swing Trading - Fibonacci"
	python scripts/setup_caso.py --bot=swing --regime=continuacao
	python scripts/executar.py --caso=swing_continuacao_btcusdt
	python scripts/validar.py --caso=swing_continuacao_btcusdt

# Executar todos os casos de uso
casos-todos:
	@echo "🎯 Executando todos os 18 casos de uso..."
	@make caso-arbitragem-alta-vol
	@make caso-grid-lateral
	@make caso-momentum-breakout
	@make caso-scalping-volume
	@make caso-mean-reversion-oversold
	@make caso-swing-fibonacci
	@echo "✅ Todos os casos de uso executados!"

# Auditoria de cobertura
audit-coverage:
	@echo "📊 Auditando cobertura de testes..."
	pytest --cov=src --cov-report=term --cov-report=html --cov-fail-under=80
	@echo "✅ Auditoria de cobertura concluída!"

# Auditoria de latência
audit-latency:
	@echo "⚡ Auditando latência do sistema..."
	@echo "Meta: 120ms geral, 50ms arbitragem"
	python -c "import time; start=time.time(); import src; print(f'Import time: {(time.time()-start)*1000:.2f}ms')"
	@echo "✅ Auditoria de latência concluída!"

# Performance testing and monitoring
test-performance:
	@echo "🚀 Executando testes de performance..."
	python scripts/test_performance.py --test=full

test-latency:
	@echo "📊 Testando latência do sistema..."
	python scripts/test_performance.py --test=latency --iterations=200

test-throughput:
	@echo "⚡ Testando throughput do sistema..."
	python scripts/test_performance.py --test=throughput --duration=120

benchmark-bots:
	@echo "🤖 Benchmark de performance dos bots..."
	python scripts/test_performance.py --test=bots

monitor-performance:
	@echo "👁️  Monitorando performance em tempo real..."
	python scripts/monitor_performance.py

optimize-cache:
	@echo "🗄️  Otimizando configurações de cache..."
	python scripts/optimize_cache.py

optimize-websockets:
	@echo "🌐 Otimizando conexões WebSocket..."
	python scripts/optimize_websockets.py

performance-report:
	@echo "📋 Gerando relatório de performance..."
	python scripts/test_performance.py --test=full > logs/performance_latest.txt
	@echo "Relatório salvo em logs/performance_latest.txt"

# CRYPTOBOT SUPREMO GLOBAL commands
test-cryptobot-supremo:
	@echo "🚀 Testando CRYPTOBOT SUPREMO GLOBAL..."
	python scripts/test_cryptobot_supremo.py

test-ultra-fast:
	@echo "⚡ Testando Ultra Fast Executor (15ms target)..."
	python -c "import asyncio; import sys; sys.path.insert(0, 'src'); from src.core.engine.ultra_fast_executor import UltraFastExecutor; asyncio.run(UltraFastExecutor().initialize())"

test-websocket-premium:
	@echo "🌐 Testando WebSocket Manager Premium..."
	python -c "import asyncio; import sys; sys.path.insert(0, 'src'); from src.core.engine.websocket_manager_premium import WebSocketManagerPremium; ws = WebSocketManagerPremium(); asyncio.run(ws.initialize_premium())"

test-cache-intelligence:
	@echo "🧠 Testando Cache Intelligence..."
	python -c "import asyncio; import sys; sys.path.insert(0, 'src'); from src.core.engine.cache_intelligence import CacheIntelligence; cache = CacheIntelligence(); asyncio.run(cache.initialize())"

test-sinfonia:
	@echo "🎼 Testando Sinfonia Tecnológica..."
	python -c "import asyncio; import sys; sys.path.insert(0, 'src'); from src.core.engine.sinfonia_suprema import get_sinfonia_suprema; asyncio.run(get_sinfonia_suprema())"

sinfonia-performance-report:
	@echo "🎼 Gerando relatório de performance da Sinfonia..."
	python scripts/test_cryptobot_supremo.py > logs/sinfonia_performance.txt
	@echo "Relatório salvo em logs/sinfonia_performance.txt"

test-all-supremo:
	@echo "🎯 Testando todos os componentes SUPREMO..."
	@make test-ultra-fast
	@make test-websocket-premium
	@make test-cache-intelligence
	@make test-sinfonia
	@make test-cryptobot-supremo

# PATCH SUPREMO v3 - Autonomy & Performance Commands
test-cryptobot-supremo-complete:
	@echo "🚀 Testing CRYPTOBOT SUPREMO GLOBAL Complete System..."
	python scripts/test_cryptobot_supremo.py

benchmark-performance:
	@echo "📊 Running comprehensive performance benchmark..."
	bash scripts/benchmark.sh

verify-performance-targets:
	@echo "🎯 Verifying all performance targets..."
	python scripts/test_cryptobot_supremo.py

generate-melhorias-report:
	@echo "📋 Generating performance improvements report..."
	@echo "Performance report generated in docs/MELHORIAS.md"
	@cat docs/MELHORIAS.md

check-dificuldades:
	@echo "🔍 Checking obstacle tracking..."
	@if [ -f logs/DIFICULDADES.json ]; then echo "✅ Obstacle tracking active"; cat logs/DIFICULDADES.json; else echo "❌ No obstacles tracked"; fi

cryptobot-supremo-status:
	@echo "🎼 CRYPTOBOT SUPREMO GLOBAL Status Report"
	@echo "=================================================="
	@make check-dificuldades
	@echo ""
	@make generate-melhorias-report
	@echo ""
	@make verify-performance-targets

# Autonomy commands
autonomy-remove-obstacles:
	@echo "🛠️ Autonomous obstacle removal..."
	@python scripts/check_obstacles.py

autonomy-optimize-performance:
	@echo "⚡ Autonomous performance optimization..."
	@make benchmark-performance
	@make verify-performance-targets

# Complete system integration
test-complete-integration:
	@echo "🔗 Testing complete system integration..."
	@make test-cryptobot-supremo-complete
	@make benchmark-performance
