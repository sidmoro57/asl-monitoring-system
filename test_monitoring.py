"""
Tests pour le système de monitoring ASL.
Valide les fonctionnalités critiques du monitoring.
"""
import pytest
import json
import os
import tempfile
import shutil
from datetime import datetime
import requests_mock

from monitoring_engine import MonitoringEngine, ServiceMonitor, HealthCheckResult
from incident_tracker import IncidentTracker
from slack_notifier import SlackNotifier


class TestHealthCheckResult:
    """Tests pour HealthCheckResult."""
    
    def test_success_result(self):
        """Test d'un résultat de health check réussi."""
        result = HealthCheckResult(success=True, status_code=200, response_time=0.5)
        
        assert result.success is True
        assert result.status_code == 200
        assert result.response_time == 0.5
        assert result.error is None
        
    def test_failure_result(self):
        """Test d'un résultat de health check en échec."""
        result = HealthCheckResult(
            success=False,
            status_code=500,
            response_time=1.2,
            error="Internal Server Error"
        )
        
        assert result.success is False
        assert result.status_code == 500
        assert result.error == "Internal Server Error"
    
    def test_to_dict(self):
        """Test de conversion en dictionnaire."""
        result = HealthCheckResult(success=True, status_code=200, response_time=0.3)
        data = result.to_dict()
        
        assert 'success' in data
        assert 'status_code' in data
        assert 'response_time' in data
        assert 'timestamp' in data
        assert data['success'] is True


class TestServiceMonitor:
    """Tests pour ServiceMonitor."""
    
    def test_monitor_initialization(self):
        """Test d'initialisation d'un moniteur."""
        monitor = ServiceMonitor(
            name="Test Service",
            url="https://example.com/health",
            expected_status=200,
            timeout=10,
            critical=True
        )
        
        assert monitor.name == "Test Service"
        assert monitor.url == "https://example.com/health"
        assert monitor.expected_status == 200
        assert monitor.timeout == 10
        assert monitor.critical is True
        assert monitor.consecutive_failures == 0
    
    def test_successful_health_check(self):
        """Test d'un health check réussi."""
        monitor = ServiceMonitor(
            name="Test Service",
            url="https://example.com/health",
            expected_status=200
        )
        
        with requests_mock.Mocker() as m:
            m.get("https://example.com/health", status_code=200)
            result = monitor.check_health()
            
            assert result.success is True
            assert result.status_code == 200
            assert monitor.consecutive_failures == 0
    
    def test_failed_health_check_wrong_status(self):
        """Test d'un health check échoué (mauvais status)."""
        monitor = ServiceMonitor(
            name="Test Service",
            url="https://example.com/health",
            expected_status=200
        )
        
        with requests_mock.Mocker() as m:
            m.get("https://example.com/health", status_code=500)
            result = monitor.check_health()
            
            assert result.success is False
            assert result.status_code == 500
            assert monitor.consecutive_failures == 1
    
    def test_failed_health_check_timeout(self):
        """Test d'un health check échoué (timeout)."""
        import requests.exceptions
        
        monitor = ServiceMonitor(
            name="Test Service",
            url="https://example.com/health",
            timeout=1
        )
        
        with requests_mock.Mocker() as m:
            m.get("https://example.com/health", exc=requests.exceptions.Timeout)
            result = monitor.check_health()
            
            assert result.success is False
            assert "Timeout" in result.error
            assert monitor.consecutive_failures == 1
    
    def test_consecutive_failures_count(self):
        """Test du comptage des échecs consécutifs."""
        monitor = ServiceMonitor(
            name="Test Service",
            url="https://example.com/health"
        )
        
        with requests_mock.Mocker() as m:
            # Premier échec
            m.get("https://example.com/health", status_code=500)
            monitor.check_health()
            assert monitor.consecutive_failures == 1
            
            # Deuxième échec
            monitor.check_health()
            assert monitor.consecutive_failures == 2
            
            # Succès - reset du compteur
            m.get("https://example.com/health", status_code=200)
            monitor.check_health()
            assert monitor.consecutive_failures == 0
    
    def test_get_status(self):
        """Test de récupération du statut."""
        monitor = ServiceMonitor(
            name="Test Service",
            url="https://example.com/health"
        )
        
        status = monitor.get_status()
        
        assert status['name'] == "Test Service"
        assert status['url'] == "https://example.com/health"
        assert status['consecutive_failures'] == 0
        assert status['critical'] is True


class TestMonitoringEngine:
    """Tests pour MonitoringEngine."""
    
    def test_engine_initialization(self):
        """Test d'initialisation du moteur."""
        services_config = [
            {
                'name': 'Service 1',
                'url': 'https://example.com/health1',
                'expected_status': 200
            },
            {
                'name': 'Service 2',
                'url': 'https://example.com/health2',
                'expected_status': 200
            }
        ]
        
        engine = MonitoringEngine(services_config, failure_threshold=2)
        
        assert len(engine.monitors) == 2
        assert engine.failure_threshold == 2
    
    def test_check_all_services(self):
        """Test de vérification de tous les services."""
        services_config = [
            {'name': 'Service 1', 'url': 'https://example.com/health1'},
            {'name': 'Service 2', 'url': 'https://example.com/health2'}
        ]
        
        engine = MonitoringEngine(services_config)
        
        with requests_mock.Mocker() as m:
            m.get("https://example.com/health1", status_code=200)
            m.get("https://example.com/health2", status_code=200)
            
            results = engine.check_all_services()
            
            assert len(results) == 2
            assert 'Service 1' in results
            assert 'Service 2' in results
            assert results['Service 1'].success is True
            assert results['Service 2'].success is True
    
    def test_get_failing_services(self):
        """Test de récupération des services en échec."""
        services_config = [
            {'name': 'Service OK', 'url': 'https://example.com/health1'},
            {'name': 'Service KO', 'url': 'https://example.com/health2'}
        ]
        
        engine = MonitoringEngine(services_config, failure_threshold=1)
        
        with requests_mock.Mocker() as m:
            m.get("https://example.com/health1", status_code=200)
            m.get("https://example.com/health2", status_code=500)
            
            engine.check_all_services()
            failing = engine.get_failing_services()
            
            assert len(failing) == 1
            assert failing[0].name == 'Service KO'
    
    def test_get_service_monitor(self):
        """Test de récupération d'un moniteur par nom."""
        services_config = [
            {'name': 'Test Service', 'url': 'https://example.com/health'}
        ]
        
        engine = MonitoringEngine(services_config)
        monitor = engine.get_service_monitor('Test Service')
        
        assert monitor is not None
        assert monitor.name == 'Test Service'
        
        # Test service inexistant
        assert engine.get_service_monitor('Inexistant') is None


class TestIncidentTracker:
    """Tests pour IncidentTracker."""
    
    def setup_method(self):
        """Créer un répertoire temporaire pour les tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.tracker = IncidentTracker(incidents_dir=self.temp_dir)
    
    def teardown_method(self):
        """Nettoyer le répertoire temporaire."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_start_incident(self):
        """Test de création d'un incident."""
        details = {
            'url': 'https://example.com/health',
            'error': 'Connection timeout',
            'status_code': None
        }
        
        incident_id = self.tracker.start_incident('Test Service', details)
        
        assert incident_id is not None
        assert self.tracker.has_active_incident('Test Service')
        
        incident = self.tracker.get_active_incident('Test Service')
        assert incident['service'] == 'Test Service'
        assert incident['status'] == 'active'
        assert incident['details'] == details
    
    def test_end_incident(self):
        """Test de résolution d'un incident."""
        details = {'url': 'https://example.com/health', 'error': 'Timeout'}
        
        self.tracker.start_incident('Test Service', details)
        assert self.tracker.has_active_incident('Test Service')
        
        self.tracker.end_incident('Test Service')
        assert not self.tracker.has_active_incident('Test Service')
    
    def test_incident_duration_calculation(self):
        """Test du calcul de la durée d'incident."""
        import time
        
        details = {'url': 'https://example.com/health'}
        incident_id = self.tracker.start_incident('Test Service', details)
        
        time.sleep(0.1)  # Attendre 100ms
        
        self.tracker.end_incident('Test Service')
        
        # Vérifier que l'incident est sauvegardé avec une durée
        history = self.tracker.get_incident_history(limit=1)
        assert len(history) == 1
        assert history[0]['duration_seconds'] is not None
        assert history[0]['duration_seconds'] > 0
    
    def test_incident_persistence(self):
        """Test de la persistance des incidents."""
        details = {'url': 'https://example.com/health'}
        incident_id = self.tracker.start_incident('Test Service', details)
        
        # Vérifier que le fichier existe
        incident_file = os.path.join(self.temp_dir, f"{incident_id}.json")
        assert os.path.exists(incident_file)
        
        # Vérifier le contenu
        with open(incident_file, 'r') as f:
            data = json.load(f)
            assert data['service'] == 'Test Service'
            assert data['id'] == incident_id
    
    def test_get_incident_history(self):
        """Test de récupération de l'historique."""
        # Créer plusieurs incidents
        for i in range(3):
            self.tracker.start_incident(f'Service {i}', {'test': i})
        
        history = self.tracker.get_incident_history()
        assert len(history) == 3
    
    def test_get_statistics(self):
        """Test des statistiques d'incidents."""
        import time
        
        # Créer et résoudre un incident
        self.tracker.start_incident('Service 1', {})
        time.sleep(0.05)
        self.tracker.end_incident('Service 1')
        
        # Créer un incident actif
        self.tracker.start_incident('Service 2', {})
        
        stats = self.tracker.get_statistics()
        
        assert stats['total_incidents'] == 2
        assert stats['resolved_incidents'] == 1
        assert stats['active_incidents'] == 1
        assert stats['average_duration_seconds'] > 0


class TestSlackNotifier:
    """Tests pour SlackNotifier."""
    
    def test_notifier_initialization_disabled(self):
        """Test d'initialisation avec notifications désactivées."""
        notifier = SlackNotifier(enabled=False)
        
        assert notifier.enabled is False
        assert notifier.client is None
    
    def test_notifier_initialization_enabled(self):
        """Test d'initialisation avec notifications activées."""
        notifier = SlackNotifier(token="xoxb-test-token", enabled=True)
        
        assert notifier.enabled is True
        assert notifier.client is not None
    
    def test_send_alert_disabled(self):
        """Test d'envoi d'alerte quand désactivé (ne doit pas planter)."""
        notifier = SlackNotifier(enabled=False)
        
        # Ne doit pas lever d'exception
        notifier.send_alert(
            service_name="Test",
            incident_id="test123",
            details={'url': 'https://example.com'},
            is_critical=True
        )
    
    def test_send_recovery_disabled(self):
        """Test d'envoi de recovery quand désactivé (ne doit pas planter)."""
        notifier = SlackNotifier(enabled=False)
        
        # Ne doit pas lever d'exception
        notifier.send_recovery(
            service_name="Test",
            incident_id="test123",
            duration_seconds=45.5
        )
    
    def test_format_duration(self):
        """Test du formatage des durées."""
        notifier = SlackNotifier(enabled=False)
        
        assert notifier._format_duration(30) == "30s"
        assert notifier._format_duration(90) == "1m 30s"
        assert notifier._format_duration(3665) == "1h 1m"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
