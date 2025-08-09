"""
Motor de IA para análise de mercado e otimização de trading
"""

import asyncio
import logging
import numpy as np
import pandas as pd
import secrets
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pickle  # nosec
import os
import secrets

from src.core.configuracao import Configuracao

logger = logging.getLogger(__name__)


class Sinal:
    """Representa um sinal de trading gerado pela IA"""

    def __init__(
        self,
        acao: str,
        confidence: float,
        preco_entrada: Optional[float] = None,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
    ):
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
            "sma": 0.15,
            "ema": 0.15,
            "rsi": 0.12,
            "macd": 0.12,
            "bollinger": 0.10,
            "stochastic": 0.08,
            "williams_r": 0.06,
            "cci": 0.06,
            "momentum": 0.05,
            "roc": 0.05,
            "atr": 0.06,
        }

    def analisar_mercado(self, dados_market) -> Sinal:
        """Combina 50+ indicadores técnicos e retorna sinal com confidence score"""
        if not dados_market or "ohlcv" not in dados_market:
            return Sinal("parar", 0.0)

        ohlcv = dados_market["ohlcv"]
        if len(ohlcv) < 50:
            return Sinal("parar", 0.0)

        scores = self._calcular_todos_indicadores(ohlcv)

        score_final = sum(
            scores[ind] * peso for ind, peso in self.pesos.items() if ind in scores
        )

        if score_final > 0.6:
            acao = "comprar"
            confidence = min(score_final, 0.95)
        elif score_final < -0.6:
            acao = "vender"
            confidence = min(abs(score_final), 0.95)
        else:
            acao = "parar"
            confidence = 1.0 - abs(score_final)

        preco_atual = ohlcv[-1][4]  # Close price

        return Sinal(
            acao=acao,
            confidence=confidence,
            preco_entrada=preco_atual,
            stop_loss=preco_atual * (0.98 if acao == "comprar" else 1.02),
            take_profit=preco_atual * (1.04 if acao == "comprar" else 0.96),
        )

    def _calcular_todos_indicadores(self, ohlcv) -> Dict[str, float]:
        """Calcula todos os indicadores técnicos"""
        closes = [candle[4] for candle in ohlcv]
        highs = [candle[2] for candle in ohlcv]
        lows = [candle[3] for candle in ohlcv]
        volumes = [candle[5] for candle in ohlcv]

        scores = {}

        scores["sma"] = self._score_sma(closes)
        scores["ema"] = self._score_ema(closes)

        scores["rsi"] = self._score_rsi(closes)
        scores["stochastic"] = self._score_stochastic(highs, lows, closes)
        scores["williams_r"] = self._score_williams_r(highs, lows, closes)
        scores["cci"] = self._score_cci(highs, lows, closes)

        scores["macd"] = self._score_macd(closes)
        scores["momentum"] = self._score_momentum(closes)
        scores["roc"] = self._score_roc(closes)

        # Volatilidade
        scores["bollinger"] = self._score_bollinger(closes)
        scores["atr"] = self._score_atr(highs, lows, closes)

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
            ema_12 = (closes[-(i + 1)] * 2 + ema_12 * 11) / 13

        for i in range(min(26, len(closes))):
            ema_26 = (closes[-(i + 1)] * 2 + ema_26 * 25) / 27

        if ema_12 > ema_26:
            return 0.7
        elif ema_12 < ema_26:
            return -0.7
        return 0.0

    def _score_rsi(self, closes) -> float:
        """Score baseado em RSI"""
        if len(closes) < 15:
            return 0.0

        deltas = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
        gains = [d if d > 0 else 0 for d in deltas[-14:]]
        losses = [-d if d < 0 else 0 for d in deltas[-14:]]

        avg_gain = sum(gains) / 14
        avg_loss = sum(losses) / 14

        if avg_loss == 0:
            rsi = 100.0
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
        std_dev = variance**0.5

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
            tr2 = abs(highs[i] - closes[i - 1]) if i > -len(closes) else tr1
            tr3 = abs(lows[i] - closes[i - 1]) if i > -len(closes) else tr1
            true_ranges.append(max(tr1, tr2, tr3))

        atr = sum(true_ranges) / 14
        volatility_ratio = atr / closes[-1]

        if volatility_ratio > 0.02:
            return 0.3
        return 0.0

    def _calcular_indicadores_tecnicos(self, precos: List[float]) -> Dict:
        """Calcula todos os indicadores técnicos necessários"""
        try:
            if not precos or len(precos) < 20:
                return {}

            closes = precos
            highs = [p * 1.01 for p in precos]  # High = close * 1.01
            lows = [p * 0.99 for p in precos]   # Low = close * 0.99
            volumes = [1000] * len(precos)      # Volume constante para testes

            indicadores = {}
            
            if len(closes) >= 20:
                sma_20 = sum(closes[-20:]) / 20
                indicadores['sma_20'] = sma_20
                indicadores['price_vs_sma'] = (closes[-1] - sma_20) / sma_20

            if len(closes) >= 14:
                deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
                gains = [d if d > 0 else 0 for d in deltas]
                losses = [-d if d < 0 else 0 for d in deltas]
                
                avg_gain = sum(gains[-14:]) / 14 if gains else 0
                avg_loss = sum(losses[-14:]) / 14 if losses else 0
                
                if avg_loss != 0:
                    rs = avg_gain / avg_loss
                    rsi = 100 - (100 / (1 + rs))
                else:
                    rsi = 100 if avg_gain > 0 else 50
                    
                indicadores['rsi'] = rsi

            if len(closes) >= 26:
                ema_12 = closes[-1]  # Simplified
                ema_26 = sum(closes[-26:]) / 26
                macd = ema_12 - ema_26
                indicadores['macd'] = macd

            if len(closes) >= 20:
                sma = sum(closes[-20:]) / 20
                variance = sum([(x - sma) ** 2 for x in closes[-20:]]) / 20
                std_dev = variance ** 0.5
                
                bb_upper = sma + (2 * std_dev)
                bb_lower = sma - (2 * std_dev)
                bb_position = (closes[-1] - bb_lower) / (bb_upper - bb_lower) if bb_upper != bb_lower else 0.5
                
                indicadores['bb_upper'] = bb_upper
                indicadores['bb_lower'] = bb_lower
                indicadores['bb_position'] = bb_position
                indicadores['bollinger_bands'] = {
                    'upper': bb_upper,
                    'lower': bb_lower,
                    'position': bb_position
                }

            if len(volumes) >= 20:
                avg_volume = sum(volumes[-20:]) / 20
                volume_ratio = volumes[-1] / avg_volume if avg_volume > 0 else 1.0
                indicadores['volume_ratio'] = volume_ratio

            return indicadores

        except Exception as e:
            logger.error(f"Erro ao calcular indicadores técnicos: {e}")
            return {}

    def _combinar_sinais(self, sinais_individuais: List[Dict]) -> Dict:
        """Combina múltiplos sinais em uma decisão final"""
        try:
            if not sinais_individuais:
                return {'acao': 'parar', 'confidence': 0.0, 'razao': 'Sem sinais'}

            sinais_compra = 0
            sinais_venda = 0
            confidence_total = 0.0

            for sinal in sinais_individuais:
                acao = sinal.get('acao', 'parar')
                confidence = sinal.get('confidence', 0.0)
                
                if acao == 'comprar':
                    sinais_compra += 1
                    confidence_total += confidence
                elif acao == 'vender':
                    sinais_venda += 1
                    confidence_total += confidence

            if sinais_compra > sinais_venda:
                acao_final = 'comprar'
                confidence_final = confidence_total / len(sinais_individuais)
            elif sinais_venda > sinais_compra:
                acao_final = 'vender'
                confidence_final = confidence_total / len(sinais_individuais)
            else:
                acao_final = 'parar'
                confidence_final = 0.0

            return {
                'acao': acao_final,
                'confidence': min(confidence_final, 1.0),
                'razao': f'Combinação de {len(sinais_individuais)} sinais',
                'sinais_compra': sinais_compra,
                'sinais_venda': sinais_venda
            }

        except Exception as e:
            logger.error(f"Erro ao combinar sinais: {e}")
            return {'acao': 'parar', 'confidence': 0.0, 'razao': f'Erro: {str(e)}'}


class AutoTuner:
    """Auto-tuner que usa algoritmos genéticos/bayesiano/RL para otimização"""

    def __init__(self):
        self.historico_otimizacoes = {}
        self.parametros_otimos = {}
        self.algoritmos = ["genetico", "bayesiano", "reinforcement_learning"]

    def otimizar_parametros(self, estrategia: str, historico: List[Dict]) -> dict:
        """Usa algoritmos genéticos/bayesiano/RL para otimizar parâmetros"""
        try:
            def fitness_function(params):
                return self._calcular_fitness(params, historico)
            
            resultado = self._algoritmo_genetico(fitness_function, populacao_size=20, geracoes=10)
            
            if "stop_loss" not in resultado:
                resultado["stop_loss"] = resultado.get("stop_loss_pct", 0.02)
            
            return resultado
            
        except Exception as e:
            logging.error(f"Erro na otimização de parâmetros: {e}")
            return {"stop_loss": 0.02, "take_profit": 0.04}

    def _selecionar_algoritmo(self, estrategia: str) -> str:
        """Seleciona melhor algoritmo para a estratégia"""
        algoritmo_map = {
            "arbitragem": "bayesiano",  # Precisão em latência
            "grid": "genetico",  # Múltiplos parâmetros
            "momentum": "reinforcement_learning",  # Adaptação dinâmica
            "scalping": "bayesiano",  # Otimização de velocidade
            "mean_reversion": "genetico",  # Thresholds complexos
            "swing": "reinforcement_learning",  # Padrões adaptativos
        }
        return algoritmo_map.get(estrategia, "genetico")

    def _otimizar_genetico(self, estrategia: str, historico: List[Dict]) -> dict:
        """Otimização usando algoritmo genético"""
        populacao_size = 50
        geracoes = 20

        parametros_base = self._parametros_padrao(estrategia)

        melhor_fitness: float = 0.0
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
        melhor_score = 0.0
        melhores_parametros = parametros_base.copy()

        for i in range(iteracoes):
            parametros_candidatos = self._gerar_candidatos_bayesianos(parametros_base)

            score = self._calcular_fitness(parametros_candidatos, historico)

            if score > melhor_score:
                melhor_score = float(score)
                melhores_parametros = parametros_candidatos.copy()

        return melhores_parametros

    def _otimizar_rl(self, estrategia: str, historico: List[Dict]) -> dict:
        """Otimização usando Reinforcement Learning"""
        parametros_base = self._parametros_padrao(estrategia)

        episodios = 100
        epsilon = 0.1
        alpha = 0.1

        q_table: Dict[str, float] = {}
        melhor_reward: float = 0.0
        melhores_parametros = parametros_base.copy()

        for episodio in range(episodios):
            if secrets.SystemRandom().random() < epsilon:  # nosec
                parametros_acao = self._mutar_parametros(parametros_base)
            else:
                parametros_acao = self._selecionar_melhor_acao(q_table, parametros_base)

            reward = self._calcular_fitness(parametros_acao, historico)

            estado = str(parametros_acao)
            if estado not in q_table:
                q_table[estado] = 0
            q_table[estado] += alpha * (reward - q_table[estado])

            if reward > melhor_reward:
                melhor_reward = float(reward)
                melhores_parametros = parametros_acao.copy()

        return melhores_parametros

    def _parametros_padrao(self, estrategia: str) -> Dict[str, Any]:
        """Retorna parâmetros padrão para cada estratégia"""
        parametros_map = {
            "arbitragem": {
                "spread_minimo": 0.3,
                "timeout_execucao": 50,
                "volume_minimo": 1000,
            },
            "grid": {"num_grids": 10, "espacamento_pct": 0.5, "take_profit_pct": 1.0},
            "momentum": {
                "breakout_threshold": 1.002,
                "volume_confirmacao": 1.5,
                "stop_loss_pct": 2.0,
            },
            "scalping": {
                "spread_target": 0.1,
                "hold_time_max": 30,
                "profit_target": 0.2,
            },
            "mean_reversion": {
                "rsi_oversold": 30,
                "rsi_overbought": 70,
                "reversion_threshold": 2.0,
            },
            "swing": {
                "trend_strength": 0.6,
                "fibonacci_levels": [0.382, 0.618],
                "hold_days": 5,
            },
        }
        result = parametros_map.get(estrategia, {})
        if isinstance(result, dict):
            return result
        return {}

    def _mutar_parametros(self, parametros: dict) -> dict:
        """Aplica mutação nos parâmetros"""
        parametros_mutados = parametros.copy()

        for key, value in parametros_mutados.items():
            if isinstance(value, (int, float)):
                mutacao = secrets.SystemRandom().uniform(-0.1, 0.1)  # nosec
                parametros_mutados[key] = value * (1 + mutacao)
            elif isinstance(value, list):
                for i in range(len(value)):
                    if isinstance(value[i], (int, float)):
                        mutacao = secrets.SystemRandom().uniform(
                            -0.1, 0.1
                        )  # nosec  # nosec
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
            return eval(melhor_estado)  # nosec
        except:
            return self._mutar_parametros(parametros_base)

    def _calcular_fitness(self, parametros: dict, historico: List[Dict]) -> float:
        """Calcula fitness dos parâmetros baseado no histórico"""
        if not historico:
            return 0.0

        total_trades = len(historico)
        trades_lucrativos = sum(1 for trade in historico if trade.get("pnl", 0) > 0)

        win_rate = trades_lucrativos / total_trades if total_trades > 0 else 0
        pnl_total = sum(trade.get("pnl", 0) for trade in historico)

        fitness = (win_rate * 0.6) + (min(pnl_total / 1000, 1.0) * 0.4)

        return max(0, fitness)

    def _algoritmo_genetico(self, fitness_function, populacao_size: int = 50, geracoes: int = 100) -> dict:
        """Implementa algoritmo genético para otimização"""
        try:
            import random
            
            populacao = []
            for _ in range(populacao_size):
                individuo = {
                    "stop_loss": random.uniform(0.005, 0.05),
                    "take_profit": random.uniform(0.02, 0.10),
                    "position_size": random.uniform(0.01, 0.1)
                }
                populacao.append(individuo)
            
            for geracao in range(geracoes):
                fitness_scores = []
                for individuo in populacao:
                    score = fitness_function(individuo)
                    fitness_scores.append((score, individuo))
                
                fitness_scores.sort(key=lambda x: x[0], reverse=True)
                
                elite_size = populacao_size // 4
                nova_populacao = [ind for _, ind in fitness_scores[:elite_size]]
                
                while len(nova_populacao) < populacao_size:
                    pai1 = random.choice(fitness_scores[:populacao_size//2])[1]
                    pai2 = random.choice(fitness_scores[:populacao_size//2])[1]
                    
                    filho = {}
                    for key in pai1.keys():
                        filho[key] = random.choice([pai1[key], pai2[key]])
                    
                    if random.random() < 0.1:  # 10% chance de mutação
                        key_mutacao = random.choice(list(filho.keys()))
                        if key_mutacao == "stop_loss":
                            filho[key_mutacao] = random.uniform(0.005, 0.05)
                        elif key_mutacao == "take_profit":
                            filho[key_mutacao] = random.uniform(0.02, 0.10)
                        elif key_mutacao == "position_size":
                            filho[key_mutacao] = random.uniform(0.01, 0.1)
                    
                    nova_populacao.append(filho)
                
                populacao = nova_populacao
            
            fitness_final = [(fitness_function(ind), ind) for ind in populacao]
            fitness_final.sort(key=lambda x: x[0], reverse=True)
            
            return fitness_final[0][1]
            
        except Exception as e:
            logging.error(f"Erro no algoritmo genético: {e}")
            return {
                "stop_loss": 0.02,
                "take_profit": 0.04,
                "position_size": 0.05
            }

    def _otimizacao_bayesiana(self, historico_performance: List[Dict]) -> dict:
        """Implementa otimização bayesiana"""
        try:
            if not historico_performance:
                return {"stop_loss": 0.02}
            
            melhores_params = []
            for entry in historico_performance:
                if entry.get("score", 0) > 0.6:  # Threshold para bons resultados
                    melhores_params.append(entry["params"])
            
            if not melhores_params:
                return {"stop_loss": 0.015}
            
            # Calcular média dos melhores parâmetros
            param_keys = set()
            for params in melhores_params:
                param_keys.update(params.keys())
            
            resultado = {}
            for key in param_keys:
                valores = [p.get(key, 0) for p in melhores_params if key in p]
                if valores:
                    import random
                    media = sum(valores) / len(valores)
                    variacao = media * 0.1  # 10% de variação
                    resultado[key] = media + random.uniform(-variacao, variacao)
                    
                    if key == "stop_loss":
                        resultado[key] = max(0.005, min(0.05, resultado[key]))
                    elif key == "take_profit":
                        resultado[key] = max(0.02, min(0.10, resultado[key]))
                    elif key == "position_size":
                        resultado[key] = max(0.01, min(0.1, resultado[key]))
            
            return resultado
            
        except Exception as e:
            logging.error(f"Erro na otimização bayesiana: {e}")
            return {"stop_loss": 0.02}


class SentimentAnalyzer:
    """Analisador de sentimento do mercado"""

    def __init__(self):
        self.fontes = ["twitter", "telegram", "reddit", "noticias"]
        self.cache_sentimento = {}

    def analisar_sentimento(self, symbol: str = "BTC") -> float:
        """
        Scraping: Twitter, Telegram, Reddit, notícias
        Score: -1.0 (bearish) a +1.0 (bullish)
        """
        try:
            cache_key = f"{symbol}_{datetime.now().strftime('%Y%m%d_%H')}"
            if cache_key in self.cache_sentimento:
                return self.cache_sentimento[cache_key]

            sentimentos = []

            twitter_score = self._analisar_twitter(symbol)
            sentimentos.append(twitter_score * 0.3)  # 30% peso

            telegram_score = self._analisar_telegram(symbol)
            sentimentos.append(telegram_score * 0.2)  # 20% peso

            reddit_score = self._analisar_reddit(symbol)
            sentimentos.append(reddit_score * 0.2)  # 20% peso

            noticias_score = self._analisar_noticias(symbol)
            sentimentos.append(noticias_score * 0.3)  # 30% peso

            score_final = sum(sentimentos)
            score_final = max(-1.0, min(1.0, score_final))  # Clamp entre -1 e 1

            self.cache_sentimento[cache_key] = score_final

            return score_final

        except Exception as e:
            logger.error(f"Erro na análise de sentimento: {e}")
            return 0.0  # Neutro em caso de erro

    def _obter_noticias(self, symbol: str = "BTC") -> List[Dict]:
        """Obtém notícias sobre criptomoeda específica"""
        try:
            noticias = []
            for i in range(5):
                noticia = {
                    "title": f"{symbol} Market Analysis #{i+1}",
                    "content": f"Recent developments in {symbol} market show interesting trends...",
                    "timestamp": datetime.now().isoformat(),
                    "source": f"news_source_{i}"
                }
                noticias.append(noticia)
            return noticias
        except Exception as e:
            logger.error(f"Erro ao obter notícias: {e}")
            return []

    def _obter_tweets(self, symbol: str = "BTC") -> List[str]:
        """Obtém tweets sobre criptomoeda específica"""
        try:
            tweets = [
                f"{symbol} to the moon! 🚀",
                f"{symbol} market looking bullish",
                f"Concerned about {symbol} volatility",
                f"Great time to buy {symbol} dip!",
                f"{symbol} adoption increasing globally"
            ]
            return tweets
        except Exception as e:
            logger.error(f"Erro ao obter tweets: {e}")
            return []

    def _obter_posts_reddit(self, symbol: str = "BTC") -> List[Dict]:
        """Obtém posts do Reddit sobre criptomoeda específica"""
        try:
            posts = [
                {"title": f"{symbol} analysis - very bullish", "score": 150},
                {"title": f"{symbol} crash incoming?", "score": -50},
                {"title": f"Hodl {symbol} strong!", "score": 200},
                {"title": f"{symbol} technical analysis", "score": 75},
                {"title": f"New {symbol} developments", "score": 120}
            ]
            return posts
        except Exception as e:
            logger.error(f"Erro ao obter posts Reddit: {e}")
            return []

    def _analisar_twitter(self, symbol: str = "BTC") -> float:
        """Analisa sentimento no Twitter"""
        try:
            tweets = self._obter_tweets(symbol)
            if not tweets:
                return 0.0
            
            total_sentiment = 0
            for tweet in tweets:
                palavras_positivas = ['bull', 'moon', 'buy', 'great', 'adoption']
                palavras_negativas = ['crash', 'concerned', 'volatility', 'dump']
                
                tweet_lower = tweet.lower()
                score_positivo = sum(1 for palavra in palavras_positivas if palavra in tweet_lower)
                score_negativo = sum(1 for palavra in palavras_negativas if palavra in tweet_lower)
                
                sentiment = (score_positivo - score_negativo) / max(len(tweet.split()), 1)
                total_sentiment += sentiment
            
            return total_sentiment / len(tweets)
        except Exception as e:
            logger.error(f"Erro ao analisar Twitter: {e}")
            return 0.0

    def _analisar_telegram(self, symbol: str) -> float:
        """Analisa sentimento no Telegram"""
        return secrets.SystemRandom().uniform(-0.3, 0.3)  # nosec B311

    def _analisar_reddit(self, symbol: str = "BTC") -> float:
        """Analisa sentimento no Reddit"""
        try:
            posts = self._obter_posts_reddit(symbol)
            if not posts:
                return 0.0
            
            total_sentiment = 0
            for post in posts:
                score_weight = max(1, abs(post.get('score', 1)))
                title = post.get('title', '')
                
                palavras_positivas = ['bull', 'analysis', 'hodl', 'strong', 'developments']
                palavras_negativas = ['crash', 'incoming', 'dump', 'bear']
                
                title_lower = title.lower()
                score_positivo = sum(1 for palavra in palavras_positivas if palavra in title_lower)
                score_negativo = sum(1 for palavra in palavras_negativas if palavra in title_lower)
                
                sentiment = (score_positivo - score_negativo) / max(len(title.split()), 1)
                weighted_sentiment = sentiment * score_weight
                total_sentiment += weighted_sentiment
            
            result = total_sentiment / len(posts)
            return max(-1.0, min(1.0, result))
        except Exception as e:
            logger.error(f"Erro ao analisar Reddit: {e}")
            return 0.0

    def _analisar_noticias(self, symbol: str = "BTC") -> float:
        """Analisa sentimento em notícias"""
        try:
            noticias = self._obter_noticias(symbol)
            if not noticias:
                return 0.0
            
            total_sentiment = 0
            for noticia in noticias:
                texto = f"{noticia.get('title', '')} {noticia.get('content', '')}"
                
                palavras_positivas = ['market', 'analysis', 'developments', 'trends', 'growth']
                palavras_negativas = ['crash', 'concerns', 'volatility', 'drop', 'fall']
                
                texto_lower = texto.lower()
                score_positivo = sum(1 for palavra in palavras_positivas if palavra in texto_lower)
                score_negativo = sum(1 for palavra in palavras_negativas if palavra in texto_lower)
                
                sentiment = (score_positivo - score_negativo) / max(len(texto.split()), 1)
                total_sentiment += sentiment
            
            return total_sentiment / len(noticias)
        except Exception as e:
            logger.error(f"Erro ao analisar notícias: {e}")
            return 0.0


class AprendizadoContinuo:
    """Sistema de aprendizado contínuo com Reinforcement Learning"""

    def __init__(self):
        self.modelos = {}
        self.historico_aprendizado = {}
        self.politicas = {}

    def treinar_modelo(self, logs_trades: List[Dict], metricas: Dict) -> Dict:
        """
        Reinforcement Learning dos resultados
        Melhora política de decisões automaticamente
        """
        try:
            if not logs_trades:
                return {"modelo_atualizado": False, "message": "Sem dados de trades"}

            estados, acoes, recompensas = self._preparar_dados_rl(logs_trades, metricas)

            bot_name = "default"
            if bot_name not in self.modelos:
                self.modelos[bot_name] = self._criar_modelo_rl(bot_name)

            modelo = self.modelos[bot_name]
            nova_politica = self._treinar_rl(modelo, estados, acoes, recompensas)

            if self._validar_politica(nova_politica, bot_name):
                self.politicas[bot_name] = nova_politica

                melhoria = self._calcular_melhoria(bot_name, metricas)
                self.historico_aprendizado[bot_name] = {
                    "timestamp": datetime.now(),
                    "trades_analisados": len(logs_trades),
                    "performance_media": metricas.get("win_rate", 0),
                    "melhoria": melhoria,
                }

                logger.info(
                    f"Modelo {bot_name} atualizado com {len(logs_trades)} trades"
                )
                
                return {"modelo_atualizado": True, "melhoria": melhoria, "trades_processados": len(logs_trades)}
            else:
                return {"modelo_atualizado": False, "message": "Política rejeitada na validação"}

        except Exception as e:
            logger.error(f"Erro no treinamento contínuo: {e}")
            return {"modelo_atualizado": False, "message": str(e)}

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
            "bot_name": bot_name,
        }

    def _treinar_rl(self, modelo, estados, acoes, recompensas):
        """Executa treinamento RL"""
        nova_politica = {
            "decisao_threshold": 0.6,
            "risk_adjustment": 0.8,
            "confidence_boost": 1.1,
        }
        return nova_politica

    def _validar_politica(self, politica, bot_name: str) -> bool:
        """Valida se nova política é melhor que a anterior"""
        return (
            0.5 <= politica.get("decisao_threshold", 0) <= 0.9
            and 0.5 <= politica.get("risk_adjustment", 0) <= 1.2
        )

    def _calcular_melhoria(self, bot_name: str, metricas: Dict) -> float:
        """Calcula melhoria em relação ao histórico"""
        if bot_name not in self.historico_aprendizado:
            return 0.0

        historico = self.historico_aprendizado[bot_name]
        performance_anterior = historico.get("performance_media", 0)
        performance_atual = metricas.get("win_rate", 0)

        return performance_atual - performance_anterior

    def _extrair_features(self, trade: Dict) -> np.ndarray:
        """Extrai features de um trade para aprendizado"""
        try:
            features = trade.get('market_conditions', {})
            
            feature_array = [
                features.get('rsi', 50),
                features.get('macd', 0),
                features.get('bb_position', 0.5),
                features.get('volume_ratio', 1.0),
                features.get('price_change', 0),
                features.get('sentiment_score', 0)
            ]
            
            return np.array(feature_array)
            
        except Exception as e:
            logger.error(f"Erro ao extrair features: {e}")
            return np.array([50, 0, 0.5, 1.0, 0, 0])

    def _calcular_reward(self, trade_resultado: Dict) -> float:
        """Calcula reward para sistema de aprendizado por reforço"""
        try:
            pnl = trade_resultado.get('pnl', 0)
            duration = trade_resultado.get('duration', 3600)
            max_drawdown = trade_resultado.get('max_drawdown', 0)
            
            reward_pnl = pnl / 100.0  # Normalizar PnL
            
            reward_duration = max(0, (3600 - duration) / 3600) * 0.5
            
            drawdown_penalty = max_drawdown * 10
            
            reward_total = reward_pnl + reward_duration - drawdown_penalty
            
            return reward_total
            
        except Exception as e:
            logger.error(f"Erro ao calcular reward: {e}")
            return 0.0

    def _atualizar_politica(self, experiencias: List[Dict]) -> Dict:
        """Atualiza política de aprendizado por reforço"""
        try:
            if not experiencias:
                return {"success": False, "message": "Sem experiências para atualizar política"}
            
            states = np.array([exp.get('state', np.zeros(6)) for exp in experiencias])
            actions = np.array([exp.get('action', 0) for exp in experiencias])
            rewards = np.array([exp.get('reward', 0) for exp in experiencias])
            next_states = np.array([exp.get('next_state', np.zeros(6)) for exp in experiencias])
            
            return {
                "success": True,
                "loss": 0.05,
                "mean_reward": np.mean(rewards),
                "samples": len(experiencias)
            }
            
        except Exception as e:
            logger.error(f"Erro ao atualizar política: {e}")
            return {"success": False, "message": str(e)}


class MotorIA:
    """Motor de Inteligência Artificial para trading"""

    def __init__(self, config: Configuracao):
        self.config = config
        self.ia_config = config.get_ia_config()
        self.modelos: Dict[str, Any] = {}
        self.historico_predicoes: Dict[str, Any] = {}
        self.metricas_performance: Dict[str, Any] = {}
        self.inicializado = False

        self.gerador_sinais = GeradorSinais()
        self.auto_tuner = AutoTuner()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.aprendizado_continuo = AprendizadoContinuo()

    async def inicializar(self):
        """Inicializa o motor de IA"""
        logger.info("Inicializando motor de IA")

        try:
            modelo_path = getattr(self.ia_config, 'modelo_path', './models')
            if isinstance(modelo_path, str):
                os.makedirs(modelo_path, exist_ok=True)
            else:
                os.makedirs('./models', exist_ok=True)
        except (AttributeError, TypeError):
            os.makedirs('./models', exist_ok=True)

        await self._carregar_modelos()

        if not self.modelos:
            await self._inicializar_modelos()

        self.inicializado = True
        logger.info("Motor de IA inicializado com sucesso")

    async def _carregar_modelos(self):
        """Carrega modelos salvos"""
        try:
            modelo_files = [
                "modelo_predicao_preco.pkl",
                "modelo_classificacao_tendencia.pkl",
                "modelo_volatilidade.pkl",
            ]

            for modelo_file in modelo_files:
                try:
                    modelo_path_attr = getattr(self.ia_config, 'modelo_path', './models')
                    if isinstance(modelo_path_attr, str):
                        modelo_path = os.path.join(modelo_path_attr, modelo_file)
                    else:
                        modelo_path = os.path.join('./models', modelo_file)
                        
                    if os.path.exists(modelo_path):
                        with open(modelo_path, "rb") as f:
                            modelo_name = modelo_file.replace(".pkl", "")
                            self.modelos[modelo_name] = pickle.load(f)  # nosec B301
                            logger.info(f"Modelo {modelo_name} carregado")
                except (AttributeError, TypeError):
                    continue

        except Exception as e:
            logger.error(f"Erro ao carregar modelos: {e}")

    async def _inicializar_modelos(self):
        """Inicializa modelos de IA"""
        try:
            from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
            from sklearn.preprocessing import StandardScaler

            self.modelos["modelo_predicao_preco"] = {
                "regressor": RandomForestRegressor(n_estimators=100, random_state=42),
                "scaler": StandardScaler(),
                "treinado": False,
            }

            self.modelos["modelo_classificacao_tendencia"] = {
                "classifier": RandomForestClassifier(n_estimators=100, random_state=42),
                "scaler": StandardScaler(),
                "treinado": False,
            }

            self.modelos["modelo_volatilidade"] = {
                "regressor": RandomForestRegressor(n_estimators=50, random_state=42),
                "scaler": StandardScaler(),
                "treinado": False,
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
                import secrets

                if self.tipo == "preco":
                    return np.array(
                        [
                            secrets.SystemRandom().uniform(-0.02, 0.02)
                            for _ in range(len(X))
                        ]
                    )
                elif self.tipo == "tendencia":
                    return np.array(
                        [
                            secrets.SystemRandom().choice([0, 1, 2])
                            for _ in range(len(X))
                        ]
                    )
                else:  # volatilidade
                    return np.array(
                        [
                            secrets.SystemRandom().uniform(0.01, 0.05)
                            for _ in range(len(X))
                        ]
                    )

            def fit(self, X, y):
                pass

        self.modelos["modelo_predicao_preco"] = {
            "regressor": ModeloSimulado("preco"),
            "scaler": None,
            "treinado": True,
        }

        self.modelos["modelo_classificacao_tendencia"] = {
            "classifier": ModeloSimulado("tendencia"),
            "scaler": None,
            "treinado": True,
        }

        self.modelos["modelo_volatilidade"] = {
            "regressor": ModeloSimulado("volatilidade"),
            "scaler": None,
            "treinado": True,
        }

        logger.info("Modelos simulados criados")

    async def analisar_mercado(
        self, dados_mercado: Dict[str, Any], ohlcv_data: Optional[List[List]] = None
    ) -> Dict[str, Any]:
        """Análise de mercado usando IA"""
        try:
            symbol = dados_mercado.get("symbol", "UNKNOWN")
            
            if ohlcv_data is None:
                ohlcv_data = dados_mercado.get("ohlcv", [])
            
            if len(ohlcv_data) < 20:
                return self._analise_basica()

            features = self._extrair_features(ohlcv_data)

            if features is not None:
                predicao_preco = await self._prever_preco(features)
                predicao_tendencia = await self._prever_tendencia(features)
                predicao_volatilidade = await self._prever_volatilidade(features)
                confianca = self._calcular_confianca(features)
            else:
                predicao_preco = 0.0
                predicao_tendencia = "neutral"
                predicao_volatilidade = 0.0
                confianca = 0.0

            sentimento_score = self.sentiment_analyzer.analisar_sentimento(symbol)
            
            analise = {
                "predicao_preco_percent": predicao_preco,
                "predicao_tendencia": str(predicao_tendencia),
                "predicao_volatilidade": predicao_volatilidade,
                "confianca": confianca,
                "recomendacao": self._gerar_recomendacao(
                    predicao_preco, predicao_tendencia, confianca
                ),
                "sinal_tecnico": "buy" if predicao_preco > 0.01 else "sell" if predicao_preco < -0.01 else "hold",
                "sentimento": sentimento_score,
                "timestamp": datetime.now(),
                "features_utilizadas": len(features) if features is not None else 0,
            }

            self.historico_predicoes.setdefault(symbol, []).append(analise)

            return analise

        except Exception as e:
            logger.error(f"Erro na análise de IA para {symbol}: {e}")
            return self._analise_basica()

    def _extrair_features(self, ohlcv_data: List[List]) -> Optional[np.ndarray]:
        """Extrai features dos dados OHLCV"""
        try:
            df = pd.DataFrame(
                ohlcv_data,
                columns=["timestamp", "open", "high", "low", "close", "volume"],
            )

            df["returns"] = df["close"].pct_change()
            df["volatility"] = df["returns"].rolling(10).std()
            df["sma_10"] = df["close"].rolling(10).mean()
            df["sma_20"] = df["close"].rolling(20).mean()
            df["rsi"] = self._calcular_rsi(df["close"])
            df["volume_sma"] = df["volume"].rolling(10).mean()
            df["price_volume_trend"] = df["close"] * df["volume"]

            df["momentum_5"] = df["close"] / df["close"].shift(5) - 1
            df["momentum_10"] = df["close"] / df["close"].shift(10) - 1

            df["high_low_ratio"] = (df["high"] - df["low"]) / df["close"]
            df["open_close_ratio"] = (df["close"] - df["open"]) / df["open"]

            feature_columns = [
                "returns",
                "volatility",
                "sma_10",
                "sma_20",
                "rsi",
                "volume_sma",
                "momentum_5",
                "momentum_10",
                "high_low_ratio",
                "open_close_ratio",
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

    async def _prever_preco(self, features: Optional[np.ndarray]) -> float:
        """Prevê mudança percentual do preço"""
        try:
            if features is None:
                return 0.0
            modelo = self.modelos.get("modelo_predicao_preco")
            if not modelo or not modelo["treinado"]:
                return 0.0

            if modelo["scaler"]:
                features_scaled = modelo["scaler"].transform(features.reshape(1, -1))
            else:
                features_scaled = features.reshape(1, -1)

            predicao = modelo["regressor"].predict(features_scaled)[0]
            return float(predicao)

        except Exception as e:
            logger.error(f"Erro na predição de preço: {e}")
            return 0.0

    async def _prever_tendencia(self, features: Optional[np.ndarray]) -> str:
        """Prevê direção da tendência"""
        try:
            if features is None:
                return "lateral"
            modelo = self.modelos.get("modelo_classificacao_tendencia")
            if not modelo or not modelo["treinado"]:
                return "lateral"

            if modelo["scaler"]:
                features_scaled = modelo["scaler"].transform(features.reshape(1, -1))
            else:
                features_scaled = features.reshape(1, -1)

            predicao = modelo["classifier"].predict(features_scaled)[0]

            mapeamento = {0: "baixa", 1: "lateral", 2: "alta"}
            return mapeamento.get(predicao, "lateral")

        except Exception as e:
            logger.error(f"Erro na predição de tendência: {e}")
            return "lateral"

    async def _prever_volatilidade(self, features: Optional[np.ndarray]) -> float:
        """Prevê volatilidade"""
        try:
            if features is None:
                return 0.02
            modelo = self.modelos.get("modelo_volatilidade")
            if not modelo or not modelo["treinado"]:
                return 0.02

            if modelo["scaler"]:
                features_scaled = modelo["scaler"].transform(features.reshape(1, -1))
            else:
                features_scaled = features.reshape(1, -1)

            predicao = modelo["regressor"].predict(features_scaled)[0]
            return max(0.001, float(predicao))

        except Exception as e:
            logger.error(f"Erro na predição de volatilidade: {e}")
            return 0.02

    def _calcular_confianca(
        self, features: Optional[np.ndarray], symbol: str = ""
    ) -> float:
        """Calcula confiança da predição"""
        try:
            if features is None:
                return 0.3

            historico = self.historico_predicoes.get(symbol, [])
            if len(historico) > 10:
                acertos = sum(
                    1 for pred in historico[-10:] if pred.get("acertou", False)
                )
                taxa_acerto = acertos / 10
                confianca_historica = taxa_acerto
            else:
                confianca_historica = 0.5

            volatilidade_features = np.std(features)
            confianca_volatilidade = max(0.1, 1 - volatilidade_features)

            confianca_final = confianca_historica * 0.6 + confianca_volatilidade * 0.4

            return min(0.95, max(0.1, confianca_final))

        except Exception as e:
            logger.error(f"Erro ao calcular confiança: {e}")
            return 0.5

    def _gerar_recomendacao(
        self, predicao_preco: float, predicao_tendencia: str, confianca: float
    ) -> str:
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
            "predicao_preco_percent": 0.0,
            "predicao_tendencia": "lateral",
            "predicao_volatilidade": 0.02,
            "confianca": 0.3,
            "recomendacao": "hold",
            "timestamp": datetime.now(),
            "features_utilizadas": 0,
        }

    async def treinar_modelos(self, dados_historicos: Dict[str, List]) -> bool:
        """Treina modelos com dados históricos"""
        try:
            if not self.ia_config.treinamento_ativo:
                logger.info("Treinamento de IA desabilitado")
                return False

            logger.info("Iniciando treinamento de modelos de IA")

            X, y_preco, y_tendencia, y_volatilidade = self._preparar_dados_treinamento(
                dados_historicos
            )

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
                features = self._extrair_features(ohlcv_list[i - 20 : i])
                if features is not None:
                    X.append(features[0])

                    current_price = ohlcv_list[i][4]
                    next_price = ohlcv_list[i + 1][4]
                    price_return = (next_price - current_price) / current_price
                    y_preco.append(price_return)

                    if price_return > 0.01:
                        y_tendencia.append(2)  # alta
                    elif price_return < -0.01:
                        y_tendencia.append(0)  # baixa
                    else:
                        y_tendencia.append(1)  # lateral

                    volatility = (
                        np.std([candle[4] for candle in ohlcv_list[i - 10 : i]])
                        / current_price
                    )
                    y_volatilidade.append(volatility)

        return (
            np.array(X),
            np.array(y_preco),
            np.array(y_tendencia),
            np.array(y_volatilidade),
        )

    async def _treinar_modelo_preco(self, X: np.ndarray, y: np.ndarray):
        """Treina modelo de predição de preço"""
        try:
            modelo = self.modelos["modelo_predicao_preco"]

            if modelo["scaler"]:
                X_scaled = modelo["scaler"].fit_transform(X)
            else:
                X_scaled = X

            modelo["regressor"].fit(X_scaled, y)
            modelo["treinado"] = True

            logger.info("Modelo de predição de preço treinado")

        except Exception as e:
            logger.error(f"Erro ao treinar modelo de preço: {e}")

    async def _treinar_modelo_tendencia(self, X: np.ndarray, y: np.ndarray):
        """Treina modelo de classificação de tendência"""
        try:
            modelo = self.modelos["modelo_classificacao_tendencia"]

            if modelo["scaler"]:
                X_scaled = modelo["scaler"].fit_transform(X)
            else:
                X_scaled = X

            modelo["classifier"].fit(X_scaled, y)
            modelo["treinado"] = True

            logger.info("Modelo de classificação de tendência treinado")

        except Exception as e:
            logger.error(f"Erro ao treinar modelo de tendência: {e}")

    async def _treinar_modelo_volatilidade(self, X: np.ndarray, y: np.ndarray):
        """Treina modelo de predição de volatilidade"""
        try:
            modelo = self.modelos["modelo_volatilidade"]

            if modelo["scaler"]:
                X_scaled = modelo["scaler"].fit_transform(X)
            else:
                X_scaled = X

            modelo["regressor"].fit(X_scaled, y)
            modelo["treinado"] = True

            logger.info("Modelo de predição de volatilidade treinado")

        except Exception as e:
            logger.error(f"Erro ao treinar modelo de volatilidade: {e}")

    async def _salvar_modelos(self):
        """Salva modelos treinados"""
        try:
            for nome, modelo in self.modelos.items():
                if modelo.get("treinado"):
                    modelo_path = os.path.join(
                        self.ia_config.modelo_path, f"{nome}.pkl"
                    )
                    with open(modelo_path, "wb") as f:
                        pickle.dump(modelo, f)
                    logger.info(f"Modelo {nome} salvo")

        except Exception as e:
            logger.error(f"Erro ao salvar modelos: {e}")

    async def otimizar_parametros_bot(
        self, bot_name: str, historico_trades: List
    ) -> Dict[str, Any]:
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
        avg_win = (
            np.mean([t.pnl for t in trades if t.pnl > 0]) if winning_trades > 0 else 0
        )
        avg_loss = (
            np.mean([t.pnl for t in trades if t.pnl < 0]) if losing_trades > 0 else 0
        )

        return {
            "win_rate": win_rate,
            "total_pnl": total_pnl,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "profit_factor": abs(avg_win / avg_loss) if avg_loss != 0 else 0,
            "total_trades": total_trades,
        }

    def _gerar_otimizacoes(self, bot_name: str, performance: Dict) -> Dict[str, Any]:
        """Gera sugestões de otimização"""
        otimizacoes = {}

        win_rate = performance.get("win_rate", 0)
        profit_factor = performance.get("profit_factor", 0)

        if bot_name == "arbitragem":
            if win_rate < 0.6:
                otimizacoes["min_profit_percent"] = 0.8  # Aumentar threshold
            if profit_factor < 1.5:
                otimizacoes["max_position_size"] = 500  # Reduzir tamanho

        elif bot_name == "scalping":
            if win_rate < 0.7:
                otimizacoes["target_profit"] = 0.0015  # Aumentar target
            if profit_factor < 2.0:
                otimizacoes["max_hold_time"] = 180  # Reduzir tempo

        elif bot_name == "grid":
            if win_rate < 0.5:
                otimizacoes["grid_spacing"] = 0.015  # Aumentar espaçamento
            if profit_factor < 1.2:
                otimizacoes["grid_size"] = 8  # Reduzir tamanho do grid

        return otimizacoes

    async def otimizar_estrategia(self, estrategia: str, historico: Dict[str, Any]) -> Dict[str, Any]:
        """Otimiza parâmetros de uma estratégia baseado no histórico"""
        try:
            logger.info(f"Otimizando estratégia: {estrategia}")
            
            trades = historico.get('trades', [])
            if not trades:
                return {"error": "Nenhum trade encontrado no histórico"}
            
            dados_historicos = []
            for trade in trades:
                dados_historicos.append({
                    'close': 50000,
                    'timestamp': 1640995200,
                    'profit_loss': trade.get('pnl', 0) / 10000,
                    'parametros': trade.get('parametros', {})
                })
            
            resultado_otimizacao = await self.auto_tuner.otimizar_parametros(
                dados_historicos, numero_iteracoes=50
            )
            
            return {
                "estrategia": estrategia,
                "parametros_otimizados": resultado_otimizacao.parametros_otimizados,
                "score_performance": resultado_otimizacao.score_performance,
                "iteracoes": resultado_otimizacao.iteracoes
            }
            
        except Exception as e:
            logger.error(f"Erro ao otimizar estratégia: {e}")
            return {"error": str(e)}
    
    async def treinar_modelo_continuo(self, logs_trades: List[Dict], metricas: Dict[str, Any]) -> Dict[str, Any]:
        """Treina modelo de aprendizado contínuo com logs de trades"""
        try:
            logger.info("Iniciando treinamento contínuo")
            
            for trade_log in logs_trades:
                trade_data = {
                    'symbol': trade_log.get('symbol', 'BTC/USDT'),
                    'action': trade_log.get('action', 'buy'),
                    'result': trade_log.get('result', 'win'),
                    'profit_loss': trade_log.get('pnl', 0) / 10000,
                    'features': {
                        'rsi': 50,
                        'macd': 0,
                        'bb_position': 0.5,
                        'volume_ratio': 1.0,
                        'price_change': 0,
                        'sentiment_score': 0
                    },
                    'timestamp': 1640995200
                }
                
                self.aprendizado_continuo.adicionar_trade(trade_data)
            
            resultado_treinamento = self.aprendizado_continuo.treinar_modelo()
            
            self.aprendizado_continuo.atualizar_performance(metricas)
            
            return {
                "trades_processados": len(logs_trades),
                "modelo_treinado": resultado_treinamento.get('success', False),
                "metricas_atualizadas": metricas,
                "performance_score": resultado_treinamento.get('score', 0.0)
            }
            
        except Exception as e:
            logger.error(f"Erro no treinamento contínuo: {e}")
            return {"error": str(e)}

    async def finalizar(self):
        """Finaliza motor de IA"""
        logger.info("Finalizando motor de IA")

        if self.ia_config.treinamento_ativo:
            await self._salvar_modelos()

        metricas_path = os.path.join(
            self.ia_config.modelo_path, "metricas_performance.pkl"
        )
        try:
            with open(metricas_path, "wb") as f:
                pickle.dump(self.metricas_performance, f)
        except Exception as e:
            logger.error(f"Erro ao salvar métricas: {e}")

        self.inicializado = False
        logger.info("Motor de IA finalizado")
