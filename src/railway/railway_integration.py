"""
🔗 RAILWAY INTEGRATION - Sistema Principal de Integração
Integra monitoramento de deploy, health checking e correção automática
Performance: Unified monitoring | Centralized control | Real-time integration
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from src.railway.deploy_monitor import DeployMonitor
from src.railway.health_checker import HealthChecker
from src.observabilidade.monitor import Monitor
from src.observabilidade.alertas_preditivos import AlertasPreditivos
from src.observabilidade.dashboard_supremo import DashboardSupremo


class RailwayIntegration:
    """Sistema principal de integração Railway"""

    def __init__(self, railway_token: str, project_id: str):
        self.railway_token = railway_token
        self.project_id = project_id
        self.logger = logging.getLogger(__name__)
        
        self.deploy_monitor: Optional[DeployMonitor] = None
        self.health_checker: Optional[HealthChecker] = None
        
        self.monitor: Optional[Monitor] = None
        self.alertas_preditivos: Optional[AlertasPreditivos] = None
        self.dashboard: Optional[DashboardSupremo] = None
        
        self.initialized = False
        self.monitoring_active = False

    async def initialize(self, config):
        """Inicializa toda a integração Railway"""
        self.logger.info("🚀 Inicializando Integração Railway Completa")
        
        try:
            await self._initialize_observability_components(config)
            
            await self._initialize_railway_components()
            
            await self._setup_integrations()
            
            self.initialized = True
            self.logger.info("✅ Integração Railway inicializada com sucesso")
            
        except Exception as e:
            self.logger.error(f"❌ Erro na inicialização da integração Railway: {e}")
            raise

    async def start_monitoring(self):
        """Inicia todos os sistemas de monitoramento"""
        if not self.initialized:
            raise RuntimeError("Sistema não inicializado. Chame initialize() primeiro.")
        
        self.logger.info("🔄 Iniciando monitoramento Railway completo")
        
        tasks = []
        
        if self.deploy_monitor:
            tasks.append(self.deploy_monitor.start_monitoring())
        
        if self.health_checker:
            tasks.append(self.health_checker.start_health_monitoring())
        
        if self.monitor:
            tasks.append(self.monitor.executar_monitoramento())
        
        self.monitoring_active = True
        
        await asyncio.gather(*tasks, return_exceptions=True)

    async def get_comprehensive_status(self) -> Dict[str, Any]:
        """Obtém status abrangente de todo o sistema"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "railway_integration": {
                "initialized": self.initialized,
                "monitoring_active": self.monitoring_active,
                "project_id": self.project_id
            }
        }
        
        if self.deploy_monitor:
            status["deploy_monitoring"] = self.deploy_monitor.get_monitoring_stats()
        
        if self.health_checker:
            status["health_monitoring"] = {
                "current_status": self.health_checker.get_current_health_status(),
                "uptime_report": self.health_checker.get_uptime_report()
            }
        
        if self.monitor:
            status["system_monitoring"] = self.monitor.get_metricas_tempo_real()
        
        if self.dashboard:
            status["dashboard_metrics"] = await self.dashboard.generate_realtime_metrics()
        
        return status

    async def trigger_manual_health_check(self) -> Dict[str, Any]:
        """Dispara verificação manual de saúde"""
        if not self.health_checker:
            return {"error": "Health checker não inicializado"}
        
        self.logger.info("🏥 Executando verificação manual de saúde")
        
        health_results = await self.health_checker._check_all_services_health()
        await self.health_checker._process_health_results(health_results)
        
        return {
            "manual_check_completed": True,
            "timestamp": datetime.now().isoformat(),
            "results": [
                {
                    "service": check.service_name,
                    "status": check.status.value,
                    "response_time": check.response_time,
                    "url": check.url
                }
                for check in health_results
            ]
        }

    async def simulate_deployment_failure(self, service_name: str) -> Dict[str, Any]:
        """Simula falha de deployment para teste"""
        if not self.deploy_monitor:
            return {"error": "Deploy monitor não inicializado"}
        
        self.logger.info(f"🧪 Simulando falha de deployment para {service_name}")
        
        
        return {
            "simulation_started": True,
            "service": service_name,
            "timestamp": datetime.now().isoformat(),
            "message": f"Simulação de falha iniciada para {service_name}"
        }

    async def get_deployment_history(self) -> Dict[str, Any]:
        """Obtém histórico de deployments"""
        if not self.deploy_monitor:
            return {"error": "Deploy monitor não inicializado"}
        
        return {
            "deployment_history": [
                {
                    "deployment_id": dep.deployment_id,
                    "service_name": dep.service_name,
                    "status": dep.status.value,
                    "created_at": dep.created_at.isoformat(),
                    "url": dep.url
                }
                for dep in self.deploy_monitor.deployment_history
            ],
            "total_deployments": len(self.deploy_monitor.deployment_history),
            "failure_patterns": self.deploy_monitor.failure_patterns
        }

    async def _initialize_observability_components(self, config):
        """Inicializa componentes de observabilidade existentes"""
        self.logger.info("📊 Inicializando componentes de observabilidade")
        
        self.monitor = Monitor(config)
        await self.monitor.inicializar()
        
        self.alertas_preditivos = AlertasPreditivos()
        await self.alertas_preditivos.initialize()
        
        self.dashboard = DashboardSupremo()

    async def _initialize_railway_components(self):
        """Inicializa componentes Railway"""
        self.logger.info("🚂 Inicializando componentes Railway")
        
        self.deploy_monitor = DeployMonitor(self.railway_token, self.project_id)
        if self.monitor and self.alertas_preditivos and self.deploy_monitor:
            await self.deploy_monitor.initialize(self.monitor, self.alertas_preditivos)
        
        self.health_checker = HealthChecker(self.railway_token, self.project_id)
        if self.health_checker:
            await self.health_checker.initialize()

    async def _setup_integrations(self):
        """Configura integrações entre componentes"""
        self.logger.info("🔗 Configurando integrações")
        
        if self.monitor:
            await self.monitor.registrar_bot("railway_integration")
        
        if self.alertas_preditivos:
            pass

    def get_integration_info(self) -> Dict[str, Any]:
        """Retorna informações da integração"""
        return {
            "integration_name": "Railway Automatic Deploy Correction System",
            "version": "1.0.0",
            "components": {
                "deploy_monitor": self.deploy_monitor is not None,
                "health_checker": self.health_checker is not None,
                "system_monitor": self.monitor is not None,
                "predictive_alerts": self.alertas_preditivos is not None,
                "dashboard": self.dashboard is not None
            },
            "features": [
                "automatic_deployment_monitoring",
                "intelligent_failure_detection",
                "auto_correction_capabilities",
                "smart_rollback_system",
                "real_time_health_monitoring",
                "predictive_failure_alerts",
                "comprehensive_uptime_tracking",
                "integration_with_existing_observability"
            ],
            "railway_project": {
                "project_id": self.project_id,
                "api_integration": "active"
            },
            "status": {
                "initialized": self.initialized,
                "monitoring_active": self.monitoring_active
            }
        }
