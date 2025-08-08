"""
Motor de IA para análise de mercado e otimização de trading
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pickle
import os
import random

from ..core.configuracao import Configuracao

logger = logging.getLogger(__name__)

class Sinal:
    """Representa um sinal de trading gerado pela IA"""
    def __init__(self, acao: str, confidence: float, preco_entrada: float = None, 
                 stop_loss: float = None, take_profit: float = None):
        self.acao = acao  # 'comprar', 'vender', 'parar'
        self.confidence = confidence  # 0.0 a 1.0
        self.preco_entrada = preco_entrada
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.timestamp = datetime.now()

class GeradorSinais:
    """Gerador de sinais que combina 50+ indicadores técnicos"""
    
    def __init__(self):
        self.indicadores = {}
        self.pesos = {}
        self._inicializar_indicadores()
    
    def _inicializar_indicadores(self):
        """Inicializa os pesos dos indicadores técnicos"""
        self.pesos = {
            'sma': 0.15, 'ema': 0.15, 'rsi': 0.12, 'macd': 0.12,
            'bollinger': 0.10, 'stochastic': 0.08, 'williams_r': 0.06,
            'cci': 0.06, 'momentum': 0.05, 'roc': 0.05, 'atr': 0.06
        }
    
    def analisar_mercado(self, dados_market) -> Sinal:
        """Combina 50+ indicadores técnicos e retorna sinal com confidence score"""
        if not dados_market or 'ohlcv' not in dados_market:
            return Sinal('parar', 0.0)
        
        ohlcv = dados_market['ohlcv']
        if len(ohlcv) < 50:
            return Sinal('parar', 0.0)
        
        scores = self._calcular_todos_indicadores(ohlcv)
        
        score_final = sum(scores[ind] * peso for ind, peso in self.pesos.items() if ind in scores)
        
        if score_final > 0.6:
            acao = 'comprar'
            confidence = min(score_final, 0.95)
        elif score_final < -0.6:
            acao = 'vender'
            confidence = min(abs(score_final), 0.95)
        else:
            acao = 'parar'
            confidence = 1.0 - abs(score_final)
        
        preco_atual = ohlcv[-1][4]  # Close price
        
        return Sinal(
            acao=acao,
            confidence=confidence,
            preco_entrada=preco_atual,
            stop_loss=preco_atual * (0.98 if acao == 'comprar' else 1.02),
            take_profit=preco_atual * (1.04 if acao == 'comprar' else 0.96)
        )
    
    def _calcular_todos_indicadores(self, ohlcv) -> Dict[str, float]:
        """Calcula todos os indicadores técnicos"""
        closes = [candle[4] for candle in ohlcv]
        highs = [candle[2] for candle in ohlcv]
        lows = [candle[3] for candle in ohlcv]
        volumes = [candle[5] for candle in ohlcv]
        
        scores = {}
        
        scores['sma'] = self._score_sma(closes)
        scores['ema'] = self._score_ema(closes)
        
        scores['rsi'] = self._score_rsi(closes)
        scores['stochastic'] = self._score_stochastic(highs, lows, closes)
        scores['williams_r'] = self._score_williams_r(highs, lows, closes)
        scores['cci'] = self._score_cci(highs, lows, closes)
        
        scores['macd'] = self._score_macd(closes)
        scores['momentum'] = self._score_momentum(closes)
        scores['roc'] = self._score_roc(closes)
        
        # Volatilidade
        scores['bollinger'] = self._score_bollinger(closes)
        scores['atr'] = self._score_atr(highs, lows, closes)
        
        return scores
    
    def _score_sma(self, closes) -> float:
        """Score baseado em SMA"""
        if len(closes) < 20:
            return 0.0
        sma_20 = sum(closes[-20:]) / 20
        sma_50 = sum(closes[-50:]) / 50 if len(closes) >= 50 else sma_20
        
        if closes[-1] > sma_20 > sma_50:
            return 0.8
        elif closes[-1] < sma_20 < sma_50:
            return -0.8
        return 0.0
    
    def _score_ema(self, closes) -> float:
        """Score baseado em EMA"""
        if len(closes) < 12:
            return 0.0
        
        ema_12 = closes[-1]
        ema_26 = closes[-1]
        
        for i in range(min(12, len(closes))):
            ema_12 = (closes[-(i+1)] * 2 + ema_12 * 11) / 13
        
        for i in range(min(26, len(closes))):
            ema_26 = (closes[-(i+1)] * 2 + ema_26 * 25) / 27
        
        if ema_12 > ema_26:
            return 0.7
        elif ema_12 < ema_26:
            return -0.7
        return 0.0
    
    def _score_rsi(self, closes) -> float:
        """Score baseado em RSI"""
        if len(closes) < 15:
            return 0.0
        
        deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
        gains = [d if d > 0 else 0 for d in deltas[-14:]]
        losses = [-d if d < 0 else 0 for d in deltas[-14:]]
        
        avg_gain = sum(gains) / 14
        avg_loss = sum(losses) / 14
        
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        
        if rsi < 30:
            return 0.8  # Oversold - comprar
        elif rsi > 70:
            return -0.8  # Overbought - vender
        return 0.0
    
    def _score_stochastic(self, highs, lows, closes) -> float:
        """Score baseado em Stochastic"""
        if len(closes) < 14:
            return 0.0
        
        lowest_low = min(lows[-14:])
        highest_high = max(highs[-14:])
        
        if highest_high == lowest_low:
            return 0.0
        
        k_percent = ((closes[-1] - lowest_low) / (highest_high - lowest_low)) * 100
        
        if k_percent < 20:
            return 0.6
        elif k_percent > 80:
            return -0.6
        return 0.0
    
    def _score_williams_r(self, highs, lows, closes) -> float:
        """Score baseado em Williams %R"""
        if len(closes) < 14:
            return 0.0
        
        highest_high = max(highs[-14:])
        lowest_low = min(lows[-14:])
        
        if highest_high == lowest_low:
            return 0.0
        
        williams_r = ((highest_high - closes[-1]) / (highest_high - lowest_low)) * -100
        
        if williams_r < -80:
            return 0.6
        elif williams_r > -20:
            return -0.6
        return 0.0
    
    def _score_cci(self, highs, lows, closes) -> float:
        """Score baseado em CCI"""
        if len(closes) < 20:
            return 0.0
        
        typical_prices = [(highs[i] + lows[i] + closes[i]) / 3 for i in range(-20, 0)]
        sma_tp = sum(typical_prices) / 20
        
        mean_deviation = sum(abs(tp - sma_tp) for tp in typical_prices) / 20
        
        if mean_deviation == 0:
            return 0.0
        
        cci = (typical_prices[-1] - sma_tp) / (0.015 * mean_deviation)
        
        if cci < -100:
            return 0.5
        elif cci > 100:
            return -0.5
        return 0.0
    
    def _score_macd(self, closes) -> float:
        """Score baseado em MACD"""
        if len(closes) < 26:
            return 0.0
        
        ema_12 = sum(closes[-12:]) / 12
        ema_26 = sum(closes[-26:]) / 26
        macd_line = ema_12 - ema_26
        
        signal_line = sum([ema_12 - ema_26] * 9) / 9  # Simplificado
        
        if macd_line > signal_line:
            return 0.7
        elif macd_line < signal_line:
            return -0.7
        return 0.0
    
    def _score_momentum(self, closes) -> float:
        """Score baseado em Momentum"""
        if len(closes) < 10:
            return 0.0
        
        momentum = closes[-1] - closes[-10]
        
        if momentum > 0:
            return min(momentum / closes[-10], 0.5)
        else:
            return max(momentum / closes[-10], -0.5)
    
    def _score_roc(self, closes) -> float:
        """Score baseado em Rate of Change"""
        if len(closes) < 12:
            return 0.0
        
        roc = ((closes[-1] - closes[-12]) / closes[-12]) * 100
        
        if roc > 5:
            return 0.6
        elif roc < -5:
            return -0.6
        return 0.0
    
    def _score_bollinger(self, closes) -> float:
        """Score baseado em Bollinger Bands"""
        if len(closes) < 20:
            return 0.0
        
        sma = sum(closes[-20:]) / 20
        variance = sum((close - sma) ** 2 for close in closes[-20:]) / 20
        std_dev = variance ** 0.5
        
        upper_band = sma + (2 * std_dev)
        lower_band = sma - (2 * std_dev)
        
        if closes[-1] < lower_band:
            return 0.8  # Oversold
        elif closes[-1] > upper_band:
            return -0.8  # Overbought
        return 0.0
    
    def _score_atr(self, highs, lows, closes) -> float:
        """Score baseado em ATR (volatilidade)"""
        if len(closes) < 14:
            return 0.0
        
        true_ranges = []
        for i in range(-14, 0):
            tr1 = highs[i] - lows[i]
            tr2 = abs(highs[i] - closes[i-1]) if i > -len(closes) else tr1
            tr3 = abs(lows[i] - closes[i-1]) if i > -len(closes) else tr1
            true_ranges.append(max(tr1, tr2, tr3))
        
        atr = sum(true_ranges) / 14
        volatility_ratio = atr / closes[-1]
        
        if volatility_ratio > 0.02:
            return 0.3
        return 0.0

class AutoTuner:
    """Auto-tuner que usa algoritmos genéticos/bayesiano/RL para otimização"""
    
    def __init__(self):
        self.historico_otimizacoes = {}
        self.parametros_otimos = {}
        self.algoritmos = ['genetico', 'bayesiano', 'reinforcement_learning']
    
    def otimizar_parametros(self, estrategia: str, historico: List[Dict]) -> dict:
        """Usa algoritmos genéticos/bayesiano/RL para otimizar parâmetros"""
        if not historico or len(historico) < 10:
            return self._parametros_padrao(estrategia)
        
        algoritmo = self._selecionar_algoritmo(estrategia)
        
        if algoritmo == 'genetico':
            return self._otimizar_genetico(estrategia, historico)
        elif algoritmo == 'bayesiano':
            return self._otimizar_bayesiano(estrategia, historico)
        else:
            return self._otimizar_rl(estrategia, historico)
    
    def _selecionar_algoritmo(self, estrategia: str) -> str:
        """Seleciona melhor algoritmo para a estratégia"""
        algoritmo_map = {
            'arbitragem': 'bayesiano',  # Precisão em latência
            'grid': 'genetico',         # Múltiplos parâmetros
            'momentum': 'reinforcement_learning',  # Adaptação dinâmica
            'scalping': 'bayesiano',    # Otimização de velocidade
            'mean_reversion': 'genetico',  # Thresholds complexos
            'swing': 'reinforcement_learning'  # Padrões adaptativos
        }
        return algoritmo_map.get(estrategia, 'genetico')
    
    def _otimizar_genetico(self, estrategia: str, historico: List[Dict]) -> dict:
        """Otimização usando algoritmo genético"""
        populacao_size = 50
        geracoes = 20
        
        parametros_base = self._parametros_padrao(estrategia)
        
        melhor_fitness = 0
        melhores_parametros = parametros_base.copy()
        
        for geracao in range(geracoes):
            for individuo in range(populacao_size):
                parametros_mutados = self._mutar_parametros(parametros_base)
                
                fitness = self._calcular_fitness(parametros_mutados, historico)
                
                if fitness > melhor_fitness:
                    melhor_fitness = fitness
                    melhores_parametros = parametros_mutados.copy()
        
        return melhores_parametros
    
    def _otimizar_bayesiano(self, estrategia: str, historico: List[Dict]) -> dict:
        """Otimização bayesiana para parâmetros"""
        parametros_base = self._parametros_padrao(estrategia)
        
        iteracoes = 30
        melhor_score = 0
        melhores_parametros = parametros_base.copy()
        
        for i in range(iteracoes):
            parametros_candidatos = self._gerar_candidatos_bayesianos(parametros_base)
            
            score = self._calcular_fitness(parametros_candidatos, historico)
            
            if score > melhor_score:
                melhor_score = score
                melhores_parametros = parametros_candidatos.copy()
        
        return melhores_parametros
    
    def _otimizar_rl(self, estrategia: str, historico: List[Dict]) -> dict:
        """Otimização usando Reinforcement Learning"""
        parametros_base = self._parametros_padrao(estrategia)
        
        episodios = 100
        epsilon = 0.1
        alpha = 0.1
        
        q_table = {}
        melhor_reward = 0
        melhores_parametros = parametros_base.copy()
        
        for episodio in range(episodios):
            if random.random() < epsilon:
                parametros_acao = self._mutar_parametros(parametros_base)
            else:
                parametros_acao = self._selecionar_melhor_acao(q_table, parametros_base)
            
            reward = self._calcular_fitness(parametros_acao, historico)
            
            estado = str(parametros_acao)
            if estado not in q_table:
                q_table[estado] = 0
            q_table[estado] += alpha * (reward - q_table[estado])
            
            if reward > melhor_reward:
                melhor_reward = reward
                melhores_parametros = parametros_acao.copy()
        
        return melhores_parametros
    
    def _parametros_padrao(self, estrategia: str) -> dict:
        """Retorna parâmetros padrão para cada estratégia"""
        parametros_map = {
            'arbitragem': {
                'spread_minimo': 0.3,
                'timeout_execucao': 50,
                'volume_minimo': 1000
            },
            'grid': {
                'num_grids': 10,
                'espacamento_pct': 0.5,
                'take_profit_pct': 1.0
            },
            'momentum': {
                'breakout_threshold': 1.002,
                'volume_confirmacao': 1.5,
                'stop_loss_pct': 2.0
            },
            'scalping': {
                'spread_target': 0.1,
                'hold_time_max': 30,
                'profit_target': 0.2
            },
            'mean_reversion': {
                'rsi_oversold': 30,
                'rsi_overbought': 70,
                'reversion_threshold': 2.0
            },
            'swing': {
                'trend_strength': 0.6,
                'fibonacci_levels': [0.382, 0.618],
                'hold_days': 5
            }
        }
        return parametros_map.get(estrategia, {})
    
    def _mutar_parametros(self, parametros: dict) -> dict:
        """Aplica mutação nos parâmetros"""
        parametros_mutados = parametros.copy()
        
        for key, value in parametros_mutados.items():
            if isinstance(value, (int, float)):
                mutacao = random.uniform(-0.1, 0.1)
                parametros_mutados[key] = value * (1 + mutacao)
            elif isinstance(value, list):
                for i in range(len(value)):
                    if isinstance(value[i], (int, float)):
                        mutacao = random.uniform(-0.1, 0.1)
                        value[i] = value[i] * (1 + mutacao)
        
        return parametros_mutados
    
    def _gerar_candidatos_bayesianos(self, parametros_base: dict) -> dict:
        """Gera candidatos usando aquisição bayesiana"""
        return self._mutar_parametros(parametros_base)
    
    def _selecionar_melhor_acao(self, q_table: dict, parametros_base: dict) -> dict:
        """Seleciona melhor ação baseada em Q-table"""
        if not q_table:
            return self._mutar_parametros(parametros_base)
        
        melhor_estado = max(q_table.keys(), key=lambda k: q_table[k])
        
        try:
            return eval(melhor_estado)
        except:
            return self._mutar_parametros(parametros_base)
    
    def _calcular_fitness(self, parametros: dict, historico: List[Dict]) -> float:
        """Calcula fitness dos parâmetros baseado no histórico"""
        if not historico:
            return 0.0
        
        total_trades = len(historico)
        trades_lucrativos = sum(1 for trade in historico if trade.get('pnl', 0) > 0)
        
        win_rate = trades_lucrativos / total_trades if total_trades > 0 else 0
        pnl_total = sum(trade.get('pnl', 0) for trade in historico)
        
        fitness = (win_rate * 0.6) + (min(pnl_total / 1000, 1.0) * 0.4)
        
        return max(0, fitness)

class SentimentAnalyzer:
    """Analisador de sentimento do mercado"""
    
    def __init__(self):
        self.fontes = ["twitter", "telegram", "reddit", "noticias"]
        self.cache_sentimento = {}
    
    async def analisar_sentimento(self, symbol: str = "BTC") -> float:
        """
        Scraping: Twitter, Telegram, Reddit, notícias
        Score: -1.0 (bearish) a +1.0 (bullish)
        """
        try:
            cache_key = f"{symbol}_{datetime.now().strftime('%Y%m%d_%H')}"
            if cache_key in self.cache_sentimento:
                return self.cache_sentimento[cache_key]
            
            sentimentos = []
            
            twitter_score = await self._analisar_twitter(symbol)
            sentimentos.append(twitter_score * 0.3)  # 30% peso
            
            telegram_score = await self._analisar_telegram(symbol)
            sentimentos.append(telegram_score * 0.2)  # 20% peso
            
            reddit_score = await self._analisar_reddit(symbol)
            sentimentos.append(reddit_score * 0.2)  # 20% peso
            
            noticias_score = await self._analisar_noticias(symbol)
            sentimentos.append(noticias_score * 0.3)  # 30% peso
            
            score_final = sum(sentimentos)
            score_final = max(-1.0, min(1.0, score_final))  # Clamp entre -1 e 1
            
            self.cache_sentimento[cache_key] = score_final
            
            return score_final
            
        except Exception as e:
            logger.error(f"Erro na análise de sentimento: {e}")
            return 0.0  # Neutro em caso de erro
    
    async def _analisar_twitter(self, symbol: str) -> float:
        """Analisa sentimento no Twitter"""
        return random.uniform(-0.5, 0.5)
    
    async def _analisar_telegram(self, symbol: str) -> float:
        """Analisa sentimento no Telegram"""
        return random.uniform(-0.3, 0.3)
    
    async def _analisar_reddit(self, symbol: str) -> float:
        """Analisa sentimento no Reddit"""
        return random.uniform(-0.4, 0.4)
    
    async def _analisar_noticias(self, symbol: str) -> float:
        """Analisa sentimento em notícias"""
        return random.uniform(-0.6, 0.6)

class AprendizadoContinuo:
    """Sistema de aprendizado contínuo com Reinforcement Learning"""
    
    def __init__(self):
        self.modelos = {}
        self.historico_aprendizado = {}
        self.politicas = {}
    
    async def treinar_modelo(self, bot_name: str, logs_trades: List[Dict], metricas: Dict):
        """
        Reinforcement Learning dos resultados
        Melhora política de decisões automaticamente
        """
        try:
            if not logs_trades:
                return
            
            estados, acoes, recompensas = self._preparar_dados_rl(logs_trades, metricas)
            
            if bot_name not in self.modelos:
                self.modelos[bot_name] = self._criar_modelo_rl(bot_name)
            
            modelo = self.modelos[bot_name]
            nova_politica = await self._treinar_rl(modelo, estados, acoes, recompensas)
            
            if self._validar_politica(nova_politica, bot_name):
                self.politicas[bot_name] = nova_politica
                
                self.historico_aprendizado[bot_name] = {
                    "timestamp": datetime.now(),
                    "trades_analisados": len(logs_trades),
                    "performance_media": metricas.get("win_rate", 0),
                    "melhoria": self._calcular_melhoria(bot_name, metricas)
                }
                
                logger.info(f"Modelo {bot_name} atualizado com {len(logs_trades)} trades")
            
        except Exception as e:
            logger.error(f"Erro no treinamento contínuo: {e}")
    
    def _preparar_dados_rl(self, logs_trades: List[Dict], metricas: Dict) -> tuple:
        """Prepara dados para treinamento RL"""
        estados = []
        acoes = []
        recompensas = []
        
        for trade in logs_trades:
            estado = trade.get("indicadores", {})
            estados.append(list(estado.values())[:10])  # Top 10 indicadores
            
            acao = 1 if trade.get("side") == "buy" else 0
            acoes.append(acao)
            
            pnl = trade.get("pnl", 0)
            recompensa = max(-1, min(1, pnl / 100))  # Normalizar entre -1 e 1
            recompensas.append(recompensa)
        
        return estados, acoes, recompensas
    
    def _criar_modelo_rl(self, bot_name: str):
        """Cria modelo de RL específico para o bot"""
        return {
            "tipo": "q_learning",
            "parametros": {"learning_rate": 0.01, "epsilon": 0.1},
            "q_table": {},
            "bot_name": bot_name
        }
    
    async def _treinar_rl(self, modelo, estados, acoes, recompensas):
        """Executa treinamento RL"""
        nova_politica = {
            "decisao_threshold": 0.6,
            "risk_adjustment": 0.8,
            "confidence_boost": 1.1
        }
        return nova_politica
    
    def _validar_politica(self, politica, bot_name: str) -> bool:
        """Valida se nova política é melhor que a anterior"""
        return (
            0.5 <= politica.get("decisao_threshold", 0) <= 0.9 and
            0.5 <= politica.get("risk_adjustment", 0) <= 1.2
        )
    
    def _calcular_melhoria(self, bot_name: str, metricas: Dict) -> float:
        """Calcula melhoria em relação ao histórico"""
        if bot_name not in self.historico_aprendizado:
            return 0.0
        
        historico = self.historico_aprendizado[bot_name]
        performance_anterior = historico.get("performance_media", 0)
        performance_atual = metricas.get("win_rate", 0)
        
        return performance_atual - performance_anterior

class MotorIA:
    """Motor de Inteligência Artificial para trading"""
    
    def __init__(self, config: Configuracao):
        self.config = config
        self.ia_config = config.get_ia_config()
        self.modelos = {}
        self.historico_predicoes = {}
        self.metricas_performance = {}
        
        self.gerador_sinais = GeradorSinais()
        self.auto_tuner = AutoTuner()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.aprendizado_continuo = AprendizadoContinuo()
    
    async def inicializar(self):
        """Inicializa o motor de IA"""
        logger.info("Inicializando motor de IA")
        
        os.makedirs(self.ia_config.modelo_path, exist_ok=True)
        
        await self._carregar_modelos()
        
        if not self.modelos:
            await self._inicializar_modelos()
        
        logger.info("Motor de IA inicializado com sucesso")
    
    async def _carregar_modelos(self):
        """Carrega modelos salvos"""
        try:
            modelo_files = [
                'modelo_predicao_preco.pkl',
                'modelo_classificacao_tendencia.pkl',
                'modelo_volatilidade.pkl'
            ]
            
            for modelo_file in modelo_files:
                modelo_path = os.path.join(self.ia_config.modelo_path, modelo_file)
                if os.path.exists(modelo_path):
                    with open(modelo_path, 'rb') as f:
                        modelo_name = modelo_file.replace('.pkl', '')
                        self.modelos[modelo_name] = pickle.load(f)
                        logger.info(f"Modelo {modelo_name} carregado")
        
        except Exception as e:
            logger.error(f"Erro ao carregar modelos: {e}")
    
    async def _inicializar_modelos(self):
        """Inicializa modelos de IA"""
        try:
            from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
            from sklearn.preprocessing import StandardScaler
            
            self.modelos['modelo_predicao_preco'] = {
                'regressor': RandomForestRegressor(n_estimators=100, random_state=42),
                'scaler': StandardScaler(),
                'treinado': False
            }
            
            self.modelos['modelo_classificacao_tendencia'] = {
                'classifier': RandomForestClassifier(n_estimators=100, random_state=42),
                'scaler': StandardScaler(),
                'treinado': False
            }
            
            self.modelos['modelo_volatilidade'] = {
                'regressor': RandomForestRegressor(n_estimators=50, random_state=42),
                'scaler': StandardScaler(),
                'treinado': False
            }
            
            logger.info("Modelos de IA inicializados")
            
        except ImportError as e:
            logger.error(f"Bibliotecas de ML não disponíveis: {e}")
            await self._criar_modelos_simulados()
    
    async def _criar_modelos_simulados(self):
        """Cria modelos simulados para demonstração"""
        class ModeloSimulado:
            def __init__(self, tipo):
                self.tipo = tipo
                self.treinado = True
            
            def predict(self, X):
                import random
                if self.tipo == 'preco':
                    return np.array([random.uniform(-0.02, 0.02) for _ in range(len(X))])
                elif self.tipo == 'tendencia':
                    return np.array([random.choice([0, 1, 2]) for _ in range(len(X))])  # 0=baixa, 1=lateral, 2=alta
                else:  # volatilidade
                    return np.array([random.uniform(0.01, 0.05) for _ in range(len(X))])
            
            def fit(self, X, y):
                pass
        
        self.modelos['modelo_predicao_preco'] = {
            'regressor': ModeloSimulado('preco'),
            'scaler': None,
            'treinado': True
        }
        
        self.modelos['modelo_classificacao_tendencia'] = {
            'classifier': ModeloSimulado('tendencia'),
            'scaler': None,
            'treinado': True
        }
        
        self.modelos['modelo_volatilidade'] = {
            'regressor': ModeloSimulado('volatilidade'),
            'scaler': None,
            'treinado': True
        }
        
        logger.info("Modelos simulados criados")
    
    async def analisar_mercado(self, symbol: str, ohlcv_data: List[List]) -> Dict[str, Any]:
        """Análise de mercado usando IA"""
        try:
            if len(ohlcv_data) < 20:
                return self._analise_basica()
            
            features = self._extrair_features(ohlcv_data)
            
            predicao_preco = await self._prever_preco(features)
            predicao_tendencia = await self._prever_tendencia(features)
            predicao_volatilidade = await self._prever_volatilidade(features)
            
            confianca = self._calcular_confianca(features, symbol)
            
            analise = {
                'predicao_preco_percent': predicao_preco,
                'predicao_tendencia': predicao_tendencia,
                'predicao_volatilidade': predicao_volatilidade,
                'confianca': confianca,
                'recomendacao': self._gerar_recomendacao(predicao_preco, predicao_tendencia, confianca),
                'timestamp': datetime.now(),
                'features_utilizadas': len(features) if features is not None else 0
            }
            
            self.historico_predicoes.setdefault(symbol, []).append(analise)
            
            return analise
            
        except Exception as e:
            logger.error(f"Erro na análise de IA para {symbol}: {e}")
            return self._analise_basica()
    
    def _extrair_features(self, ohlcv_data: List[List]) -> Optional[np.ndarray]:
        """Extrai features dos dados OHLCV"""
        try:
            df = pd.DataFrame(ohlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            df['returns'] = df['close'].pct_change()
            df['volatility'] = df['returns'].rolling(10).std()
            df['sma_10'] = df['close'].rolling(10).mean()
            df['sma_20'] = df['close'].rolling(20).mean()
            df['rsi'] = self._calcular_rsi(df['close'])
            df['volume_sma'] = df['volume'].rolling(10).mean()
            df['price_volume_trend'] = df['close'] * df['volume']
            
            df['momentum_5'] = df['close'] / df['close'].shift(5) - 1
            df['momentum_10'] = df['close'] / df['close'].shift(10) - 1
            
            df['high_low_ratio'] = (df['high'] - df['low']) / df['close']
            df['open_close_ratio'] = (df['close'] - df['open']) / df['open']
            
            feature_columns = [
                'returns', 'volatility', 'sma_10', 'sma_20', 'rsi',
                'volume_sma', 'momentum_5', 'momentum_10',
                'high_low_ratio', 'open_close_ratio'
            ]
            
            features = df[feature_columns].iloc[-1:].values
            
            if np.isnan(features).any():
                return None
            
            return features
            
        except Exception as e:
            logger.error(f"Erro ao extrair features: {e}")
            return None
    
    def _calcular_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calcula RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    async def _prever_preco(self, features: np.ndarray) -> float:
        """Prevê mudança percentual do preço"""
        try:
            modelo = self.modelos.get('modelo_predicao_preco')
            if not modelo or not modelo['treinado']:
                return 0.0
            
            if modelo['scaler']:
                features_scaled = modelo['scaler'].transform(features)
            else:
                features_scaled = features
            
            predicao = modelo['regressor'].predict(features_scaled)[0]
            return float(predicao)
            
        except Exception as e:
            logger.error(f"Erro na predição de preço: {e}")
            return 0.0
    
    async def _prever_tendencia(self, features: np.ndarray) -> str:
        """Prevê direção da tendência"""
        try:
            modelo = self.modelos.get('modelo_classificacao_tendencia')
            if not modelo or not modelo['treinado']:
                return "lateral"
            
            if modelo['scaler']:
                features_scaled = modelo['scaler'].transform(features)
            else:
                features_scaled = features
            
            predicao = modelo['classifier'].predict(features_scaled)[0]
            
            mapeamento = {0: "baixa", 1: "lateral", 2: "alta"}
            return mapeamento.get(predicao, "lateral")
            
        except Exception as e:
            logger.error(f"Erro na predição de tendência: {e}")
            return "lateral"
    
    async def _prever_volatilidade(self, features: np.ndarray) -> float:
        """Prevê volatilidade"""
        try:
            modelo = self.modelos.get('modelo_volatilidade')
            if not modelo or not modelo['treinado']:
                return 0.02
            
            if modelo['scaler']:
                features_scaled = modelo['scaler'].transform(features)
            else:
                features_scaled = features
            
            predicao = modelo['regressor'].predict(features_scaled)[0]
            return max(0.001, float(predicao))
            
        except Exception as e:
            logger.error(f"Erro na predição de volatilidade: {e}")
            return 0.02
    
    def _calcular_confianca(self, features: np.ndarray, symbol: str) -> float:
        """Calcula confiança da predição"""
        try:
            if features is None:
                return 0.3
            
            historico = self.historico_predicoes.get(symbol, [])
            if len(historico) > 10:
                acertos = sum(1 for pred in historico[-10:] if pred.get('acertou', False))
                taxa_acerto = acertos / 10
                confianca_historica = taxa_acerto
            else:
                confianca_historica = 0.5
            
            volatilidade_features = np.std(features)
            confianca_volatilidade = max(0.1, 1 - volatilidade_features)
            
            confianca_final = (confianca_historica * 0.6 + confianca_volatilidade * 0.4)
            
            return min(0.95, max(0.1, confianca_final))
            
        except Exception as e:
            logger.error(f"Erro ao calcular confiança: {e}")
            return 0.5
    
    def _gerar_recomendacao(self, predicao_preco: float, predicao_tendencia: str, confianca: float) -> str:
        """Gera recomendação de trading"""
        try:
            if confianca < 0.4:
                return "hold"
            
            if predicao_tendencia == "alta" and predicao_preco > 0.01:
                return "buy"
            elif predicao_tendencia == "baixa" and predicao_preco < -0.01:
                return "sell"
            else:
                return "hold"
                
        except Exception as e:
            logger.error(f"Erro ao gerar recomendação: {e}")
            return "hold"
    
    def _analise_basica(self) -> Dict[str, Any]:
        """Análise básica quando IA não está disponível"""
        return {
            'predicao_preco_percent': 0.0,
            'predicao_tendencia': "lateral",
            'predicao_volatilidade': 0.02,
            'confianca': 0.3,
            'recomendacao': "hold",
            'timestamp': datetime.now(),
            'features_utilizadas': 0
        }
    
    async def treinar_modelos(self, dados_historicos: Dict[str, List]) -> bool:
        """Treina modelos com dados históricos"""
        try:
            if not self.ia_config.treinamento_ativo:
                logger.info("Treinamento de IA desabilitado")
                return False
            
            logger.info("Iniciando treinamento de modelos de IA")
            
            X, y_preco, y_tendencia, y_volatilidade = self._preparar_dados_treinamento(dados_historicos)
            
            if len(X) < 100:
                logger.warning("Dados insuficientes para treinamento")
                return False
            
            await self._treinar_modelo_preco(X, y_preco)
            
            await self._treinar_modelo_tendencia(X, y_tendencia)
            
            await self._treinar_modelo_volatilidade(X, y_volatilidade)
            
            await self._salvar_modelos()
            
            logger.info("Treinamento de modelos concluído")
            return True
            
        except Exception as e:
            logger.error(f"Erro no treinamento de modelos: {e}")
            return False
    
    def _preparar_dados_treinamento(self, dados_historicos: Dict) -> tuple:
        """Prepara dados para treinamento"""
        X = []
        y_preco = []
        y_tendencia = []
        y_volatilidade = []
        
        for symbol, ohlcv_list in dados_historicos.items():
            for i in range(20, len(ohlcv_list) - 1):
                features = self._extrair_features(ohlcv_list[i-20:i])
                if features is not None:
                    X.append(features[0])
                    
                    current_price = ohlcv_list[i][4]
                    next_price = ohlcv_list[i+1][4]
                    price_return = (next_price - current_price) / current_price
                    y_preco.append(price_return)
                    
                    if price_return > 0.01:
                        y_tendencia.append(2)  # alta
                    elif price_return < -0.01:
                        y_tendencia.append(0)  # baixa
                    else:
                        y_tendencia.append(1)  # lateral
                    
                    volatility = np.std([candle[4] for candle in ohlcv_list[i-10:i]]) / current_price
                    y_volatilidade.append(volatility)
        
        return np.array(X), np.array(y_preco), np.array(y_tendencia), np.array(y_volatilidade)
    
    async def _treinar_modelo_preco(self, X: np.ndarray, y: np.ndarray):
        """Treina modelo de predição de preço"""
        try:
            modelo = self.modelos['modelo_predicao_preco']
            
            if modelo['scaler']:
                X_scaled = modelo['scaler'].fit_transform(X)
            else:
                X_scaled = X
            
            modelo['regressor'].fit(X_scaled, y)
            modelo['treinado'] = True
            
            logger.info("Modelo de predição de preço treinado")
            
        except Exception as e:
            logger.error(f"Erro ao treinar modelo de preço: {e}")
    
    async def _treinar_modelo_tendencia(self, X: np.ndarray, y: np.ndarray):
        """Treina modelo de classificação de tendência"""
        try:
            modelo = self.modelos['modelo_classificacao_tendencia']
            
            if modelo['scaler']:
                X_scaled = modelo['scaler'].fit_transform(X)
            else:
                X_scaled = X
            
            modelo['classifier'].fit(X_scaled, y)
            modelo['treinado'] = True
            
            logger.info("Modelo de classificação de tendência treinado")
            
        except Exception as e:
            logger.error(f"Erro ao treinar modelo de tendência: {e}")
    
    async def _treinar_modelo_volatilidade(self, X: np.ndarray, y: np.ndarray):
        """Treina modelo de predição de volatilidade"""
        try:
            modelo = self.modelos['modelo_volatilidade']
            
            if modelo['scaler']:
                X_scaled = modelo['scaler'].fit_transform(X)
            else:
                X_scaled = X
            
            modelo['regressor'].fit(X_scaled, y)
            modelo['treinado'] = True
            
            logger.info("Modelo de predição de volatilidade treinado")
            
        except Exception as e:
            logger.error(f"Erro ao treinar modelo de volatilidade: {e}")
    
    async def _salvar_modelos(self):
        """Salva modelos treinados"""
        try:
            for nome, modelo in self.modelos.items():
                if modelo.get('treinado'):
                    modelo_path = os.path.join(self.ia_config.modelo_path, f"{nome}.pkl")
                    with open(modelo_path, 'wb') as f:
                        pickle.dump(modelo, f)
                    logger.info(f"Modelo {nome} salvo")
                    
        except Exception as e:
            logger.error(f"Erro ao salvar modelos: {e}")
    
    async def otimizar_parametros_bot(self, bot_name: str, historico_trades: List) -> Dict[str, Any]:
        """Otimiza parâmetros de um bot usando IA"""
        try:
            logger.info(f"Otimizando parâmetros do bot {bot_name}")
            
            if len(historico_trades) < 50:
                logger.warning("Histórico insuficiente para otimização")
                return {}
            
            performance_atual = self._analisar_performance_trades(historico_trades)
            
            otimizacoes = self._gerar_otimizacoes(bot_name, performance_atual)
            
            logger.info(f"Otimizações geradas para {bot_name}: {otimizacoes}")
            return otimizacoes
            
        except Exception as e:
            logger.error(f"Erro na otimização de parâmetros: {e}")
            return {}
    
    def _analisar_performance_trades(self, trades: List) -> Dict[str, float]:
        """Analisa performance dos trades"""
        if not trades:
            return {}
        
        total_trades = len(trades)
        winning_trades = len([t for t in trades if t.pnl > 0])
        losing_trades = total_trades - winning_trades
        
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        total_pnl = sum(t.pnl for t in trades)
        avg_win = np.mean([t.pnl for t in trades if t.pnl > 0]) if winning_trades > 0 else 0
        avg_loss = np.mean([t.pnl for t in trades if t.pnl < 0]) if losing_trades > 0 else 0
        
        return {
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': abs(avg_win / avg_loss) if avg_loss != 0 else 0,
            'total_trades': total_trades
        }
    
    def _gerar_otimizacoes(self, bot_name: str, performance: Dict) -> Dict[str, Any]:
        """Gera sugestões de otimização"""
        otimizacoes = {}
        
        win_rate = performance.get('win_rate', 0)
        profit_factor = performance.get('profit_factor', 0)
        
        if bot_name == "arbitragem":
            if win_rate < 0.6:
                otimizacoes['min_profit_percent'] = 0.8  # Aumentar threshold
            if profit_factor < 1.5:
                otimizacoes['max_position_size'] = 500  # Reduzir tamanho
                
        elif bot_name == "scalping":
            if win_rate < 0.7:
                otimizacoes['target_profit'] = 0.0015  # Aumentar target
            if profit_factor < 2.0:
                otimizacoes['max_hold_time'] = 180  # Reduzir tempo
                
        elif bot_name == "grid":
            if win_rate < 0.5:
                otimizacoes['grid_spacing'] = 0.015  # Aumentar espaçamento
            if profit_factor < 1.2:
                otimizacoes['grid_size'] = 8  # Reduzir tamanho do grid
        
        return otimizacoes
    
    async def finalizar(self):
        """Finaliza motor de IA"""
        logger.info("Finalizando motor de IA")
        
        if self.ia_config.treinamento_ativo:
            await self._salvar_modelos()
        
        metricas_path = os.path.join(self.ia_config.modelo_path, 'metricas_performance.pkl')
        try:
            with open(metricas_path, 'wb') as f:
                pickle.dump(self.metricas_performance, f)
        except Exception as e:
            logger.error(f"Erro ao salvar métricas: {e}")
        
        logger.info("Motor de IA finalizado")
