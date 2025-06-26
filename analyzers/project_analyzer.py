"""
Analyseur de projet simplifié
"""
import os
from pathlib import Path
from typing import Dict, Any
from collections import defaultdict

class ProjectAnalyzer:
    """Analyseur de projet simple"""
    
    def __init__(self):
        self.extensions = {
            '.py': 'python',
            '.js': 'javascript', 
            '.ts': 'typescript',
            '.java': 'java',
            '.cs': 'csharp',
            '.go': 'go',
            '.rs': 'rust'
        }
    
    def analyze_project(self, project_path: str) -> Dict[str, Any]:
        """Analyse simple d'un projet"""
        if not os.path.exists(project_path):
            return {}
        
        print(f"🔍 Analyse du projet: {project_path}")
        
        language_stats = self._detect_languages(project_path)
        main_language = max(language_stats.items(), key=lambda x: x[1])[0] if language_stats else 'unknown'
        
        metrics = self._calculate_basic_metrics(project_path)
        
        analysis = {
            'language': main_language,
            'language_stats': language_stats,
            'framework': self._detect_framework(project_path, main_language),
            'test_framework': self._detect_test_framework(project_path, main_language),
            'conventions': ['standard'],
            'patterns': ['standard'],
            'metrics': metrics,
            'quality_score': self._calculate_quality_score(metrics)
        }
        
        print(f"✅ Analyse terminée: {main_language}")
        return analysis
    
    def _detect_languages(self, project_path: str) -> Dict[str, int]:
        """Détecter les langages utilisés"""
        language_counts = defaultdict(int)
        
        for root, dirs, files in os.walk(project_path):
            dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', 'venv', '__pycache__']]
            
            for file in files:
                ext = Path(file).suffix.lower()
                if ext in self.extensions:
                    language_counts[self.extensions[ext]] += 1
        
        return dict(language_counts)
    
    def _detect_framework(self, project_path: str, language: str) -> str:
        """Détection simple de framework"""
        framework_files = {
            'python': {
                'django': ['manage.py', 'settings.py'],
                'flask': ['app.py'],
                'fastapi': ['main.py']
            },
            'javascript': {
                'react': ['package.json'],
                'vue': ['vue.config.js'],
                'express': ['app.js', 'server.js']
            }
        }
        
        if language in framework_files:
            for framework, files in framework_files[language].items():
                if any(os.path.exists(os.path.join(project_path, f)) for f in files):
                    return framework
        
        return 'standard'
    
    def _detect_test_framework(self, project_path: str, language: str) -> str:
        """Détection simple de framework de test"""
        test_frameworks = {
            'python': 'pytest',
            'javascript': 'jest',
            'java': 'junit'
        }
        return test_frameworks.get(language, 'standard')
    
    def _calculate_basic_metrics(self, project_path: str) -> Dict[str, Any]:
        """Calcul de métriques basiques"""
        metrics = {
            'total_files': 0,
            'test_files': 0,
            'code_lines': 0,
            'avg_complexity': 1.0
        }
        
        for root, dirs, files in os.walk(project_path):
            dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', 'venv']]
            
            for file in files:
                if any(file.endswith(ext) for ext in self.extensions.keys()):
                    metrics['total_files'] += 1
                    
                    if 'test' in file.lower() or 'spec' in file.lower():
                        metrics['test_files'] += 1
                    
                    # Compter les lignes
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = len([line for line in f if line.strip()])
                            metrics['code_lines'] += lines
                    except:
                        pass
        
        return metrics
    
    def _calculate_quality_score(self, metrics: Dict[str, Any]) -> float:
        """Calcul simple du score de qualité"""
        score = 5.0  # Score de base
        
        # Bonus pour les tests
        total_files = metrics.get('total_files', 1)
        test_files = metrics.get('test_files', 0)
        test_ratio = test_files / total_files if total_files > 0 else 0
        score += min(2.0, test_ratio * 4)
        
        # Bonus pour la taille raisonnable
        if metrics.get('code_lines', 0) > 1000:
            score += 1.0
        
        return round(min(10.0, max(0.0, score)), 1)