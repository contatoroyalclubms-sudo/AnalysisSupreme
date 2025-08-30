"""
🏥 HEALTH CHECKER - Sistema de Verificação de Saúde
Monitora saúde dos serviços Railway em tempo real
Performance: Health monitoring | Service validation | Uptime tracking
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

import aiohttp


class HealthStatus(Enum):
    """Status de saúde"""
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"
    UNKNOWN = "UNKNOWN"


@dataclass
class HealthCheck:
    """Resultado de verificação de saúde"""
    service_id: str
    service_name: str
    status: HealthStatus
    response_time: float
    timestamp: datetime
    url: Optional[str] = None
    error_message: Optional[str] = None
    status_code: Optional[int] = None


class HealthChecker:
    """Sistema de verificação de saúde dos serviços"""

    def __init__(self, railway_token: str, project_id: str):
        self.railway_token = railway_token
        self.project_id = project_id
        self.api_base = "https://backboard.railway.com/graphql/v2"
        self.logger = logging.getLogger(__name__)
        
        self.check_interval = 60  # Verificar a cada 60 segundos
        self.timeout = 10  # Timeout de 10 segundos
        self.healthy_threshold = 2.0  # Resposta < 2s = saudável
        self.degraded_threshold = 5.0  # Resposta < 5s = degradado
        
        self.health_history: List[HealthCheck] = []
        self.service_urls: Dict[str, str] = {}
        self.uptime_stats: Dict[str, Dict] = {}

    async def initialize(self):
        """Inicializa o health checker"""
        self.logger.info("🏥 Inicializando Health Checker")
        
        await self._discover_service_urls()
        
        await self._initialize_uptime_stats()
        
        self.logger.info("✅ Health Checker inicializado")

    async def start_health_monitoring(self):
        """Inicia monitoramento contínuo de saúde"""
        self.logger.info("🔄 Iniciando monitoramento de saúde")
        
        while True:
            try:
                health_results = await self._check_all_services_health()
                
                await self._process_health_results(health_results)
                
                await self._update_uptime_stats(health_results)
                
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                self.logger.error(f"❌ Erro no monitoramento de saúde: {e}")
                await asyncio.sleep(self.check_interval)

    async def _discover_service_urls(self):
        """Descobre URLs dos serviços"""
        query = """
        query {
            project(id: "%s") {
                services {
                    edges {
                        node {
                            id
                            name
                            deployments(first: 1) {
                                edges {
                                    node {
                                        url
                                        staticUrl
                                        status
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        """ % self.project_id
        
        try:
            result = await self._execute_graphql_query(query)
            project_data = result.get("data", {}).get("project", {})
            
            for service_edge in project_data.get("services", {}).get("edges", []):
                service = service_edge["node"]
                service_id = service["id"]
                service_name = service["name"]
                
                deployments = service.get("deployments", {}).get("edges", [])
                if deployments:
                    deployment = deployments[0]["node"]
                    url = deployment.get("url") or deployment.get("staticUrl")
                    
                    if url and deployment.get("status") == "SUCCESS":
                        self.service_urls[service_id] = url
                        self.logger.info(f"🔗 Descoberto serviço {service_name}: {url}")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao descobrir URLs dos serviços: {e}")

    async def _initialize_uptime_stats(self):
        """Inicializa estatísticas de uptime"""
        for service_id in self.service_urls.keys():
            self.uptime_stats[service_id] = {
                "total_checks": 0,
                "successful_checks": 0,
                "uptime_percentage": 100.0,
                "last_downtime": None,
                "total_downtime": timedelta(0),
                "average_response_time": 0.0
            }

    async def _check_all_services_health(self) -> List[HealthCheck]:
        """Verifica saúde de todos os serviços"""
        health_checks = []
        
        tasks = []
        for service_id, url in self.service_urls.items():
            task = self._check_service_health(service_id, url)
            tasks.append(task)
        
        if tasks:
            health_checks = await asyncio.gather(*tasks, return_exceptions=True)
            
            health_checks = [
                check for check in health_checks 
                if isinstance(check, HealthCheck)
            ]
        
        return health_checks

    async def _check_service_health(self, service_id: str, url: str) -> HealthCheck:
        """Verifica saúde de um serviço específico"""
        start_time = time.time()
        
        try:
            health_url = f"{url}/health" if not url.endswith("/health") else url
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.get(health_url) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        if response_time < self.healthy_threshold:
                            status = HealthStatus.HEALTHY
                        elif response_time < self.degraded_threshold:
                            status = HealthStatus.DEGRADED
                        else:
                            status = HealthStatus.UNHEALTHY
                    else:
                        status = HealthStatus.UNHEALTHY
                    
                    return HealthCheck(
                        service_id=service_id,
                        service_name=await self._get_service_name(service_id),
                        status=status,
                        response_time=response_time,
                        timestamp=datetime.now(),
                        url=health_url,
                        status_code=response.status
                    )
                    
        except asyncio.TimeoutError:
            return HealthCheck(
                service_id=service_id,
                service_name=await self._get_service_name(service_id),
                status=HealthStatus.UNHEALTHY,
                response_time=self.timeout,
                timestamp=datetime.now(),
                url=url,
                error_message="Timeout"
            )
            
        except Exception as e:
            return HealthCheck(
                service_id=service_id,
                service_name=await self._get_service_name(service_id),
                status=HealthStatus.UNKNOWN,
                response_time=time.time() - start_time,
                timestamp=datetime.now(),
                url=url,
                error_message=str(e)
            )

    async def _process_health_results(self, health_results: List[HealthCheck]):
        """Processa resultados de verificação de saúde"""
        for health_check in health_results:
            self.health_history.append(health_check)
            
            if len(self.health_history) > 1000:
                self.health_history = self.health_history[-1000:]
            
            if health_check.status == HealthStatus.HEALTHY:
                self.logger.debug(
                    f"✅ {health_check.service_name}: {health_check.response_time:.2f}s"
                )
            elif health_check.status == HealthStatus.DEGRADED:
                self.logger.warning(
                    f"⚠️ {health_check.service_name}: DEGRADED ({health_check.response_time:.2f}s)"
                )
            else:
                self.logger.error(
                    f"❌ {health_check.service_name}: {health_check.status.value} - {health_check.error_message}"
                )

    async def _update_uptime_stats(self, health_results: List[HealthCheck]):
        """Atualiza estatísticas de uptime"""
        for health_check in health_results:
            service_id = health_check.service_id
            stats = self.uptime_stats.get(service_id, {})
            
            stats["total_checks"] = stats.get("total_checks", 0) + 1
            
            if health_check.status == HealthStatus.HEALTHY:
                stats["successful_checks"] = stats.get("successful_checks", 0) + 1
            
            if stats["total_checks"] > 0:
                stats["uptime_percentage"] = (
                    stats["successful_checks"] / stats["total_checks"]
                ) * 100
            
            current_avg = stats.get("average_response_time", 0.0)
            total_checks = stats["total_checks"]
            
            stats["average_response_time"] = (
                (current_avg * (total_checks - 1) + health_check.response_time) / total_checks
            )
            
            if health_check.status != HealthStatus.HEALTHY:
                if stats.get("last_downtime") is None:
                    stats["last_downtime"] = health_check.timestamp
            else:
                if stats.get("last_downtime") is not None:
                    downtime_duration = health_check.timestamp - stats["last_downtime"]
                    stats["total_downtime"] = stats.get("total_downtime", timedelta(0)) + downtime_duration
                    stats["last_downtime"] = None
            
            self.uptime_stats[service_id] = stats

    async def _get_service_name(self, service_id: str) -> str:
        """Obtém nome do serviço"""
        service_names = {
            "8836e701-3783-4320-90d1-1db8addf72c6": "SISTEMA-MEEP",
            "5ecb6cf3-7b62-445c-bd27-7eab8ea798ca": "beautiful-courtesy",
            "a89f4f4f-2a04-4d4d-a11a-63c490ec3456": "GitMcp",
            "d2d93a99-f5d7-47da-ba32-5085bfd61152": "Postgres",
            "dd15444e-0ff5-48d6-96f3-a375b1f258c2": "Redis"
        }
        
        return service_names.get(service_id, f"Service-{service_id[:8]}")

    async def _execute_graphql_query(self, query: str) -> Dict:
        """Executa query GraphQL na Railway API"""
        headers = {
            "Authorization": f"Bearer {self.railway_token}",
            "Content-Type": "application/json"
        }
        
        payload = {"query": query}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.api_base, headers=headers, json=payload) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Railway API error {response.status}: {error_text}")

    def get_current_health_status(self) -> Dict:
        """Retorna status atual de saúde"""
        if not self.health_history:
            return {"status": "no_data", "services": {}}
        
        latest_checks = {}
        for check in reversed(self.health_history):
            if check.service_id not in latest_checks:
                latest_checks[check.service_id] = check
        
        services_status = {}
        overall_healthy = True
        
        for service_id, check in latest_checks.items():
            services_status[check.service_name] = {
                "status": check.status.value,
                "response_time": check.response_time,
                "last_check": check.timestamp.isoformat(),
                "uptime_percentage": self.uptime_stats.get(service_id, {}).get("uptime_percentage", 0),
                "url": check.url
            }
            
            if check.status != HealthStatus.HEALTHY:
                overall_healthy = False
        
        return {
            "overall_status": "HEALTHY" if overall_healthy else "DEGRADED",
            "services": services_status,
            "last_update": datetime.now().isoformat()
        }

    def get_uptime_report(self) -> Dict:
        """Gera relatório de uptime"""
        report = {
            "report_generated": datetime.now().isoformat(),
            "services": {}
        }
        
        for service_id, stats in self.uptime_stats.items():
            service_name = asyncio.run(self._get_service_name(service_id))
            
            report["services"][service_name] = {
                "uptime_percentage": round(stats.get("uptime_percentage", 0), 2),
                "total_checks": stats.get("total_checks", 0),
                "successful_checks": stats.get("successful_checks", 0),
                "average_response_time": round(stats.get("average_response_time", 0), 3),
                "total_downtime_minutes": stats.get("total_downtime", timedelta(0)).total_seconds() / 60,
                "currently_down": stats.get("last_downtime") is not None
            }
        
        return report
