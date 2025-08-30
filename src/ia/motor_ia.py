"""
Motor de IA Avançado para CryptoBot Supremo Global
Sistema completo de análise de mercado e tomada de decisões
"""

import asyncio
import logging
import pandas as pd
import numpy as np
import secrets
import os
import pickle  # nosec B403
import random
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class Configuracao:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


@dataclass
class DecisaoTrading:
    """Decisão de trading do Motor IA"""

    acao: str  # 'comprar', 'vender', 'aguardar'
    confianca: float  # 0.0 a 1.0
    preco_entrada: float
    quantidade: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    justificativa: str = ""
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class AnaliseCompleta:
    """Análise completa do mercado"""

    symbol: str
    timestamp: datetime
    analise_tecnica: Dict[str, Any]
    analise_sentimento: Dict[str, Any]
    analise_ml: Dict[str, Any]
    analise_risco: Dict[str, Any]
    condicoes_mercado: Dict[str, Any]
    recomendacao_final: str
    confianca_geral: float


class MotorIA:
    """Motor de IA Avançado para análise de mercado e tomada de decisões"""

    def __init__(self, configuracao: Optional[Dict] = None):
        self.configuracao = configuracao or {}
        self.config = self.configuracao  # Add config attribute for compatibility
        self.sentiment_analyzer: Optional[Any] = None
        self.aprendizado_continuo: Optional[Any] = None
        self.gerador_sinais: Optional[Any] = None
        self.auto_tuner: Optional[Any] = None  # Para compatibilidade com testes
        self.posicoes_ativas: Dict[str, Any] = {}
        self.historico_decisoes: List[Dict[str, Any]] = []
        self.performance_metrics: Dict[str, Any] = {}
        self.is_running = False
        self.inicializado = False

        self._inicializar_componentes()

    def _inicializar_componentes(self) -> None:
        """Inicializa todos os componentes de IA"""
        try:
            from .sentiment_analyzer import SentimentAnalyzer
            from .aprendizado_continuo import AprendizadoContinuo
            from .gerador_sinais import GeradorSinais
            from ..optimization.autotuner import AutoTuner

            self.sentiment_analyzer = SentimentAnalyzer()
            self.aprendizado_continuo = AprendizadoContinuo()
            self.gerador_sinais = GeradorSinais()
            self.auto_tuner = AutoTuner()

            self.inicializado = True
            logger.info("Componentes IA inicializados com sucesso")

        except Exception as e:
            logger.error(f"Erro ao inicializar componentes IA: {e}")
            self.sentiment_analyzer = type(
                "MockSentimentAnalyzer",
                (),
                {"analisar_sentimento": lambda self, symbol: 0.0},
            )()
            self.aprendizado_continuo = type(
                "MockAprendizadoContinuo",
                (),
                {"prever_resultado": lambda self, features: 0.0},
            )()
            self.gerador_sinais = type(
                "MockGeradorSinais",
                (),
                {
                    "gerar_sinal": lambda self, symbol, dados: {
                        "tipo": "hold",
                        "forca": 0.0,
                    }
                },
            )()
            self.inicializado = True

    async def inicializar(self):
        """Método de inicialização para compatibilidade"""
        try:
            if not self.inicializado:
                self._inicializar_componentes()
            return True
        except Exception as e:
            logger.error(f"Erro na inicialização: {e}")
            return False

    async def analisar_mercado(
        self, dados_mercado: Dict[str, Any], symbol: Optional[str] = None
    ) -> Dict[str, Any]:
        """Análise completa do mercado para um símbolo com cache e paralelização"""
        try:
            timestamp = datetime.now()

            if not self._validar_dados_entrada(dados_mercado):
                return self._get_default_analysis(symbol, timestamp)

            ohlcv = dados_mercado.get("ohlcv", [])
            if len(ohlcv) < 20:
                return self._get_default_analysis(symbol, timestamp)

            if not hasattr(self, "cache"):
                from ..cache.redis_cache import RedisCache

                config_dict = {}
                if hasattr(self, "configuracao") and self.configuracao:
                    if hasattr(self.configuracao, "__dict__"):
                        config_dict = self.configuracao.__dict__
                    elif isinstance(self.configuracao, dict):
                        config_dict = self.configuracao
                self.cache = RedisCache(config_dict)
                await self.cache.initialize()

            tasks = [
                self.cache.get_cached_or_compute(
                    f"analise_tecnica_{symbol}_{timestamp.strftime('%Y%m%d_%H%M')}",
                    self._analise_tecnica,
                    symbol,
                    dados_mercado,
                    data_type="signals",
                ),
                self.cache.get_cached_or_compute(
                    f"analise_sentimento_{symbol}_{timestamp.strftime('%Y%m%d_%H')}",
                    self._analise_sentimento,
                    symbol,
                    data_type="sentiment",
                ),
                self.cache.get_cached_or_compute(
                    f"analise_ml_{symbol}_{timestamp.strftime('%Y%m%d_%H%M')}",
                    self._analise_ml,
                    symbol,
                    dados_mercado,
                    data_type="ml_predictions",
                ),
            ]

            analise_tecnica, analise_sentimento, analise_ml = await asyncio.gather(
                *tasks
            )

            analise_risco = self._analise_risco(symbol, dados_mercado)
            condicoes_mercado = self._analise_condicoes_mercado(dados_mercado)

            analise_consolidada = self._consolidar_analise(
                analise_tecnica,
                analise_sentimento,
                analise_ml,
                analise_risco,
                condicoes_mercado,
            )

            recomendacao_final = self._determinar_recomendacao_final(
                analise_consolidada
            )

            return {
                "symbol": symbol,
                "timestamp": timestamp.isoformat(),
                "analise_tecnica": analise_tecnica,
                "analise_sentimento": analise_sentimento,
                "analise_ml": analise_ml,
                "analise_risco": analise_risco,
                "condicoes_mercado": condicoes_mercado,
                "recomendacao_final": recomendacao_final["acao"],
                "confianca_geral": recomendacao_final["confianca"],
                "sinal": recomendacao_final["acao"],
                "sentiment": analise_sentimento.get("score", 0.0),
                "cached": True,  # Indicador de que usou cache
            }

        except Exception as e:
            logger.error(f"Erro na análise de mercado para {symbol}: {e}")
            return self._get_default_analysis(symbol, timestamp)

    def _get_default_analysis(
        self, symbol: Optional[str], timestamp: datetime
    ) -> Dict[str, Any]:
        """Retorna análise padrão em caso de erro"""
        return {
            "symbol": symbol or "UNKNOWN",
            "timestamp": timestamp.isoformat(),
            "analise_tecnica": {},
            "analise_sentimento": {},
            "analise_ml": {},
            "analise_risco": {},
            "condicoes_mercado": {},
            "recomendacao_final": "aguardar",
            "confianca_geral": 0.0,
            "sinal": "aguardar",
            "sentiment": 0.0,
            "cached": False,
        }

    async def executar_decisao(self, symbol: str, analise: Dict) -> bool:
        """Executa uma decisão de trading baseada na análise"""
        try:
            if analise.get("recomendacao_final") == "aguardar":
                return True

            decisao = self._gerar_decisao_trading(symbol, analise)

            if not self._validar_decisao(decisao):
                logger.warning(f"Decisão inválida para {symbol}: {decisao}")
                return False

            sucesso = await self._executar_ordem(decisao)

            if sucesso:
                self._atualizar_portfolio(decisao)

                self._registrar_para_aprendizado(decisao, analise)

                self._atualizar_metricas(decisao)

                logger.info(f"Decisão executada com sucesso: {decisao.acao} {symbol}")
                return True
            else:
                logger.error(f"Falha ao executar decisão para {symbol}")
                return False

        except Exception as e:
            logger.error(f"Erro ao executar decisão para {symbol}: {e}")
            return False

    async def otimizar_estrategia(
        self, symbol: str, dados_historicos: List[Dict], iteracoes: int = 50
    ) -> Dict:
        """Otimiza estratégia de trading usando AutoTuner"""
        try:
            from ..optimization.autotuner import AutoTuner

            autotuner = AutoTuner()

            resultado = await autotuner.otimizar_parametros(dados_historicos, iteracoes)

            return {
                "symbol": symbol,
                "parametros_otimos": resultado.parametros_otimizados,
                "sharpe_ratio": resultado.score_performance,
                "iteracoes": resultado.iteracoes,
                "tempo_otimizacao": resultado.tempo_execucao,
            }

        except Exception as e:
            logger.error(f"Erro na otimização para {symbol}: {e}")
            return {
                "symbol": symbol,
                "parametros_otimos": {},
                "sharpe_ratio": 0.0,
                "iteracoes": 0,
                "tempo_otimizacao": 0.0,
            }

    async def treinar_modelo_continuo(
        self,
        logs_trades: List[Dict[str, Any]],
        metricas: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Treina modelo de aprendizado contínuo"""
        try:
            if not self.aprendizado_continuo:
                return False

            try:
                resultado = True
                if hasattr(self.aprendizado_continuo, "treinar_modelo"):
                    try:
                        treinar_func = getattr(
                            self.aprendizado_continuo, "treinar_modelo", None
                        )
                        if treinar_func:
                            resultado = await treinar_func(logs_trades, metricas)
                    except (AttributeError, TypeError):
                        resultado = True
            except (AttributeError, TypeError):
                resultado = True

            return True

        except Exception as e:
            logger.error(f"Erro no treinamento contínuo: {e}")
            return False

    async def _analise_tecnica(
        self, symbol: Optional[str], dados_mercado: Dict
    ) -> Dict[str, Any]:
        """Análise técnica usando gerador de sinais"""
        try:
            if not self.gerador_sinais:
                return {"erro": "Gerador de sinais não disponível"}

            try:
                if hasattr(self.gerador_sinais, "gerar_sinal"):
                    gerar_func = getattr(self.gerador_sinais, "gerar_sinal", None)
                    if gerar_func:
                        sinal = gerar_func(symbol or "BTC", dados_mercado)
                    else:
                        sinal = type(
                            "MockSinal",
                            (),
                            {
                                "tipo": "hold",
                                "forca": 0.0,
                                "indicadores": {},
                                "stop_loss": None,
                                "take_profit": None,
                            },
                        )()
                else:
                    sinal = type(
                        "MockSinal",
                        (),
                        {
                            "tipo": "hold",
                            "forca": 0.0,
                            "indicadores": {},
                            "stop_loss": None,
                            "take_profit": None,
                        },
                    )()
            except (AttributeError, TypeError):
                sinal = type(
                    "MockSinal",
                    (),
                    {
                        "tipo": "hold",
                        "forca": 0.0,
                        "indicadores": {},
                        "stop_loss": None,
                        "take_profit": None,
                    },
                )()

            return {
                "sinal": getattr(sinal, "tipo", "hold"),
                "forca": getattr(sinal, "forca", 0.0),
                "confianca_tecnica": getattr(sinal, "forca", 0.0),
                "indicadores": getattr(sinal, "indicadores", {}),
                "preco_entrada": dados_mercado.get("preco_atual", 0.0),
                "stop_loss": getattr(sinal, "stop_loss", None),
                "take_profit": getattr(sinal, "take_profit", None),
            }

        except Exception as e:
            logger.error(f"Erro na análise técnica: {e}")
            return {"erro": str(e), "sinal": "hold", "forca": 0.0}

    async def _analise_sentimento(self, symbol: Optional[str]) -> Dict[str, Any]:
        """Análise de sentimento do mercado"""
        try:
            if not self.sentiment_analyzer:
                return {"erro": "Analisador de sentimento não disponível"}

            try:
                score = 0.0
                if hasattr(self.sentiment_analyzer, "analisar_sentimento"):
                    try:
                        analisar_func = getattr(
                            self.sentiment_analyzer, "analisar_sentimento", None
                        )
                        if analisar_func:
                            score_result = analisar_func(symbol or "BTC")
                            if hasattr(score_result, "__await__"):
                                score_result = await score_result
                            try:
                                score = (
                                    float(score_result)
                                    if score_result is not None
                                    else 0.0
                                )
                            except (ValueError, TypeError):
                                score = 0.0
                    except (AttributeError, TypeError):
                        score = 0.0
            except (AttributeError, TypeError):
                score = 0.0

            return {
                "score": score,
                "classificacao": (
                    "positivo"
                    if score > 0.1
                    else "negativo" if score < -0.1 else "neutro"
                ),
                "confianca_sentimento": abs(score),
            }

        except Exception as e:
            logger.error(f"Erro na análise de sentimento: {e}")
            return {"erro": str(e), "score": 0.0, "classificacao": "neutro"}

    async def _analise_ml(
        self, symbol: Optional[str], dados_mercado: Dict
    ) -> Dict[str, Any]:
        """Análise usando machine learning"""
        try:
            if not self.aprendizado_continuo:
                return {"erro": "Sistema ML não disponível"}

            features = self._extrair_features_ml(dados_mercado)

            try:
                predicao = 0.0
                if hasattr(self.aprendizado_continuo, "prever_resultado"):
                    try:
                        prever_func = getattr(
                            self.aprendizado_continuo, "prever_resultado", None
                        )
                        if prever_func:
                            predicao_result = prever_func(features)
                            predicao = (
                                float(predicao_result)
                                if predicao_result is not None
                                else 0.0
                            )
                    except (AttributeError, TypeError, ValueError):
                        predicao = 0.0
            except (AttributeError, TypeError):
                predicao = 0.0

            return {
                "predicao": predicao,
                "probabilidade_sucesso": max(0, min(1, (predicao + 1) / 2)),
                "confianca_ml": abs(predicao),
            }

        except Exception as e:
            logger.error(f"Erro na análise ML: {e}")
            return {"erro": str(e), "predicao": 0.0, "probabilidade_sucesso": 0.5}

    def _analise_risco(
        self, symbol: Optional[str], dados_mercado: Dict
    ) -> Dict[str, Any]:
        """Análise de risco do trade"""
        try:
            preco_atual = dados_mercado.get("preco_atual", 0)
            if not preco_atual:
                return self._risco_default(symbol or "BTC")

            precos = dados_mercado.get("precos", [])
            if len(precos) < 20:
                return self._risco_default(symbol or "BTC")

            returns = [precos[i] / precos[i - 1] - 1 for i in range(1, len(precos))]
            volatilidade = np.std(returns) * np.sqrt(252)  # Anualizada

            var_95 = np.percentile(returns, 5)

            if volatilidade > 0.5:
                categoria = "ALTO"
                score = 0.8
            elif volatilidade > 0.3:
                categoria = "MEDIO"
                score = 0.5
            else:
                categoria = "BAIXO"
                score = 0.2

            return {
                "categoria_risco": categoria,
                "score_risco": score,
                "volatilidade": volatilidade,
                "var_95": var_95,
                "max_perda_esperada": abs(var_95) * preco_atual,
            }

        except Exception as e:
            logger.error(f"Erro na análise de risco: {e}")
            return self._risco_default(symbol or "BTC")

    def _risco_default(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Retorna análise de risco padrão"""
        return {
            "symbol": symbol or "UNKNOWN",
            "categoria_risco": "MEDIO",
            "score_risco": 0.5,
            "volatilidade": 0.3,
            "var_95": -0.05,
            "max_perda_esperada": 0.0,
        }

    def _analise_condicoes_mercado(self, dados_mercado: Dict) -> Dict[str, Any]:
        """Análise das condições gerais do mercado"""
        try:
            volumes = dados_mercado.get("volumes", [])
            volume_atual = volumes[-1] if volumes else 0
            volume_medio = (
                np.mean(volumes[-20:]) if len(volumes) >= 20 else volume_atual
            )

            volume_ratio = volume_atual / volume_medio if volume_medio > 0 else 1.0

            precos = dados_mercado.get("precos", [])
            if len(precos) >= 20:
                sma_20 = np.mean(precos[-20:])
                sma_50 = np.mean(precos[-50:]) if len(precos) >= 50 else sma_20

                if precos[-1] > sma_20 > sma_50:
                    tendencia = "ALTA"
                    forca_tendencia = 0.8
                elif precos[-1] < sma_20 < sma_50:
                    tendencia = "BAIXA"
                    forca_tendencia = 0.8
                else:
                    tendencia = "LATERAL"
                    forca_tendencia = 0.3
            else:
                tendencia = "INDEFINIDA"
                forca_tendencia = 0.0

            regime = self._identificar_regime_mercado(dados_mercado)

            return {
                "tendencia": tendencia,
                "forca_tendencia": forca_tendencia,
                "volume_ratio": volume_ratio,
                "regime_mercado": regime,
                "liquidez": (
                    "ALTA"
                    if volume_ratio > 1.5
                    else "MEDIA" if volume_ratio > 0.8 else "BAIXA"
                ),
            }

        except Exception as e:
            logger.error(f"Erro na análise de condições de mercado: {e}")
            return {
                "tendencia": "INDEFINIDA",
                "forca_tendencia": 0.0,
                "volume_ratio": 1.0,
                "regime_mercado": "NORMAL",
                "liquidez": "MEDIA",
            }

    def _identificar_regime_mercado(self, dados_mercado: Dict) -> str:
        """Identifica o regime atual do mercado"""
        try:
            precos = dados_mercado.get("precos", [])
            if len(precos) < 50:
                return "NORMAL"

            returns_recentes = [precos[i] / precos[i - 1] - 1 for i in range(-10, 0)]
            returns_historicos = [
                precos[i] / precos[i - 1] - 1 for i in range(1, len(precos))
            ]

            vol_recente = np.std(returns_recentes)
            vol_historica = np.std(returns_historicos)

            if vol_recente > vol_historica * 2:
                return "ALTA_VOLATILIDADE"
            elif vol_recente < vol_historica * 0.5:
                return "BAIXA_VOLATILIDADE"
            else:
                return "NORMAL"

        except Exception as e:
            logger.error(f"Erro ao identificar regime de mercado: {e}")
            return "NORMAL"

    def _consolidar_analise(
        self,
        analise_tecnica: Dict,
        analise_sentimento: Dict,
        analise_ml: Dict,
        analise_risco: Dict,
        condicoes_mercado: Dict,
    ) -> Dict[str, Any]:
        """Consolida todas as análises em uma decisão unificada"""
        try:
            score_tecnico = self._converter_sinal_para_score(
                analise_tecnica.get("sinal", "hold")
            )
            score_sentimento = self._converter_sentimento_para_score(
                analise_sentimento.get("score", 0)
            )
            score_ml = analise_ml.get("predicao", 0)

            peso_tecnico = 0.4
            peso_sentimento = 0.2
            peso_ml = 0.3
            peso_risco = 0.1

            confianca_tecnica = analise_tecnica.get("confianca_tecnica", 0.5)
            confianca_sentimento = analise_sentimento.get("confianca_sentimento", 0.5)
            confianca_ml = analise_ml.get("confianca_ml", 0.5)

            score_consolidado = (
                score_tecnico * peso_tecnico * confianca_tecnica
                + score_sentimento * peso_sentimento * confianca_sentimento
                + score_ml * peso_ml * confianca_ml
            )

            fator_risco = 1.0 - (analise_risco.get("score_risco", 0.5) * peso_risco)
            score_final = score_consolidado * fator_risco

            return {
                "score_consolidado": score_final,
                "componentes": {
                    "tecnico": score_tecnico,
                    "sentimento": score_sentimento,
                    "ml": score_ml,
                    "risco": analise_risco.get("score_risco", 0.5),
                },
                "confiancas": {
                    "tecnica": confianca_tecnica,
                    "sentimento": confianca_sentimento,
                    "ml": confianca_ml,
                },
            }

        except Exception as e:
            logger.error(f"Erro ao consolidar análise: {e}")
            return {"score_consolidado": 0.0, "componentes": {}, "confiancas": {}}

    def _determinar_recomendacao_final(
        self, analise_consolidada: Dict
    ) -> Dict[str, Any]:
        """Determina a recomendação final baseada na análise consolidada"""
        try:
            score = analise_consolidada.get("score_consolidado", 0.0)

            threshold_compra = 0.3
            threshold_venda = -0.3

            if score > threshold_compra:
                acao = "comprar"
                confianca = min(score, 0.95)
            elif score < threshold_venda:
                acao = "vender"
                confianca = min(abs(score), 0.95)
            else:
                acao = "aguardar"
                confianca = 1.0 - abs(score)

            return {
                "acao": acao,
                "confianca": confianca,
                "score": score,
                "justificativa": f"Score consolidado: {score:.3f}",
            }

        except Exception as e:
            logger.error(f"Erro ao determinar recomendação: {e}")
            return {"acao": "aguardar", "confianca": 0.0, "score": 0.0}

    def _converter_sinal_para_score(self, sinal: str) -> float:
        """Converte sinal técnico para score numérico"""
        conversao = {
            "buy": 1.0,
            "sell": -1.0,
            "hold": 0.0,
            "comprar": 1.0,
            "vender": -1.0,
            "aguardar": 0.0,
        }
        return conversao.get(sinal.lower(), 0.0)

    def _converter_sentimento_para_score(self, score_sentimento: float) -> float:
        """Converte score de sentimento para escala padronizada"""
        return max(-1.0, min(1.0, score_sentimento))

    def _gerar_decisao_trading(self, symbol: str, analise: Dict) -> DecisaoTrading:
        """Gera decisão de trading baseada na análise"""
        try:
            acao = analise.get("recomendacao_final", "aguardar")
            confianca = analise.get("confianca_geral", 0.0)
            preco_entrada = analise.get("analise_tecnica", {}).get("preco_entrada", 0.0)

            quantidade = self._calcular_quantidade(symbol, preco_entrada, confianca)

            if acao == "comprar":
                stop_loss = preco_entrada * 0.98  # 2% stop loss
                take_profit = preco_entrada * 1.04  # 4% take profit
            elif acao == "vender":
                stop_loss = preco_entrada * 1.02
                take_profit = preco_entrada * 0.96
            else:
                stop_loss = None
                take_profit = None

            justificativa = self._gerar_justificativa(analise)

            return DecisaoTrading(
                acao=acao,
                confianca=confianca,
                preco_entrada=preco_entrada,
                quantidade=quantidade,
                stop_loss=stop_loss,
                take_profit=take_profit,
                justificativa=justificativa,
            )

        except Exception as e:
            logger.error(f"Erro ao gerar decisão de trading: {e}")
            return DecisaoTrading(
                acao="aguardar",
                confianca=0.0,
                preco_entrada=0.0,
                quantidade=0.0,
                justificativa=f"Erro: {str(e)}",
            )

    def _calcular_quantidade(
        self, symbol: str, preco_entrada: float, confianca: float
    ) -> float:
        """Calcula quantidade a ser negociada baseada no risco"""
        try:
            capital_disponivel = 10000.0

            risco_percentual = 0.01 + (confianca * 0.02)

            valor_risco = capital_disponivel * risco_percentual
            quantidade = valor_risco / preco_entrada if preco_entrada > 0 else 0.0

            return round(quantidade, 8)

        except Exception as e:
            logger.error(f"Erro ao calcular quantidade: {e}")
            return 0.0

    def _calcular_retorno_esperado(self, decisao: DecisaoTrading) -> float:
        """Calcula retorno esperado do trade"""
        try:
            if not decisao.take_profit or not decisao.preco_entrada:
                return 0.0

            if decisao.acao == "comprar":
                retorno = (
                    decisao.take_profit - decisao.preco_entrada
                ) / decisao.preco_entrada
            elif decisao.acao == "vender":
                retorno = (
                    decisao.preco_entrada - decisao.take_profit
                ) / decisao.preco_entrada
            else:
                retorno = 0.0

            return retorno * decisao.confianca

        except Exception as e:
            logger.error(f"Erro ao calcular retorno esperado: {e}")
            return 0.0

    def _gerar_justificativa(self, analise: Dict) -> str:
        """Gera justificativa textual para a decisão"""
        try:
            componentes = []

            analise_tecnica = analise.get("analise_tecnica", {})
            if analise_tecnica.get("sinal") != "hold":
                componentes.append(f"Técnica: {analise_tecnica.get('sinal')}")

            analise_sentimento = analise.get("analise_sentimento", {})
            sentimento = analise_sentimento.get("classificacao", "neutro")
            if sentimento != "neutro":
                componentes.append(f"Sentimento: {sentimento}")

            analise_ml = analise.get("analise_ml", {})
            if abs(analise_ml.get("predicao", 0)) > 0.1:
                componentes.append(f"ML: {analise_ml.get('predicao', 0):.2f}")

            analise_risco = analise.get("analise_risco", {})
            risco = analise_risco.get("categoria_risco", "MEDIO")
            componentes.append(f"Risco: {risco}")

            condicoes_mercado = analise.get("condicoes_mercado", {})
            tendencia = condicoes_mercado.get("tendencia", "INDEFINIDA")
            if tendencia != "INDEFINIDA":
                componentes.append(f"Tendência: {tendencia}")

            return " | ".join(componentes) if componentes else "Análise neutra"

        except Exception as e:
            logger.error(f"Erro ao gerar justificativa: {e}")
            return "Erro na análise"

    def _validar_decisao(self, decisao: DecisaoTrading) -> bool:
        """Valida se a decisão é executável"""
        try:
            if not decisao.acao or decisao.acao not in [
                "comprar",
                "vender",
                "aguardar",
            ]:
                return False

            if decisao.confianca < 0 or decisao.confianca > 1:
                return False

            if decisao.acao != "aguardar":
                if decisao.preco_entrada <= 0 or decisao.quantidade <= 0:
                    return False

            return True

        except Exception as e:
            logger.error(f"Erro na validação da decisão: {e}")
            return False

    async def _executar_ordem(self, decisao: DecisaoTrading) -> bool:
        """Executa ordem no mercado (mock)"""
        try:
            await asyncio.sleep(0.1)  # Simular latência

            sucesso = random.random() > 0.05  # nosec B311

            if sucesso:
                logger.info(
                    f"Ordem executada: {decisao.acao} {decisao.quantidade} @ {decisao.preco_entrada}"
                )
            else:
                logger.warning(f"Falha na execução da ordem: {decisao.acao}")

            return sucesso

        except Exception as e:
            logger.error(f"Erro ao executar ordem: {e}")
            return False

    def _atualizar_portfolio(self, decisao: DecisaoTrading) -> None:
        """Atualiza portfolio com nova posição"""
        try:
            if decisao.acao in ["comprar", "vender"]:
                self.posicoes_ativas[f"{decisao.timestamp}"] = {
                    "acao": decisao.acao,
                    "quantidade": decisao.quantidade,
                    "preco_entrada": decisao.preco_entrada,
                    "stop_loss": decisao.stop_loss,
                    "take_profit": decisao.take_profit,
                }

        except Exception as e:
            logger.error(f"Erro ao atualizar portfolio: {e}")

    def _registrar_para_aprendizado(
        self, decisao: DecisaoTrading, analise: Dict
    ) -> None:
        """Registra decisão para aprendizado contínuo"""
        try:
            if self.aprendizado_continuo:
                trade_data = {
                    "features": self._extrair_features_ml(
                        analise.get("analise_tecnica", {})
                    ),
                    "acao": decisao.acao,
                    "confianca": decisao.confianca,
                    "timestamp": decisao.timestamp,
                    "preco_entrada": decisao.preco_entrada,
                }

                try:
                    if hasattr(self.aprendizado_continuo, "adicionar_trade"):
                        try:
                            adicionar_func = getattr(
                                self.aprendizado_continuo, "adicionar_trade", None
                            )
                            if adicionar_func:
                                adicionar_func(trade_data)
                        except (AttributeError, TypeError):
                            pass
                except (AttributeError, TypeError):
                    pass

        except Exception as e:
            logger.error(f"Erro ao registrar para aprendizado: {e}")

    def _atualizar_metricas(self, decisao: DecisaoTrading) -> None:
        """Atualiza métricas de performance"""
        try:
            if "total_decisoes" not in self.performance_metrics:
                self.performance_metrics["total_decisoes"] = 0
                self.performance_metrics["total_comprar"] = 0.0
                self.performance_metrics["total_vender"] = 0.0
                self.performance_metrics["total_aguardar"] = 0.0

            self.performance_metrics["total_decisoes"] += 1
            if decisao.acao == "comprar":
                self.performance_metrics["total_comprar"] += 1.0
            elif decisao.acao == "vender":
                self.performance_metrics["total_vender"] += 1.0
            else:
                self.performance_metrics["total_aguardar"] += 1.0
            self.performance_metrics["ultima_atualizacao_timestamp"] = (
                datetime.now().timestamp()
            )

        except Exception as e:
            logger.error(f"Erro ao atualizar métricas: {e}")

    def _validar_dados_entrada(self, dados_mercado: Dict) -> bool:
        """Valida se os dados de entrada são suficientes"""
        try:
            if not dados_mercado:
                return False

            # Accept either ohlcv or preco_atual
            if "ohlcv" in dados_mercado:
                ohlcv = dados_mercado["ohlcv"]
                if not ohlcv or len(ohlcv) < 1:
                    return False
                return True

            if "preco_atual" in dados_mercado:
                preco = dados_mercado.get("preco_atual", 0)
                if not isinstance(preco, (int, float)) or preco <= 0:
                    return False
                return True

            return False

        except Exception as e:
            logger.error(f"Erro na validação de dados: {e}")
            return False

    def _extrair_features_ml(self, dados_mercado: Dict) -> Dict[str, float]:
        """Extrai features para machine learning"""
        try:
            features = {}

            features["preco_atual"] = dados_mercado.get("preco_atual", 0.0)

            if "indicadores" in dados_mercado:
                indicadores = dados_mercado["indicadores"]
                features["rsi"] = indicadores.get("rsi", 50.0)
                features["macd"] = indicadores.get("macd", 0.0)
                features["bb_position"] = indicadores.get("bb_position", 0.5)

            features["volume_ratio"] = dados_mercado.get("volume_ratio", 1.0)

            features["sentiment_score"] = dados_mercado.get("sentiment_score", 0.0)

            return features

        except Exception as e:
            logger.error(f"Erro ao extrair features ML: {e}")
            return {}

    def obter_status(self) -> Dict[str, Any]:
        """Retorna status atual do motor IA"""
        try:
            return {
                "inicializado": self.inicializado,
                "componentes": {
                    "sentiment_analyzer": self.sentiment_analyzer is not None,
                    "aprendizado_continuo": self.aprendizado_continuo is not None,
                    "gerador_sinais": self.gerador_sinais is not None,
                },
                "posicoes_ativas": len(self.posicoes_ativas),
                "historico_decisoes": len(self.historico_decisoes),
                "performance_metrics": self.performance_metrics,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Erro ao obter status: {e}")
            return {"erro": str(e)}

    async def treinar_modelos(self, dados_treinamento: Dict[str, Any]) -> bool:
        """Treina modelos de IA com dados fornecidos"""
        try:
            features = dados_treinamento.get("features", [])
            targets = dados_treinamento.get("targets", [])
            
            logs_trades = []
            for i, (feature, target) in enumerate(zip(features, targets)):
                logs_trades.append({
                    "features": feature,
                    "target": target,
                    "timestamp": datetime.now(),
                })
            
            return await self.treinar_modelo_continuo(logs_trades)
        except Exception as e:
            logger.error(f"Erro ao treinar modelos: {e}")
            return False

    async def otimizar_parametros_bot(self, bot_type: str, historico_trades: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Otimiza parâmetros para um tipo específico de bot"""
        try:
            symbol = "BTC/USDT"
            dados_historicos = []
            
            for trade in historico_trades:
                dados_historicos.append({
                    "symbol": trade.get("symbol", symbol),
                    "pnl": trade.get("pnl", 0),
                    "timestamp": datetime.now(),
                    "bot_type": bot_type,
                })
            
            resultado = await self.otimizar_estrategia(symbol, dados_historicos)
            return resultado
        except Exception as e:
            logger.error(f"Erro ao otimizar parâmetros do bot {bot_type}: {e}")
            return {
                "bot_type": bot_type,
                "parametros_otimos": {},
                "sharpe_ratio": 0.0,
                "iteracoes": 0,
            }

    async def finalizar(self) -> None:
        """Finaliza o motor de IA"""
        try:
            self.is_running = False
            
            if self.historico_decisoes:
                logger.info(f"Motor IA finalizado com {len(self.historico_decisoes)} decisões no histórico")
            
            self.posicoes_ativas.clear()
            self.performance_metrics.clear()
            
            logger.info("Motor IA finalizado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao finalizar motor IA: {e}")


# Legacy classes for backward compatibility
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
