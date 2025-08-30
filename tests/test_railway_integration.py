"""
🧪 TESTES - Railway Integration
Testes para o sistema de correção automática de deploy
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from src.railway.deploy_monitor import DeployMonitor, DeploymentStatus, ErrorSeverity
from src.railway.health_checker import HealthChecker, HealthStatus
from src.railway.railway_integration import RailwayIntegration


class TestDeployMonitor:
    """Testes para DeployMonitor"""

    @pytest.fixture
    def deploy_monitor(self):
        return DeployMonitor("test_token", "test_project_id")

    @pytest.mark.asyncio
    async def test_initialization(self, deploy_monitor):
        """Testa inicialização do deploy monitor"""
        mock_monitor = Mock()
        mock_alertas = Mock()
        
        with patch.object(deploy_monitor, '_verify_api_connectivity', new_callable=AsyncMock):
            with patch.object(deploy_monitor, '_load_deployment_history', new_callable=AsyncMock):
                with patch.object(deploy_monitor, '_establish_deployment_baseline', new_callable=AsyncMock):
                    await deploy_monitor.initialize(mock_monitor, mock_alertas)
                    
                    assert deploy_monitor.monitor == mock_monitor
                    assert deploy_monitor.alertas_preditivos == mock_alertas

    def test_classify_error_type(self, deploy_monitor):
        """Testa classificação de tipos de erro"""
        from src.railway.deploy_monitor import DeploymentInfo
        
        failed_deployment = DeploymentInfo(
            deployment_id="test_id",
            service_id="test_service",
            service_name="test_service",
            status=DeploymentStatus.FAILED,
            created_at=datetime.now()
        )
        
        error_type = deploy_monitor._classify_error_type(failed_deployment)
        assert error_type == "build_failure"

    def test_determine_error_severity(self, deploy_monitor):
        """Testa determinação de severidade de erro"""
        severity = deploy_monitor._determine_error_severity("runtime_crash", None)
        assert severity == ErrorSeverity.CRITICAL
        
        severity = deploy_monitor._determine_error_severity("dependency_failure", None)
        assert severity == ErrorSeverity.HIGH

    def test_is_auto_fixable(self, deploy_monitor):
        """Testa se erro é auto-corrigível"""
        assert deploy_monitor._is_auto_fixable("environment_variable_missing", ErrorSeverity.MEDIUM)
        assert not deploy_monitor._is_auto_fixable("runtime_crash", ErrorSeverity.CRITICAL)

    def test_get_monitoring_stats(self, deploy_monitor):
        """Testa obtenção de estatísticas"""
        stats = deploy_monitor.get_monitoring_stats()
        
        assert "corrections_applied" in stats
        assert "rollbacks_performed" in stats
        assert "success_rate" in stats
        assert "monitoring_features" in stats


class TestHealthChecker:
    """Testes para HealthChecker"""

    @pytest.fixture
    def health_checker(self):
        return HealthChecker("test_token", "test_project_id")

    @pytest.mark.asyncio
    async def test_initialization(self, health_checker):
        """Testa inicialização do health checker"""
        with patch.object(health_checker, '_discover_service_urls', new_callable=AsyncMock):
            with patch.object(health_checker, '_initialize_uptime_stats', new_callable=AsyncMock):
                await health_checker.initialize()
                
                assert health_checker.service_urls is not None
                assert health_checker.uptime_stats is not None

    @pytest.mark.asyncio
    async def test_check_service_health(self, health_checker):
        """Testa verificação de saúde de serviço"""
        service_id = "test_service"
        url = "https://test.railway.app"
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = Mock()
            mock_response.status = 200
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)
            
            mock_session.return_value.__aenter__.return_value.get.return_value = mock_response
            
            health_check = await health_checker._check_service_health(service_id, url)
            
            assert health_check.service_id == service_id
            assert health_check.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED, HealthStatus.UNHEALTHY]

    def test_get_current_health_status(self, health_checker):
        """Testa obtenção de status atual"""
        status = health_checker.get_current_health_status()
        
        assert "overall_status" in status
        assert "services" in status
        assert "last_update" in status

    def test_get_uptime_report(self, health_checker):
        """Testa geração de relatório de uptime"""
        report = health_checker.get_uptime_report()
        
        assert "report_generated" in report
        assert "services" in report


class TestRailwayIntegration:
    """Testes para RailwayIntegration"""

    @pytest.fixture
    def railway_integration(self):
        return RailwayIntegration("test_token", "test_project_id")

    @pytest.mark.asyncio
    async def test_initialization(self, railway_integration):
        """Testa inicialização da integração"""
        mock_config = Mock()
        
        with patch.object(railway_integration, '_initialize_observability_components', new_callable=AsyncMock):
            with patch.object(railway_integration, '_initialize_railway_components', new_callable=AsyncMock):
                with patch.object(railway_integration, '_setup_integrations', new_callable=AsyncMock):
                    await railway_integration.initialize(mock_config)
                    
                    assert railway_integration.initialized

    @pytest.mark.asyncio
    async def test_get_comprehensive_status(self, railway_integration):
        """Testa obtenção de status abrangente"""
        railway_integration.initialized = True
        
        status = await railway_integration.get_comprehensive_status()
        
        assert "timestamp" in status
        assert "railway_integration" in status
        assert status["railway_integration"]["initialized"]

    def test_get_integration_info(self, railway_integration):
        """Testa obtenção de informações da integração"""
        info = railway_integration.get_integration_info()
        
        assert "integration_name" in info
        assert "version" in info
        assert "components" in info
        assert "features" in info
        assert "railway_project" in info


class TestIntegrationScenarios:
    """Testes de cenários de integração"""

    @pytest.mark.asyncio
    async def test_deployment_failure_workflow(self):
        """Testa fluxo completo de falha de deployment"""
        deploy_monitor = DeployMonitor("test_token", "test_project_id")
        
        from src.railway.deploy_monitor import DeploymentInfo, FailureAnalysis
        
        failure = DeploymentInfo(
            deployment_id="test_deployment",
            service_id="test_service",
            service_name="test_service",
            status=DeploymentStatus.FAILED,
            created_at=datetime.now()
        )
        
        analysis = FailureAnalysis(
            error_type="dependency_failure",
            severity=ErrorSeverity.HIGH,
            root_cause="Missing dependency",
            recommended_actions=["Update dependencies"],
            auto_fixable=True,
            confidence=0.85
        )
        
        with patch.object(deploy_monitor, '_analyze_deployment_failure', return_value=analysis):
            with patch.object(deploy_monitor, '_attempt_auto_correction', return_value=True):
                with patch.object(deploy_monitor, '_create_deployment_alert', new_callable=AsyncMock):
                    await deploy_monitor._process_deployment_failure(failure)
                    
                    assert deploy_monitor.corrections_applied == 1

    @pytest.mark.asyncio
    async def test_health_monitoring_workflow(self):
        """Testa fluxo de monitoramento de saúde"""
        health_checker = HealthChecker("test_token", "test_project_id")
        health_checker.service_urls = {"test_service": "https://test.railway.app"}
        
        with patch.object(health_checker, '_check_service_health') as mock_check:
            from src.railway.health_checker import HealthCheck
            
            mock_check.return_value = HealthCheck(
                service_id="test_service",
                service_name="test_service",
                status=HealthStatus.HEALTHY,
                response_time=1.0,
                timestamp=datetime.now(),
                url="https://test.railway.app"
            )
            
            health_results = await health_checker._check_all_services_health()
            
            assert len(health_results) == 1
            assert health_results[0].status == HealthStatus.HEALTHY


@pytest.mark.asyncio
async def test_api_endpoints():
    """Testa endpoints da API"""
    from src.api.railway_endpoints import railway_router
    from fastapi.testclient import TestClient
    from fastapi import FastAPI
    
    app = FastAPI()
    app.include_router(railway_router)
    
    client = TestClient(app)
    
    response = client.get("/api/railway/info")
    assert response.status_code in [200, 503]  # 503 se não inicializado


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
