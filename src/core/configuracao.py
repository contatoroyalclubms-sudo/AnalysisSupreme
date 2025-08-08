"""
Sistema de configuração centralizada
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ConfigExchange:
    """Configuração de exchange"""
    nome: str
    api_key: str
    api_secret: str
    sandbox: bool = True
    passphrase: Optional[str] = None

@dataclass
class ConfigBot:
    """Configuração de bot"""
    nome: str
    ativo: bool
    parametros: Dict[str, Any]
    casos_uso: Dict[int, Dict[str, Any]]

@dataclass
class ConfigIA:
    """Configuração da IA"""
    modelo_path: str
    treinamento_ativo: bool
    intervalo_retreino: int
    parametros: Dict[str, Any]

@dataclass
class ConfigObservabilidade:
    """Configuração de observabilidade"""
    prometheus_port: int
    grafana_url: str
    grafana_api_key: str
    metricas_ativas: bool

class Configuracao:
    """Gerenciador de configuração do sistema"""
    
    def __init__(self, config_path: str = "config/config.json"):
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self._carregar_configuracao()
    
    def _carregar_configuracao(self):
        """Carrega configuração do arquivo"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
            else:
                logger.warning(f"Arquivo de configuração não encontrado: {self.config_path}")
                self._config = self._configuracao_padrao()
            
            self._aplicar_env_vars()
            
        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {e}")
            self._config = self._configuracao_padrao()
    
    def _configuracao_padrao(self) -> Dict[str, Any]:
        """Retorna configuração padrão"""
        return {
            "geral": {
                "paper_mode": True,
                "max_concurrent_bots": 6,
                "risk_limit_percent": 2.0
            },
            "exchanges": {
                "binance": {
                    "api_key": "",
                    "api_secret": "",
                    "sandbox": True
                }
            },
            "bots": {
                "arbitragem": {
                    "ativo": True,
                    "parametros": {
                        "min_profit_percent": 0.5,
                        "max_position_size": 1000
                    },
                    "casos_uso": {
                        1: {"tipo": "simples", "exchanges": ["binance", "coinbase"]},
                        2: {"tipo": "triangular", "exchange": "binance"},
                        3: {"tipo": "funding", "exchange": "binance"}
                    }
                },
                "grid": {
                    "ativo": True,
                    "parametros": {
                        "grid_size": 10,
                        "grid_spacing": 0.01
                    },
                    "casos_uso": {
                        1: {"tipo": "fixo", "range_percent": 5},
                        2: {"tipo": "dinamico", "ajuste_auto": True},
                        3: {"tipo": "stop_loss", "stop_percent": 2}
                    }
                },
                "momentum": {
                    "ativo": True,
                    "parametros": {
                        "lookback_period": 20,
                        "momentum_threshold": 0.02
                    },
                    "casos_uso": {
                        1: {"tipo": "breakout", "volume_confirm": False},
                        2: {"tipo": "continuacao", "trend_confirm": True},
                        3: {"tipo": "volume", "volume_threshold": 1.5}
                    }
                },
                "scalping": {
                    "ativo": True,
                    "parametros": {
                        "target_profit": 0.001,
                        "max_hold_time": 300
                    },
                    "casos_uso": {
                        1: {"tipo": "spread", "min_spread": 0.0005},
                        2: {"tipo": "micro", "tick_size": 0.0001},
                        3: {"tipo": "orderbook", "depth_levels": 5}
                    }
                },
                "mean_reversion": {
                    "ativo": True,
                    "parametros": {
                        "lookback_period": 50,
                        "deviation_threshold": 2.0
                    },
                    "casos_uso": {
                        1: {"tipo": "simples", "media_type": "sma"},
                        2: {"tipo": "bollinger", "std_dev": 2},
                        3: {"tipo": "rsi_divergence", "rsi_period": 14}
                    }
                },
                "swing": {
                    "ativo": True,
                    "parametros": {
                        "swing_period": 100,
                        "min_swing_size": 0.05
                    },
                    "casos_uso": {
                        1: {"tipo": "suporte_resistencia", "levels": 5},
                        2: {"tipo": "candlestick", "patterns": ["doji", "hammer"]},
                        3: {"tipo": "fibonacci", "retracement_levels": [0.382, 0.618]}
                    }
                }
            },
            "ia": {
                "modelo_path": "models/",
                "treinamento_ativo": True,
                "intervalo_retreino": 24,
                "parametros": {
                    "features": ["price", "volume", "volatility"],
                    "lookback_window": 100,
                    "prediction_horizon": 10
                }
            },
            "observabilidade": {
                "prometheus_port": 8000,
                "grafana_url": "http://localhost:3000",
                "grafana_api_key": "",
                "metricas_ativas": True
            }
        }
    
    def _aplicar_env_vars(self):
        """Aplica variáveis de ambiente sobre a configuração"""
        env_mappings = {
            "PAPER_MODE": ("geral", "paper_mode"),
            "BINANCE_API_KEY": ("exchanges", "binance", "api_key"),
            "BINANCE_API_SECRET": ("exchanges", "binance", "api_secret"),
            "PROMETHEUS_PORT": ("observabilidade", "prometheus_port"),
        }
        
        for env_var, config_path in env_mappings.items():
            value = os.getenv(env_var)
            if value:
                self._set_nested_config(config_path, value)
    
    def _set_nested_config(self, path: tuple, value: Any):
        """Define valor em configuração aninhada"""
        config = self._config
        for key in path[:-1]:
            config = config.setdefault(key, {})
        
        if isinstance(config.get(path[-1]), bool):
            value = value.lower() in ('true', '1', 'yes')
        elif isinstance(config.get(path[-1]), int):
            value = int(value)
        elif isinstance(config.get(path[-1]), float):
            value = float(value)
        
        config[path[-1]] = value
    
    def get(self, *path: str, default: Any = None) -> Any:
        """Obtém valor da configuração"""
        config = self._config
        try:
            for key in path:
                config = config[key]
            return config
        except KeyError:
            return default
    
    def get_exchange_config(self, exchange: str) -> Optional[ConfigExchange]:
        """Obtém configuração de exchange"""
        config = self.get("exchanges", exchange)
        if not config:
            return None
        
        return ConfigExchange(
            nome=exchange,
            api_key=config.get("api_key", ""),
            api_secret=config.get("api_secret", ""),
            sandbox=config.get("sandbox", True),
            passphrase=config.get("passphrase")
        )
    
    def get_bot_config(self, bot: str) -> Optional[ConfigBot]:
        """Obtém configuração de bot"""
        config = self.get("bots", bot)
        if not config:
            return None
        
        return ConfigBot(
            nome=bot,
            ativo=config.get("ativo", True),
            parametros=config.get("parametros", {}),
            casos_uso=config.get("casos_uso", {})
        )
    
    def get_ia_config(self) -> ConfigIA:
        """Obtém configuração da IA"""
        config = self.get("ia", default={})
        
        return ConfigIA(
            modelo_path=config.get("modelo_path", "models/"),
            treinamento_ativo=config.get("treinamento_ativo", True),
            intervalo_retreino=config.get("intervalo_retreino", 24),
            parametros=config.get("parametros", {})
        )
    
    def get_observabilidade_config(self) -> ConfigObservabilidade:
        """Obtém configuração de observabilidade"""
        config = self.get("observabilidade", default={})
        
        return ConfigObservabilidade(
            prometheus_port=config.get("prometheus_port", 8000),
            grafana_url=config.get("grafana_url", ""),
            grafana_api_key=config.get("grafana_api_key", ""),
            metricas_ativas=config.get("metricas_ativas", True)
        )
    
    @property
    def paper_mode(self) -> bool:
        """Retorna se está em modo paper"""
        return self.get("geral", "paper_mode", default=True)
    
    @property
    def max_concurrent_bots(self) -> int:
        """Retorna número máximo de bots concorrentes"""
        return self.get("geral", "max_concurrent_bots", default=6)
    
    @property
    def risk_limit_percent(self) -> float:
        """Retorna limite de risco em percentual"""
        return self.get("geral", "risk_limit_percent", default=2.0)
    
    def get_cache_config(self) -> Dict[str, Any]:
        """Retorna configuração do sistema de cache"""
        return {
            'redis_url': os.getenv('REDIS_URL', 'redis://localhost:6379'),
            'l1_max_size_mb': 512,
            'l2_max_size_mb': 2048,
            'sqlite_path': 'cache_l3.db',
            'prediction_window': 30,
            'learning_enabled': True
        }
