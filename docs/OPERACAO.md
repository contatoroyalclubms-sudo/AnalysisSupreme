# 🎮 MANUAL DE OPERAÇÃO - CRYPTOBOT SUPREMO GLOBAL

## 🎯 Visão Geral

Este manual fornece instruções completas para operação do sistema CRYPTOBOT SUPREMO GLOBAL, incluindo execução de bots, monitoramento e manutenção.

## 🚀 Iniciando o Sistema

### 1. Ativação do Ambiente

```bash
# Navegar para diretório do projeto
cd AnalysisSupreme

# Ativar ambiente virtual
source venv/bin/activate

# Verificar status
make status
```

### 2. Verificações Pré-Operação

```bash
# Verificar configuração
python scripts/verificar_config.py

# Testar conexões com exchanges
python scripts/test_exchanges.py

# Verificar saldo (paper mode)
python scripts/verificar_saldo.py
```

## 🤖 Operação dos Bots

### Modos de Operação

#### 1. Paper Trading (Padrão)
```bash
# Executar paper trading
bash scripts/run_paper.sh

# Monitorar em tempo real
tail -f logs/cryptobot.log
```

#### 2. Backtest Histórico
```bash
# Executar backtest completo
bash scripts/run_backtest.sh

# Backtest específico
python scripts/executar.py --bot=arbitragem --modo=backtest --periodo=30d
```

#### 3. Live Trading (Produção)
```bash
# ⚠️ ATENÇÃO: Usa dinheiro real!
bash scripts/run_live.sh --confirm "EU_SOU_O_SUPREMO"
```

### Execução por Bot

#### Arbitragem
```bash
# Caso 1: Arbitragem simples
python scripts/executar.py --bot=arbitragem --caso=1

# Caso 2: Arbitragem triangular
python scripts/executar.py --bot=arbitragem --caso=2

# Caso 3: Funding rate
python scripts/executar.py --bot=arbitragem --caso=3
```

#### Grid Trading
```bash
# Caso 1: Grid fixo
python scripts/executar.py --bot=grid --caso=1

# Caso 2: Grid dinâmico
python scripts/executar.py --bot=grid --caso=2

# Caso 3: Grid com stop loss
python scripts/executar.py --bot=grid --caso=3
```

#### Momentum
```bash
# Caso 1: Breakout
python scripts/executar.py --bot=momentum --caso=1

# Caso 2: Continuação
python scripts/executar.py --bot=momentum --caso=2

# Caso 3: Volume breakout
python scripts/executar.py --bot=momentum --caso=3
```

#### Scalping
```bash
# Caso 1: Spread scalping
python scripts/executar.py --bot=scalping --caso=1

# Caso 2: Micro movements
python scripts/executar.py --bot=scalping --caso=2

# Caso 3: Order book
python scripts/executar.py --bot=scalping --caso=3
```

#### Mean Reversion
```bash
# Caso 1: RSI simples
python scripts/executar.py --bot=mean_reversion --caso=1

# Caso 2: Bollinger bands
python scripts/executar.py --bot=mean_reversion --caso=2

# Caso 3: RSI divergence
python scripts/executar.py --bot=mean_reversion --caso=3
```

#### Swing Trading
```bash
# Caso 1: Suporte/resistência
python scripts/executar.py --bot=swing --caso=1

# Caso 2: Candlestick patterns
python scripts/executar.py --bot=swing --caso=2

# Caso 3: Fibonacci
python scripts/executar.py --bot=swing --caso=3
```

## 📊 Monitoramento

### 1. Logs em Tempo Real

```bash
# Log principal
tail -f logs/cryptobot.log

# Logs específicos por bot
tail -f logs/arbitragem.log
tail -f logs/grid.log
tail -f logs/momentum.log
tail -f logs/scalping.log
tail -f logs/mean_reversion.log
tail -f logs/swing.log
```

### 2. Métricas de Performance

```bash
# Dashboard de métricas
python scripts/dashboard_metricas.py

# Relatório de performance
python scripts/relatorio_performance.py

# KPIs em tempo real
python scripts/monitor_kpis.py
```

### 3. Status dos Bots

```bash
# Status geral
make status

# Status detalhado
python scripts/status_detalhado.py

# Health check
python scripts/health_check.py
```

## 📈 Relatórios

### 1. Relatório Geral

```bash
# Gerar relatório completo
make relatorio

# Relatório personalizado
python scripts/relatorio_geral.py --periodo=7d --formato=json
```

### 2. Relatórios por Bot

```bash
# Relatório de arbitragem
python scripts/relatorio_bot.py --bot=arbitragem --periodo=24h

# Relatório de performance
python scripts/relatorio_performance.py --bot=grid --detalhado
```

### 3. Relatórios de Risco

```bash
# Análise de risco
python scripts/analise_risco.py

# Drawdown analysis
python scripts/analise_drawdown.py

# Correlação entre bots
python scripts/analise_correlacao.py
```

## ⚙️ Configuração Dinâmica

### 1. Ajustar Parâmetros

```bash
# Editar configuração principal
nano config/config.json

# Configuração específica por bot
nano config/bots/arbitragem.json

# Recarregar configuração (sem restart)
python scripts/reload_config.py
```

### 2. Gerenciar Exchanges

```bash
# Adicionar nova exchange
python scripts/add_exchange.py --exchange=kraken

# Testar conexão
python scripts/test_exchange.py --exchange=binance

# Desabilitar exchange
python scripts/disable_exchange.py --exchange=coinbase
```

### 3. Ajustar Limites de Risco

```bash
# Configurar stop loss global
python scripts/set_global_stop.py --percent=5

# Ajustar tamanho de posição
python scripts/set_position_size.py --bot=scalping --size=0.01

# Configurar correlação máxima
python scripts/set_correlation_limit.py --limit=0.8
```

## 🔧 Manutenção

### 1. Limpeza de Logs

```bash
# Rotacionar logs
bash scripts/rotate_logs.sh

# Limpar logs antigos (>30 dias)
bash scripts/cleanup_old_logs.sh

# Compactar logs
bash scripts/compress_logs.sh
```

### 2. Backup

```bash
# Backup completo
bash scripts/backup_completo.sh

# Backup apenas configurações
bash scripts/backup_configs.sh

# Backup de dados
bash scripts/backup_dados.sh
```

### 3. Otimização

```bash
# Otimizar cache
python scripts/optimize_cache.py

# Otimizar conexões WebSocket
python scripts/optimize_websockets.py

# Benchmark de performance
bash scripts/benchmark.sh
```

## 🚨 Situações de Emergência

### 1. Parada de Emergência

```bash
# Parar todos os bots imediatamente
bash scripts/emergency_stop.sh

# Fechar todas as posições
python scripts/close_all_positions.py --confirm

# Parada específica por bot
python scripts/stop_bot.py --bot=scalping
```

### 2. Rollback

```bash
# Rollback para versão anterior
bash scripts/rollback.sh

# Restaurar configuração
bash scripts/restore_config.sh

# Restaurar dados
bash scripts/restore_backup.sh logs/backups/backup_YYYYMMDD.tar.gz
```

### 3. Recuperação

```bash
# Verificar integridade
python scripts/verify_integrity.py

# Reparar dados corrompidos
python scripts/repair_data.py

# Reinicializar sistema
bash scripts/reinitialize.sh
```

## 📱 Alertas e Notificações

### 1. Configurar Alertas

```bash
# Telegram
export TELEGRAM_BOT_TOKEN=seu_token
export TELEGRAM_CHAT_ID=seu_chat_id

# Discord
export DISCORD_WEBHOOK_URL=sua_webhook_url

# Email
export SMTP_SERVER=smtp.gmail.com
export SMTP_USER=seu_email
export SMTP_PASSWORD=sua_senha
```

### 2. Tipos de Alertas

- **🔴 Crítico**: Falhas de sistema, perdas significativas
- **🟡 Aviso**: Performance degradada, limites atingidos
- **🟢 Info**: Trades executados, relatórios gerados

### 3. Configurar Limites

```bash
# Alerta de perda
python scripts/set_alert.py --tipo=loss --limite=1000 --moeda=USDT

# Alerta de performance
python scripts/set_alert.py --tipo=performance --limite=0.5 --metrica=sharpe

# Alerta de latência
python scripts/set_alert.py --tipo=latency --limite=100 --unidade=ms
```

## 📊 Dashboard Web (Opcional)

### 1. Iniciar Dashboard

```bash
# Iniciar servidor web
python scripts/start_dashboard.py --port=8080

# Acessar: http://localhost:8080
```

### 2. Funcionalidades

- **📈 Gráficos em tempo real**
- **📊 Métricas de performance**
- **🤖 Status dos bots**
- **📋 Logs centralizados**
- **⚙️ Configuração via web**

## 🔍 Troubleshooting

### Problemas Comuns

#### 1. Bot não executa trades
```bash
# Verificar saldo
python scripts/verificar_saldo.py

# Verificar conexão
python scripts/test_exchanges.py

# Verificar configuração
python scripts/validate_config.py
```

#### 2. Alta latência
```bash
# Verificar conexão de rede
ping api.binance.com

# Otimizar WebSockets
python scripts/optimize_websockets.py

# Verificar carga do sistema
top
```

#### 3. Erro de API
```bash
# Verificar chaves API
python scripts/test_api_keys.py

# Verificar rate limits
python scripts/check_rate_limits.py

# Rotacionar chaves
python scripts/rotate_api_keys.py
```

## 📋 Checklist Operacional Diário

### Manhã
- [ ] Verificar status dos bots
- [ ] Revisar relatório noturno
- [ ] Verificar saldos
- [ ] Analisar performance

### Durante o Dia
- [ ] Monitorar alertas
- [ ] Verificar métricas
- [ ] Ajustar parâmetros se necessário
- [ ] Backup incremental

### Noite
- [ ] Gerar relatório diário
- [ ] Backup completo
- [ ] Limpeza de logs
- [ ] Planejamento do dia seguinte

## 📞 Suporte

### Logs de Debug
```bash
# Ativar debug
export LOG_LEVEL=DEBUG

# Gerar relatório de debug
python scripts/debug_report.py

# Verificar saúde do sistema
python scripts/system_health.py
```

### Contato
- **Documentação**: `docs/`
- **Logs**: `logs/DIFICULDADES.json`
- **Status**: `logs/status_sistema.json`

---

**🎯 Operação Eficiente = Lucros Consistentes**

Próximo: [Procedimentos de Backup](BACKUP.md)
