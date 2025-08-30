import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import logging
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Sinal:
    tipo: str  # 'buy', 'sell', 'hold'
    forca: float  # 0.0 a 1.0
    preco_entrada: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    razao: str = ""


class GeradorSinais:
    """Gerador de sinais de trading baseado em análise técnica"""

    def __init__(self):
        self.indicadores = {}
        self.historical_data = {}
        self.configuracao = {
            "rsi_oversold": 30,
            "rsi_overbought": 70,
            "macd_threshold": 0.001,
            "bb_extreme": 0.1,
            "volume_threshold": 1.5,
        }
        self.config = self.configuracao
        self.cache_indicadores = {}
        self.pesos = {
            "rsi": 0.3,
            "macd": 0.3,
            "bb": 0.4,
        }  # Para compatibilidade com testes

    def calcular_indicadores_basicos(
        self, precos: List[float], volumes: List[float]
    ) -> Dict:
        """Calcula indicadores técnicos básicos"""
        try:
            if not precos or len(precos) < 20:
                return {
                    "sma": precos[-1] if precos else 0,
                    "ema": precos[-1] if precos else 0,
                    "rsi": 50.0,
                    "macd": 0.0,
                    "macd_signal": 0.0,
                    "bb_upper": precos[-1] * 1.02 if precos else 0,
                    "bb_middle": precos[-1] if precos else 0,
                    "bb_lower": precos[-1] * 0.98 if precos else 0,
                    "volume_atual": volumes[-1] if volumes else 100,
                    "volume_avg": np.mean(volumes) if volumes else 100,
                    "volume_ratio": 1.0,
                }

            indicadores = {}

            indicadores["sma"] = self.calcular_sma(precos, 20)
            indicadores["ema"] = self.calcular_ema(precos, 20)

            indicadores["rsi"] = self.calcular_rsi(precos)
            macd, signal = self.calcular_macd(precos)
            indicadores["macd"] = macd
            indicadores["macd_signal"] = signal
            indicadores["macd_histogram"] = macd - signal

            # Volatilidade
            bb = self.calcular_bandas_bollinger(precos)
            indicadores["bb_upper"] = bb["upper"]
            indicadores["bb_middle"] = bb["middle"]
            indicadores["bb_lower"] = bb["lower"]
            indicadores["bb_position"] = bb["position"]

            if volumes and len(volumes) >= 20:
                indicadores["volume_atual"] = volumes[-1]
                indicadores["volume_avg"] = float(np.mean(volumes[-20:]))
                indicadores["volume_ratio"] = float(
                    volumes[-1] / np.mean(volumes[-20:])
                )
            else:
                indicadores["volume_atual"] = volumes[-1] if volumes else 100
                indicadores["volume_avg"] = (
                    float(np.mean(volumes)) if volumes else 100.0
                )
                indicadores["volume_ratio"] = 1.0

            return indicadores

        except Exception as e:
            logging.error(f"Erro ao calcular indicadores: {e}")
            return {}

    def calcular_rsi(self, precos: List[float], periodo: int = 14) -> float:
        """Calcula RSI (Relative Strength Index)"""
        return self._calcular_rsi(precos, periodo)

    def _calcular_rsi(self, precos: List[float], periodo: int = 14) -> float:
        """Calcula RSI (Relative Strength Index)"""
        try:
            if len(precos) < periodo + 1:
                return 50.0

            deltas = np.diff(precos)
            ganhos = np.where(deltas > 0, deltas, 0)
            perdas = np.where(deltas < 0, -deltas, 0)

            media_ganhos = np.mean(ganhos[-periodo:])
            media_perdas = np.mean(perdas[-periodo:])

            if media_perdas == 0:
                return 100.0

            rs = media_ganhos / media_perdas
            rsi = 100 - (100 / (1 + rs))

            return float(rsi)

        except Exception as e:
            logging.error(f"Erro no cálculo RSI: {e}")
            return 50.0

    def calcular_macd(
        self, precos: List[float], fast: int = 12, slow: int = 26, signal: int = 9
    ) -> Tuple[float, float]:
        """Calcula MACD (Moving Average Convergence Divergence)"""
        return self._calcular_macd(precos, fast, slow, signal)

    def _calcular_macd(
        self, precos: List[float], fast: int = 12, slow: int = 26, signal: int = 9
    ) -> Tuple[float, float]:
        """Calcula MACD (Moving Average Convergence Divergence)"""
        try:
            if len(precos) < slow:
                return 0.0, 0.0

            precos_array = np.array(precos)

            ema_fast = self._calcular_ema(precos, fast)
            ema_slow = self._calcular_ema(precos, slow)

            macd_line = ema_fast - ema_slow
            signal_line = self._calcular_ema(precos[-len(precos) :], signal)

            return macd_line, signal_line

        except Exception as e:
            logging.error(f"Erro no cálculo MACD: {e}")
            return 0.0, 0.0

    def calcular_ema(self, precos: List[float], periodo: int = 20) -> float:
        """Calcula EMA (Exponential Moving Average)"""
        try:
            if len(precos) < periodo:
                return precos[-1] if precos else 0.0

            alpha = 2 / (periodo + 1)
            ema = precos[-periodo]

            for i in range(-periodo + 1, 0):
                ema = alpha * precos[i] + (1 - alpha) * ema

            return float(ema)

        except Exception as e:
            logging.error(f"Erro no cálculo EMA: {e}")
            return precos[-1] if precos else 0.0

    def _calcular_ema(self, precos: List[float], periodo: int) -> float:
        """Calcula EMA (Exponential Moving Average) - método privado"""
        return self.calcular_ema(precos, periodo)

    def calcular_sma(self, precos: List[float], periodo: int = 20) -> float:
        """Calcula SMA (Simple Moving Average)"""
        try:
            if len(precos) < periodo:
                return precos[-1] if precos else 0.0

            return float(np.mean(precos[-periodo:]))

        except Exception as e:
            logging.error(f"Erro no cálculo SMA: {e}")
            return precos[-1] if precos else 0.0

    def _calcular_sma(self, precos: List[float], periodo: int) -> float:
        """Calcula SMA (Simple Moving Average) - método privado"""
        return self.calcular_sma(precos, periodo)

    def calcular_bandas_bollinger(
        self, precos: List[float], periodo: int = 20, desvios: float = 2
    ) -> Dict:
        """Calcula Bandas de Bollinger"""
        try:
            if len(precos) < periodo:
                preco_atual = precos[-1] if precos else 0
                return {
                    "upper": preco_atual * 1.02,
                    "middle": preco_atual,
                    "lower": preco_atual * 0.98,
                    "position": 0.5,
                }

            precos_periodo = precos[-periodo:]
            media = np.mean(precos_periodo)
            desvio = np.std(precos_periodo)

            upper = media + (desvios * desvio)
            lower = media - (desvios * desvio)

            preco_atual = precos[-1]
            position = (
                (preco_atual - lower) / (upper - lower) if upper != lower else 0.5
            )

            return {
                "upper": upper,
                "middle": media,
                "lower": lower,
                "position": max(0.0, min(1.0, float(position))),
            }

        except Exception as e:
            logging.error(f"Erro no cálculo Bandas Bollinger: {e}")
            return {"upper": 0, "middle": 0, "lower": 0, "position": 0.5}

    def analisar_mercado_completo(self, symbol: str, dados_mercado: Dict) -> Dict:
        """Análise completa do mercado incluindo todos os indicadores"""
        try:
            precos = dados_mercado.get("precos", [])
            volumes = dados_mercado.get("volumes", [])

            if not precos or len(precos) < 20:
                return {
                    "symbol": symbol,
                    "indicadores": {},
                    "sinal": {"tipo": "hold", "forca": 0.0},
                    "confianca": 0.0,
                }

            # Calcular todos os indicadores
            indicadores = self.calcular_indicadores_basicos(precos, volumes)

            # Gerar sinal baseado nos indicadores
            sinal = self.gerar_sinal(symbol, dados_mercado)

            # Calcular confiança baseada na convergência dos indicadores
            confianca = self._calcular_confianca_sinais(indicadores)

            return {
                "symbol": symbol,
                "indicadores": indicadores,
                "sinal": {
                    "tipo": sinal.tipo,
                    "forca": sinal.forca,
                    "preco_entrada": sinal.preco_entrada,
                    "stop_loss": sinal.stop_loss,
                    "take_profit": sinal.take_profit,
                    "razao": sinal.razao,
                },
                "confianca": confianca,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logging.error(f"Erro na análise completa do mercado: {e}")
            return {
                "symbol": symbol,
                "indicadores": {},
                "sinal": {"tipo": "hold", "forca": 0.0},
                "confianca": 0.0,
                "erro": str(e),
            }

    def _calcular_confianca_sinais(self, indicadores: Dict) -> float:
        """Calcula confiança baseada na convergência dos indicadores"""
        try:
            if not indicadores:
                return 0.0

            sinais_compra = 0
            sinais_venda = 0
            total_indicadores = 0

            rsi = indicadores.get("rsi", 50)
            if rsi < 30:
                sinais_compra += 1
            elif rsi > 70:
                sinais_venda += 1
            total_indicadores += 1

            macd = indicadores.get("macd", 0)
            macd_signal = indicadores.get("macd_signal", 0)
            if macd > macd_signal:
                sinais_compra += 1
            elif macd < macd_signal:
                sinais_venda += 1
            total_indicadores += 1

            bb_position = indicadores.get("bb_position", 0.5)
            if bb_position < 0.2:
                sinais_compra += 1
            elif bb_position > 0.8:
                sinais_venda += 1
            total_indicadores += 1

            # Calcular confiança baseada na convergência
            if sinais_compra > sinais_venda:
                confianca = sinais_compra / total_indicadores
            elif sinais_venda > sinais_compra:
                confianca = sinais_venda / total_indicadores
            else:
                confianca = 0.0

            return min(confianca, 1.0)

        except Exception as e:
            logging.error(f"Erro ao calcular confiança: {e}")
            return 0.0

    def gerar_sinal(self, symbol: str, dados_mercado: Dict) -> Sinal:
        """Gera sinal de trading baseado em análise técnica"""
        try:
            precos = dados_mercado.get("precos", [])
            volumes = dados_mercado.get("volumes", [])
            preco_atual = precos[-1] if precos else 0

            if not precos or len(precos) < 20:
                return Sinal("hold", 0.0, preco_atual, razao="Dados insuficientes")

            rsi = self.calcular_rsi(precos)
            macd, signal = self.calcular_macd(precos)
            bb = self.calcular_bandas_bollinger(precos)
            volume_ratio = (
                volumes[-1] / np.mean(volumes[-20:])
                if volumes and len(volumes) >= 20
                else 1.0
            )

            sinais_compra = 0.0
            sinais_venda = 0.0
            forca_total = 0.0

            if rsi < self.configuracao["rsi_oversold"]:
                sinais_compra += 1
                forca_total += (
                    self.configuracao["rsi_oversold"] - rsi
                ) / self.configuracao["rsi_oversold"]
            elif rsi > self.configuracao["rsi_overbought"]:
                sinais_venda += 1
                forca_total += (rsi - self.configuracao["rsi_overbought"]) / (
                    100 - self.configuracao["rsi_overbought"]
                )

            if macd > signal:
                sinais_compra += 1
                forca_total += float(min(abs(macd - signal) * 1000, 1.0))
            elif macd < signal:
                sinais_venda += 1
                forca_total += float(min(abs(macd - signal) * 1000, 1.0))

            if bb["position"] < self.configuracao["bb_extreme"]:
                sinais_compra += 1
                forca_total += (
                    self.configuracao["bb_extreme"] - bb["position"]
                ) / self.configuracao["bb_extreme"]
            elif bb["position"] > (1 - self.configuracao["bb_extreme"]):
                sinais_venda += 1
                forca_total += (
                    bb["position"] - (1 - self.configuracao["bb_extreme"])
                ) / self.configuracao["bb_extreme"]

            volume_boost = min(
                volume_ratio / self.configuracao["volume_threshold"], 2.0
            )

            if sinais_compra > sinais_venda and sinais_compra >= 2:
                tipo = "buy"
                forca = min((forca_total / 3) * volume_boost, 1.0)
                stop_loss = preco_atual * 0.98
                take_profit = preco_atual * 1.04
                razao = f"RSI:{rsi:.1f}, MACD:{macd:.4f}, BB:{bb['position']:.2f}"

            elif sinais_venda > sinais_compra and sinais_venda >= 2:
                tipo = "sell"
                forca = min((forca_total / 3) * volume_boost, 1.0)
                stop_loss = preco_atual * 1.02
                take_profit = preco_atual * 0.96
                razao = f"RSI:{rsi:.1f}, MACD:{macd:.4f}, BB:{bb['position']:.2f}"

            else:
                tipo = "hold"
                forca = 0.0
                stop_loss = None
                take_profit = None
                razao = f"Sinais conflitantes ou fracos. RSI:{rsi:.1f}"

            return Sinal(
                tipo=tipo,
                forca=forca,
                preco_entrada=preco_atual,
                stop_loss=stop_loss,
                take_profit=take_profit,
                razao=razao,
            )

        except Exception as e:
            logging.error(f"Erro ao gerar sinal: {e}")
            return Sinal("hold", 0.0, 0.0, razao=f"Erro: {str(e)}")

    def analisar_mercado(self, dados_market: Dict) -> Any:
        """Analisa mercado e gera sinal de trading (método para testes)"""
        try:
            ohlcv = dados_market.get("ohlcv", [])
            symbol = dados_market.get("symbol", "BTC/USDT")

            if not ohlcv or len(ohlcv) < 20:

                from dataclasses import dataclass

                @dataclass
                class MockSinalInsuficiente:
                    acao: str = "parar"
                    confidence: float = 0.0
                    preco_entrada: float = 0.0
                    razao: str = "Dados insuficientes"
                    tipo: str = "parar"
                    forca: float = 0.0

                return MockSinalInsuficiente()

            precos = [candle[4] for candle in ohlcv]  # Close price
            volumes = [candle[5] for candle in ohlcv]  # Volume

            # Calcular indicadores
            indicadores = self._calcular_indicadores_tecnicos(precos)

            sinais_individuais = []

            rsi = indicadores.get("rsi", 50)
            if rsi < 30:
                sinais_individuais.append(
                    {"acao": "comprar", "confidence": (30 - rsi) / 30}
                )
            elif rsi > 70:
                sinais_individuais.append(
                    {"acao": "vender", "confidence": (rsi - 70) / 30}
                )
            else:
                sinais_individuais.append({"acao": "parar", "confidence": 0.1})

            macd = indicadores.get("macd", 0)
            if macd > 0:
                sinais_individuais.append(
                    {"acao": "comprar", "confidence": min(abs(macd) * 100, 1.0)}
                )
            elif macd < 0:
                sinais_individuais.append(
                    {"acao": "vender", "confidence": min(abs(macd) * 100, 1.0)}
                )
            else:
                sinais_individuais.append({"acao": "parar", "confidence": 0.1})

            sinal_final = self._combinar_sinais(sinais_individuais)

            preco_atual = precos[-1]

            from dataclasses import dataclass

            @dataclass
            class MockSinalFinal:
                acao: str = sinal_final["acao"]
                confidence: float = sinal_final["confidence"]
                preco_entrada: float = preco_atual
                stop_loss: float = (
                    preco_atual * 0.98
                    if sinal_final["acao"] == "comprar"
                    else preco_atual * 1.02
                )
                take_profit: float = (
                    preco_atual * 1.04
                    if sinal_final["acao"] == "comprar"
                    else preco_atual * 0.96
                )
                razao: str = f"RSI:{rsi:.1f}, MACD:{macd:.4f}"
                tipo: str = sinal_final["acao"]
                forca: float = sinal_final["confidence"]

            return MockSinalFinal()

        except Exception as e:
            logging.error(f"Erro ao analisar mercado: {e}")

            from dataclasses import dataclass

            @dataclass
            class MockSinalErro:
                acao: str = "parar"
                confidence: float = 0.0
                preco_entrada: float = 0.0
                razao: str = f"Erro: {str(e)}"
                tipo: str = "parar"
                forca: float = 0.0

            return MockSinalErro()

    def _calcular_indicadores_tecnicos(self, precos: List[float]) -> Dict:
        """Calcula indicadores técnicos (método privado para testes)"""
        try:
            if len(precos) < 20:
                return {
                    "sma": precos[-1] if precos else 0,
                    "ema": precos[-1] if precos else 0,
                    "rsi": 50.0,
                    "macd": 0.0,
                    "macd_signal": 0.0,
                    "bb_upper": precos[-1] * 1.02 if precos else 0,
                    "bb_middle": precos[-1] if precos else 0,
                    "bb_lower": precos[-1] * 0.98 if precos else 0,
                    "volume_ratio": 1.0,
                }

            indicadores = {}

            indicadores["sma_20"] = float(np.mean(precos[-20:]))

            indicadores["rsi"] = float(self.calcular_rsi(precos))

            indicadores["macd"] = float(self.calcular_macd(precos)[0])

            bb_result = self.calcular_bandas_bollinger(precos)
            indicadores["bb_upper"] = bb_result.get("upper", 0.0)
            indicadores["bb_middle"] = bb_result.get("middle", 0.0)
            indicadores["bb_lower"] = bb_result.get("lower", 0.0)
            indicadores["bb_position"] = bb_result.get("position", 0.5)

            return indicadores

        except Exception as e:
            logging.error(f"Erro ao calcular indicadores: {e}")
            return {}

    def _combinar_sinais(self, sinais_individuais: List[Dict]) -> Dict:
        """Combina múltiplos sinais em um sinal final (método privado para testes)"""
        try:
            if not sinais_individuais:
                return {"acao": "parar", "confidence": 0.0}

            votos = {"comprar": 0, "vender": 0, "parar": 0}
            confidence_total = {"comprar": 0, "vender": 0, "parar": 0}

            for sinal in sinais_individuais:
                acao = sinal["acao"]
                confidence = sinal["confidence"]

                votos[acao] += 1
                confidence_total[acao] += confidence

            acao_vencedora = max(votos.keys(), key=lambda k: votos[k])

            if votos[acao_vencedora] > 0:
                confidence_media = (
                    confidence_total[acao_vencedora] / votos[acao_vencedora]
                )
            else:
                confidence_media = 0.0

            return {"acao": acao_vencedora, "confidence": min(confidence_media, 1.0)}

        except Exception as e:
            logging.error(f"Erro ao combinar sinais: {e}")
            return {"acao": "parar", "confidence": 0.0}

    def atualizar_configuracao(self, nova_config: Dict) -> None:
        """Atualiza configuração dos indicadores"""
        try:
            self.configuracao.update(nova_config)
            logging.info(f"Configuração atualizada: {self.configuracao}")
        except Exception as e:
            logging.error(f"Erro ao atualizar configuração: {e}")
