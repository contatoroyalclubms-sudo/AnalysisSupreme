"""
🌐 RAILWAY API ENDPOINTS - Endpoints FastAPI para Railway Integration
Endpoints para controle e monitoramento do sistema Railway
Performance: REST API | Real-time status | Control interface
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, Optional
import logging

from src.railway.railway_integration import RailwayIntegration

logger = logging.getLogger(__name__)

railway_router = APIRouter(prefix="/api/railway", tags=["Railway Integration"])

railway_integration: Optional[RailwayIntegration] = None


def initialize_railway_integration(railway_token: str, project_id: str, config):
    """Inicializa integração Railway"""
    global railway_integration
    railway_integration = RailwayIntegration(railway_token, project_id)
    return railway_integration


@railway_router.get("/status")
async def get_railway_status():
    """Obtém status completo da integração Railway"""
    if not railway_integration:
        raise HTTPException(
            status_code=503, detail="Railway integration not initialized"
        )

    try:
        status = await railway_integration.get_comprehensive_status()
        return status
    except Exception as e:
        logger.error(f"Error getting Railway status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@railway_router.get("/health")
async def get_services_health():
    """Obtém status de saúde de todos os serviços"""
    if not railway_integration or not railway_integration.health_checker:
        raise HTTPException(status_code=503, detail="Health checker not available")

    try:
        health_status = railway_integration.health_checker.get_current_health_status()
        return health_status
    except Exception as e:
        logger.error(f"Error getting health status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@railway_router.post("/health/check")
async def trigger_health_check():
    """Dispara verificação manual de saúde"""
    if not railway_integration:
        raise HTTPException(
            status_code=503, detail="Railway integration not initialized"
        )

    try:
        result = await railway_integration.trigger_manual_health_check()
        return result
    except Exception as e:
        logger.error(f"Error triggering health check: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@railway_router.get("/deployments")
async def get_deployment_history():
    """Obtém histórico de deployments"""
    if not railway_integration:
        raise HTTPException(
            status_code=503, detail="Railway integration not initialized"
        )

    try:
        history = await railway_integration.get_deployment_history()
        return history
    except Exception as e:
        logger.error(f"Error getting deployment history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@railway_router.get("/deployments/stats")
async def get_deployment_stats():
    """Obtém estatísticas de deployments"""
    if not railway_integration or not railway_integration.deploy_monitor:
        raise HTTPException(status_code=503, detail="Deploy monitor not available")

    try:
        stats = railway_integration.deploy_monitor.get_monitoring_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting deployment stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@railway_router.get("/uptime")
async def get_uptime_report():
    """Obtém relatório de uptime"""
    if not railway_integration or not railway_integration.health_checker:
        raise HTTPException(status_code=503, detail="Health checker not available")

    try:
        uptime_report = railway_integration.health_checker.get_uptime_report()
        return uptime_report
    except Exception as e:
        logger.error(f"Error getting uptime report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@railway_router.post("/simulate/failure")
async def simulate_deployment_failure(
    service_name: str, background_tasks: BackgroundTasks
):
    """Simula falha de deployment para teste"""
    if not railway_integration:
        raise HTTPException(
            status_code=503, detail="Railway integration not initialized"
        )

    try:
        result = await railway_integration.simulate_deployment_failure(service_name)
        return result
    except Exception as e:
        logger.error(f"Error simulating deployment failure: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@railway_router.post("/monitoring/start")
async def start_monitoring(background_tasks: BackgroundTasks):
    """Inicia monitoramento Railway"""
    if not railway_integration:
        raise HTTPException(
            status_code=503, detail="Railway integration not initialized"
        )

    if railway_integration.monitoring_active:
        return {"message": "Monitoring already active", "status": "active"}

    try:
        background_tasks.add_task(railway_integration.start_monitoring)

        return {
            "message": "Railway monitoring started",
            "status": "starting",
            "timestamp": "2025-08-30T10:42:24Z",
        }
    except Exception as e:
        logger.error(f"Error starting monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@railway_router.get("/info")
async def get_integration_info():
    """Obtém informações da integração"""
    if not railway_integration:
        raise HTTPException(
            status_code=503, detail="Railway integration not initialized"
        )

    try:
        info = railway_integration.get_integration_info()
        return info
    except Exception as e:
        logger.error(f"Error getting integration info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@railway_router.get("/dashboard/metrics")
async def get_railway_dashboard_metrics():
    """Obtém métricas para dashboard Railway"""
    if not railway_integration:
        raise HTTPException(
            status_code=503, detail="Railway integration not initialized"
        )

    try:
        status = await railway_integration.get_comprehensive_status()

        dashboard_metrics = {
            "deployment_success_rate": status.get("deploy_monitoring", {}).get(
                "success_rate", 0
            ),
            "corrections_applied": status.get("deploy_monitoring", {}).get(
                "corrections_applied", 0
            ),
            "rollbacks_performed": status.get("deploy_monitoring", {}).get(
                "rollbacks_performed", 0
            ),
            "services_healthy": len(
                [
                    s
                    for s in status.get("health_monitoring", {})
                    .get("current_status", {})
                    .get("services", {})
                    .values()
                    if s.get("status") == "HEALTHY"
                ]
            ),
            "total_services": len(
                status.get("health_monitoring", {})
                .get("current_status", {})
                .get("services", {})
            ),
            "average_response_time": sum(
                [
                    s.get("response_time", 0)
                    for s in status.get("health_monitoring", {})
                    .get("current_status", {})
                    .get("services", {})
                    .values()
                ]
            )
            / max(
                len(
                    status.get("health_monitoring", {})
                    .get("current_status", {})
                    .get("services", {})
                ),
                1,
            ),
            "monitoring_active": status.get("railway_integration", {}).get(
                "monitoring_active", False
            ),
            "last_update": status.get("timestamp"),
        }

        return dashboard_metrics

    except Exception as e:
        logger.error(f"Error getting dashboard metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
