"""
Circuit Breaker pattern para exchanges
"""

import time
import logging
from typing import Callable, Any, Optional
from enum import Enum
import asyncio

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreakerOpenException(Exception):
    """Exceção quando circuit breaker está aberto"""

    pass


class CircuitBreaker:
    """Circuit Breaker para proteger chamadas a exchanges"""

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        expected_exception: type = Exception,
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = CircuitState.CLOSED
        self.success_count = 0

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Executa função protegida pelo circuit breaker"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
                logger.info("Circuit breaker mudou para HALF_OPEN")
            else:
                time_remaining = (
                    self.timeout - (time.time() - (self.last_failure_time or 0))
                    if self.last_failure_time
                    else 0
                )
                raise CircuitBreakerOpenException(
                    f"Circuit breaker está OPEN. Próxima tentativa em "
                    f"{time_remaining:.1f}s"
                )

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result

        except Exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        """Verifica se deve tentar resetar o circuit breaker"""
        if self.last_failure_time is None:
            return False
        return (time.time() - self.last_failure_time) >= self.timeout

    def _on_success(self):
        """Chamado quando operação é bem-sucedida"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= 3:
                self._reset()
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0

    def _on_failure(self):
        """Chamado quando operação falha"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker ABERTO após {self.failure_count} falhas")
        elif self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            logger.warning("Circuit breaker voltou para OPEN durante HALF_OPEN")

    def _reset(self):
        """Reseta circuit breaker para estado fechado"""
        self.failure_count = 0
        self.success_count = 0
        self.state = CircuitState.CLOSED
        logger.info("Circuit breaker RESETADO para CLOSED")

    def get_state(self) -> dict:
        """Retorna estado atual do circuit breaker"""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time,
            "time_until_retry": (
                max(0, self.timeout - (time.time() - self.last_failure_time))
                if self.last_failure_time is not None
                else 0
            ),
        }


class ExchangeCircuitBreakers:
    """Gerenciador de circuit breakers para múltiplas exchanges"""

    def __init__(self):
        self.breakers: dict[str, CircuitBreaker] = {}

    def get_breaker(self, exchange: str) -> CircuitBreaker:
        """Obtém circuit breaker para exchange específica"""
        if exchange not in self.breakers:
            self.breakers[exchange] = CircuitBreaker(
                failure_threshold=5, timeout=60, expected_exception=Exception
            )
        return self.breakers[exchange]

    async def call_with_breaker(
        self, exchange: str, func: Callable, *args, **kwargs
    ) -> Any:
        """Executa função com circuit breaker da exchange"""
        breaker = self.get_breaker(exchange)
        return await breaker.call(func, *args, **kwargs)

    def get_all_states(self) -> dict:
        """Retorna estado de todos os circuit breakers"""
        return {
            exchange: breaker.get_state() for exchange, breaker in self.breakers.items()
        }
