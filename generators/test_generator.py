"""
Générateur de tests avancé
"""
import re
from typing import Dict, List, Optional, Any
from core.llm_handler import LLMHandler
from generators.templates import CodeTemplateGenerator
from config.settings import get_settings

class TestGenerator:
    """Générateur de tests intelligent"""
    
    def __init__(self, project_info: Dict[str, Any] = None):
        self.project_info = project_info or {}
        self.settings = get_settings()
        self.llm_handler = LLMHandler()
        self.template_generator = CodeTemplateGenerator(project_info)
        
        # Détection du langage et framework de test
        self.language = self.project_info.get('language', 'python')
        self.test_framework = self.project_info.get('test_framework', 'pytest')
    
    def generate_unit_tests(self,
                           code: str,
                           class_name: str = None,
                           coverage_target: float = 0.9) -> str:
        """Générer des tests unitaires complets"""
        
        if not self.llm_handler.is_available():
            return self.template_generator.generate_test_template(class_name or "TestClass")
        
        prompt = self._build_unit_test_prompt(code, class_name, coverage_target)
        return self.llm_handler.invoke(prompt)
    
    def generate_integration_tests(self,
                                 components: List[str],
                                 description: str = "") -> str:
        """Générer des tests d'intégration"""
        
        integration_prompt = f"""
Génère des tests d'intégration en {self.language} avec {self.test_framework}.

Composants à tester: {', '.join(components)}
Description: {description}

Requirements:
- Tests d'intégration entre composants
- Configuration de test appropriée
- Mocking des dépendances externes
- Tests de flux complets
- Nettoyage après tests

Framework de test: {self.test_framework}
"""
        
        if self.llm_handler.is_available():
            return self.llm_handler.invoke(integration_prompt)
        else:
            return self._generate_integration_template(components, description)
    
    def generate_api_tests(self,
                          endpoints: List[Dict[str, str]],
                          base_url: str = "http://localhost:8000") -> str:
        """Générer des tests d'API"""
        
        api_prompt = f"""
Génère des tests d'API en {self.language}.

Endpoints à tester:
{self._format_endpoints(endpoints)}

Base URL: {base_url}

Requirements:
- Tests pour chaque endpoint
- Validation des codes de statut
- Validation des réponses JSON
- Tests des cas d'erreur
- Tests de sécurité basiques
- Setup/teardown approprié

Framework de test: {self.test_framework}
"""
        
        if self.llm_handler.is_available():
            return self.llm_handler.invoke(api_prompt)
        else:
            return self._generate_api_template(endpoints, base_url)
    
    def generate_performance_tests(self,
                                 function_name: str,
                                 expected_time: float = 1.0,
                                 load_scenarios: List[Dict] = None) -> str:
        """Générer des tests de performance"""
        
        perf_prompt = f"""
Génère des tests de performance en {self.language}.

Fonction à tester: {function_name}
Temps attendu maximum: {expected_time} secondes
Scénarios de charge: {load_scenarios or []}

Requirements:
- Mesure du temps d'exécution
- Tests de charge avec différents volumes
- Détection de fuites mémoire
- Profilage si possible
- Assertions sur les performances

Framework de test: {self.test_framework}
"""
        
        if self.llm_handler.is_available():
            return self.llm_handler.invoke(perf_prompt)
        else:
            return self._generate_performance_template(function_name, expected_time)
    
    def generate_mock_objects(self,
                             interface_name: str,
                             methods: List[str]) -> str:
        """Générer des objets mock"""
        
        mock_prompt = f"""
Génère des objets mock en {self.language} pour {self.test_framework}.

Interface à mocker: {interface_name}
Méthodes: {', '.join(methods)}

Requirements:
- Mock complet de l'interface
- Comportements configurables
- Vérification des appels
- Valeurs de retour personnalisables
- Documentation d'utilisation

Framework de test: {self.test_framework}
"""
        
        if self.llm_handler.is_available():
            return self.llm_handler.invoke(mock_prompt)
        else:
            return self._generate_mock_template(interface_name, methods)
    
    def analyze_code_for_tests(self, code: str) -> Dict[str, Any]:
        """Analyser le code pour identifier ce qui doit être testé"""
        analysis = {
            'classes': [],
            'functions': [],
            'public_methods': [],
            'private_methods': [],
            'complexity_hotspots': [],
            'dependencies': [],
            'test_suggestions': []
        }
        
        if self.language == 'python':
            analysis.update(self._analyze_python_code(code))
        elif self.language in ['javascript', 'typescript']:
            analysis.update(self._analyze_js_code(code))
        elif self.language == 'java':
            analysis.update(self._analyze_java_code(code))
        
        # Générer des suggestions de tests
        analysis['test_suggestions'] = self._generate_test_suggestions(analysis)
        
        return analysis
    
    def _build_unit_test_prompt(self, code: str, class_name: str = None, coverage_target: float = 0.9) -> str:
        """Construire le prompt pour les tests unitaires"""
        
        # Analyser le code
        analysis = self.analyze_code_for_tests(code)
        
        prompt = f"""
Génère des tests unitaires complets en {self.language} avec {self.test_framework}.

CODE À TESTER:
{code}

ANALYSE DU CODE:
- Classes: {', '.join(analysis['classes'])}
- Fonctions: {', '.join(analysis['functions'])}
- Méthodes publiques: {', '.join(analysis['public_methods'])}

OBJECTIFS:
- Couverture cible: {coverage_target * 100}%
- Framework: {self.test_framework}
- Tests Given-When-Then

REQUIREMENTS:
1. Test de chaque méthode publique
2. Tests des cas limites et d'erreur
3. Mocking des dépendances
4. Assertions complètes
5. Documentation des tests
6. Setup/teardown approprié

TESTS GÉNÉRÉS:
"""
        return prompt
    
    def _analyze_python_code(self, code: str) -> Dict[str, List[str]]:
        """Analyser le code Python"""
        analysis = {
            'classes': re.findall(r'class\s+(\w+)', code),
            'functions': re.findall(r'def\s+(\w+)', code),
            'public_methods': [],
            'private_methods': [],
            'dependencies': re.findall(r'import\s+(\w+)|from\s+(\w+)', code)
        }
        
        # Séparer méthodes publiques/privées
        all_methods = analysis['functions']
        for method in all_methods:
            if method.startswith('_'):
                analysis['private_methods'].append(method)
            else:
                analysis['public_methods'].append(method)
        
        return analysis
    
    def _analyze_js_code(self, code: str) -> Dict[str, List[str]]:
        """Analyser le code JavaScript/TypeScript"""
        return {
            'classes': re.findall(r'class\s+(\w+)', code),
            'functions': re.findall(r'function\s+(\w+)|(\w+)\s*=\s*(?:function|\(.*?\)\s*=>)', code),
            'public_methods': re.findall(r'(\w+)\s*\(.*?\)\s*{', code),
            'dependencies': re.findall(r'import.*?from\s+[\'"]([^\'"]+)[\'"]', code)
        }
    
    def _analyze_java_code(self, code: str) -> Dict[str, List[str]]:
        """Analyser le code Java"""
        return {
            'classes': re.findall(r'class\s+(\w+)', code),
            'functions': re.findall(r'(?:public|private|protected)?\s*\w+\s+(\w+)\s*\(', code),
            'public_methods': re.findall(r'public\s+\w+\s+(\w+)\s*\(', code),
            'dependencies': re.findall(r'import\s+([\w.]+)', code)
        }
    
    def _generate_test_suggestions(self, analysis: Dict[str, Any]) -> List[str]:
        """Générer des suggestions de tests"""
        suggestions = []
        
        if analysis['classes']:
            suggestions.append("Tester l'initialisation de chaque classe")
            suggestions.append("Tester les getters/setters")
        
        if analysis['public_methods']:
            suggestions.append("Tester chaque méthode publique")
            suggestions.append("Tester les cas limites de chaque méthode")
        
        if analysis['dependencies']:
            suggestions.append("Mocker les dépendances externes")
        
        suggestions.extend([
            "Tester la gestion d'erreurs",
            "Tester les validations d'entrée",
            "Tester les cas de nullité",
            "Ajouter des tests de performance si nécessaire"
        ])
        
        return suggestions
    
    def _format_endpoints(self, endpoints: List[Dict[str, str]]) -> str:
        """Formater la liste des endpoints"""
        formatted = []
        for endpoint in endpoints:
            method = endpoint.get('method', 'GET')
            path = endpoint.get('path', '/')
            desc = endpoint.get('description', '')
            formatted.append(f"- {method} {path} : {desc}")
        return '\n'.join(formatted)
    
    def _generate_integration_template(self, components: List[str], description: str) -> str:
        """Template de tests d'intégration"""
        if self.language == 'python':
            return f'''```python
import pytest
from unittest.mock import Mock, patch

class TestIntegration:
    """Tests d'intégration pour {', '.join(components)}"""
    
    @pytest.fixture
    def setup_components(self):
        """Configuration des composants"""
        # Setup des composants à tester
        components = {{}}
        yield components
        # Cleanup
    
    def test_component_integration(self, setup_components):
        """Test d'intégration entre composants"""
        # Given
        components = setup_components
        
        # When
        result = self.execute_integration_flow(components)
        
        # Then
        assert result is not None
        assert result['status'] == 'success'
    
    def execute_integration_flow(self, components):
        """Exécuter le flux d'intégration"""
        # Logique de test d'intégration
        return {{'status': 'success', 'data': 'test'}}
```'''
        else:
            return f"Template d'intégration pour {self.language} non disponible."
    
    def _generate_api_template(self, endpoints: List[Dict[str, str]], base_url: str) -> str:
        """Template de tests d'API"""
        if self.language == 'python':
            return f'''```python
import pytest
import requests
from unittest.mock import patch

class TestAPI:
    """Tests d'API"""
    
    BASE_URL = "{base_url}"
    
    @pytest.fixture
    def api_client(self):
        """Client API pour les tests"""
        return requests.Session()
    
    def test_api_health(self, api_client):
        """Test de santé de l'API"""
        response = api_client.get(f"{{self.BASE_URL}}/health")
        assert response.status_code == 200
    
    def test_api_endpoints(self, api_client):
        """Test des endpoints principaux"""
        endpoints = {self._format_endpoints_for_template(endpoints)}
        
        for method, path in endpoints:
            response = api_client.request(method, f"{{self.BASE_URL}}{{path}}")
            assert response.status_code in [200, 201, 204]
def test_api_error_handling(self, api_client):
       """Test de gestion d'erreurs"""
       # Test 404
       response = api_client.get(f"{self.BASE_URL}/nonexistent")
       assert response.status_code == 404
       
       # Test 400 avec données invalides
       response = api_client.post(f"{self.BASE_URL}/api/data", json={{"invalid": "data"}})
       assert response.status_code == 400
   
   def test_api_authentication(self, api_client):
       """Test d'authentification"""
       # Test sans token
       response = api_client.get(f"{self.BASE_URL}/protected")
       assert response.status_code == 401
       
       # Test avec token valide
       headers = {{"Authorization": "Bearer valid_token"}}
       response = api_client.get(f"{self.BASE_URL}/protected", headers=headers)
       assert response.status_code == 200
```'''
       else:
           return f"Template d'API pour {self.language} non disponible."
   
   def _generate_performance_template(self, function_name: str, expected_time: float) -> str:
       """Template de tests de performance"""
       if self.language == 'python':
           return f'''```python
import pytest
import time
import statistics
from memory_profiler import profile

class TestPerformance:
   """Tests de performance pour {function_name}"""
   
   def test_execution_time(self):
       """Test du temps d'exécution"""
       execution_times = []
       
       for _ in range(10):
           start_time = time.time()
           result = {function_name}()  # Remplacer par l'appel réel
           end_time = time.time()
           execution_times.append(end_time - start_time)
       
       avg_time = statistics.mean(execution_times)
       assert avg_time < {expected_time}, f"Temps moyen: {{avg_time:.3f}}s > {expected_time}s"
   
   def test_load_performance(self):
       """Test de performance sous charge"""
       import concurrent.futures
       
       def execute_function():
           return {function_name}()  # Remplacer par l'appel réel
       
       # Test avec 10 threads simultanés
       with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
           start_time = time.time()
           futures = [executor.submit(execute_function) for _ in range(100)]
           results = [f.result() for f in concurrent.futures.as_completed(futures)]
           end_time = time.time()
       
       total_time = end_time - start_time
       throughput = len(results) / total_time
       
       assert throughput > 10, f"Throughput trop faible: {{throughput:.2f}} op/s"
   
   @profile
   def test_memory_usage(self):
       """Test d'utilisation mémoire"""
       # Ce test nécessite memory_profiler
       result = {function_name}()  # Remplacer par l'appel réel
       assert result is not None
```'''
       else:
           return f"Template de performance pour {self.language} non disponible."
   
   def _generate_mock_template(self, interface_name: str, methods: List[str]) -> str:
       """Template d'objets mock"""
       if self.language == 'python':
           methods_str = '\n'.join([f'    def {method}(self, *args, **kwargs):\n        return self.mock_{method}(*args, **kwargs)' for method in methods])
           
           return f'''```python
from unittest.mock import Mock, MagicMock
import pytest

class Mock{interface_name}:
   """Mock pour {interface_name}"""
   
   def __init__(self):
       # Créer des mocks pour chaque méthode
{chr(10).join([f"        self.mock_{method} = Mock()" for method in methods])}
   
{methods_str}
   
   def configure_method(self, method_name: str, return_value=None, side_effect=None):
       """Configurer le comportement d'une méthode"""
       mock_method = getattr(self, f"mock_{{method_name}}")
       if return_value is not None:
           mock_method.return_value = return_value
       if side_effect is not None:
           mock_method.side_effect = side_effect
   
   def assert_method_called(self, method_name: str, *args, **kwargs):
       """Vérifier qu'une méthode a été appelée"""
       mock_method = getattr(self, f"mock_{{method_name}}")
       mock_method.assert_called_with(*args, **kwargs)
   
   def reset_mocks(self):
       """Réinitialiser tous les mocks"""
{chr(10).join([f"        self.mock_{method}.reset_mock()" for method in methods])}

@pytest.fixture
def {interface_name.lower()}_mock():
   """Fixture pour le mock {interface_name}"""
   return Mock{interface_name}()

# Exemple d'utilisation:
# def test_with_mock({interface_name.lower()}_mock):
#     {interface_name.lower()}_mock.configure_method("method_name", return_value="test")
#     result = your_function_using_{interface_name.lower()}({interface_name.lower()}_mock)
#     {interface_name.lower()}_mock.assert_method_called("method_name")
```'''
       else:
           return f"Template de mock pour {self.language} non disponible."
   
   def _format_endpoints_for_template(self, endpoints: List[Dict[str, str]]) -> str:
       """Formater les endpoints pour le template"""
       formatted = []
       for endpoint in endpoints:
           method = endpoint.get('method', 'GET')
           path = endpoint.get('path', '/')
           formatted.append(f'("{method}", "{path}")')
       return '[' + ', '.join(formatted) + ']'
   
   def generate_test_suite(self, code: str, test_types: List[str] = None) -> str:
       """Générer une suite de tests complète"""
       test_types = test_types or ['unit', 'integration']
       
       analysis = self.analyze_code_for_tests(code)
       
       suite_prompt = f"""
Génère une suite de tests complète en {self.language} avec {self.test_framework}.

CODE À TESTER:
{code[:1000]}...

TYPES DE TESTS: {', '.join(test_types)}
ANALYSE: {analysis}

Requirements:
- Suite de tests organisée
- Configuration de test appropriée
- Fixtures réutilisables
- Tests de différents niveaux
- Documentation complète
- Coverage maximale

Framework: {self.test_framework}
"""
       
       if self.llm_handler.is_available():
           return self.llm_handler.invoke(suite_prompt)
       else:
           return self._generate_test_suite_template(analysis, test_types)
   
   def _generate_test_suite_template(self, analysis: Dict[str, Any], test_types: List[str]) -> str:
       """Template de suite de tests"""
       if self.language == 'python':
           return f'''```python
import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock

class TestSuite:
   """Suite de tests complète"""
   
   @pytest.fixture(scope="session")
   def setup_test_environment(self):
       """Configuration globale des tests"""
       # Setup de l'environnement de test
       yield
       # Cleanup global
   
   @pytest.fixture
   def mock_dependencies(self):
       """Mock des dépendances communes"""
       mocks = {{}}
       # Créer les mocks nécessaires
       yield mocks
   
   class TestUnit:
       """Tests unitaires"""
       
       def test_basic_functionality(self, mock_dependencies):
           """Test de fonctionnalité de base"""
           # Given
           setup_data = {{"test": "data"}}
           
           # When
           result = self.execute_function(setup_data)
           
           # Then
           assert result is not None
           assert result['status'] == 'success'
       
       def execute_function(self, data):
           """Fonction d'aide pour les tests"""
           return {{"status": "success", "data": data}}
   
   {"class TestIntegration:" if "integration" in test_types else "# Tests d'intégration désactivés"}
       {"def test_component_integration(self):" if "integration" in test_types else ""}
           {"# Test d'intégration" if "integration" in test_types else ""}
           {"pass" if "integration" in test_types else ""}

# Configuration pytest
pytest_plugins = []

def pytest_configure(config):
   """Configuration pytest"""
   config.addinivalue_line(
       "markers", "integration: mark test as integration test"
   )
   config.addinivalue_line(
       "markers", "slow: mark test as slow running"
   )

# Exécution: pytest -v --cov=your_module tests/
```'''
       else:
           return f"Template de suite pour {self.language} non disponible."