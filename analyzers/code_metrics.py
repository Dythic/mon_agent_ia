"""
Calcul des métriques de qualité du code
"""
import os
import re
import ast
from typing import Dict, List, Any, Optional
from pathlib import Path

class CodeMetricsCalculator:
    """Calculateur de métriques de code"""
    
    def __init__(self):
        self.language_analyzers = {
            'python': self._analyze_python_file,
            'javascript': self._analyze_js_file,
            'typescript': self._analyze_js_file,
            'java': self._analyze_java_file,
        }
    
    def calculate_project_metrics(self, project_path: str, language: str) -> Dict[str, Any]:
        """Calculer les métriques d'un projet complet"""
        metrics = {
            'total_files': 0,
            'test_files': 0,
            'code_lines': 0,
            'comment_lines': 0,
            'blank_lines': 0,
            'avg_complexity': 0.0,
            'max_complexity': 0,
            'functions_count': 0,
            'classes_count': 0,
            'duplicated_lines': 0,
            'technical_debt_ratio': 0.0,
            'maintainability_index': 0.0
        }
        
        complexity_scores = []
        all_functions = []
        
        for root, dirs, files in os.walk(project_path):
            # Exclure les dossiers standards
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', 'venv', 'target']]
            
            for file in files:
                if self._is_code_file(file, language):
                    file_path = os.path.join(root, file)
                    file_metrics = self.calculate_file_metrics(file_path, language)
                    
                    if file_metrics:
                        metrics['total_files'] += 1
                        metrics['code_lines'] += file_metrics['code_lines']
                        metrics['comment_lines'] += file_metrics['comment_lines']
                        metrics['blank_lines'] += file_metrics['blank_lines']
                        metrics['functions_count'] += file_metrics['functions_count']
                        metrics['classes_count'] += file_metrics['classes_count']
                        
                        if 'test' in file.lower() or 'spec' in file.lower():
                            metrics['test_files'] += 1
                        
                        if file_metrics['complexity'] > 0:
                            complexity_scores.append(file_metrics['complexity'])
                            metrics['max_complexity'] = max(metrics['max_complexity'], file_metrics['complexity'])
                        
                        all_functions.extend(file_metrics.get('function_names', []))
        
        # Calculs finaux
        if complexity_scores:
            metrics['avg_complexity'] = sum(complexity_scores) / len(complexity_scores)
        
        # Calcul de la dette technique (estimation)
        metrics['technical_debt_ratio'] = self._calculate_technical_debt(metrics)
        
        # Index de maintenabilité (formule simplifiée)
        metrics['maintainability_index'] = self._calculate_maintainability_index(metrics)
        
        # Détection de duplication simple
        metrics['duplicated_lines'] = self._estimate_duplication(all_functions)
        
        return metrics
    
    def calculate_file_metrics(self, file_path: str, language: str) -> Optional[Dict[str, Any]]:
        """Calculer les métriques d'un fichier"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Métriques de base
            lines = content.split('\n')
            metrics = {
                'total_lines': len(lines),
                'code_lines': 0,
                'comment_lines': 0,
                'blank_lines': 0,
                'complexity': 0,
                'functions_count': 0,
                'classes_count': 0,
                'function_names': [],
                'class_names': []
            }
            
            # Compter les types de lignes
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    metrics['blank_lines'] += 1
                elif self._is_comment_line(stripped, language):
                    metrics['comment_lines'] += 1
                else:
                    metrics['code_lines'] += 1
            
            # Analyse spécifique au langage
            if language in self.language_analyzers:
                lang_metrics = self.language_analyzers[language](content)
                metrics.update(lang_metrics)
            
            return metrics
            
        except Exception as e:
            print(f"⚠️ Erreur analyse fichier {file_path}: {e}")
            return None
    
    def _is_code_file(self, filename: str, language: str) -> bool:
        """Vérifier si c'est un fichier de code"""
        extensions = {
            'python': ['.py', '.pyw'],
            'javascript': ['.js', '.jsx'],
            'typescript': ['.ts', '.tsx'],
            'java': ['.java'],
            'csharp': ['.cs'],
            'go': ['.go'],
            'rust': ['.rs']
        }
        
        if language not in extensions:
            return False
        
        return any(filename.endswith(ext) for ext in extensions[language])
    
    def _is_comment_line(self, line: str, language: str) -> bool:
        """Vérifier si une ligne est un commentaire"""
        comment_patterns = {
            'python': ['#'],
            'javascript': ['//', '/*', '*/', '*'],
            'typescript': ['//', '/*', '*/', '*'],
            'java': ['//', '/*', '*/', '*'],
            'csharp': ['//', '/*', '*/', '*'],
            'go': ['//', '/*', '*/'],
            'rust': ['//', '/*', '*/']
        }
        
        if language not in comment_patterns:
            return False
        
        return any(line.startswith(pattern) for pattern in comment_patterns[language])
    
    def _analyze_python_file(self, content: str) -> Dict[str, Any]:
        """Analyser un fichier Python"""
        metrics = {
            'complexity': 0,
            'functions_count': 0,
            'classes_count': 0,
            'function_names': [],
            'class_names': []
        }
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    metrics['functions_count'] += 1
                    metrics['function_names'].append(node.name)
                    # Complexité cyclomatique simplifiée
                    complexity = self._calculate_python_complexity(node)
                    metrics['complexity'] += complexity
                
                elif isinstance(node, ast.ClassDef):
                    metrics['classes_count'] += 1
                    metrics['class_names'].append(node.name)
        
        except SyntaxError:
            # Si le parsing échoue, utiliser une analyse par regex
            metrics.update(self._analyze_by_regex(content, 'python'))
        
        return metrics
    
    def _analyze_js_file(self, content: str) -> Dict[str, Any]:
        """Analyser un fichier JavaScript/TypeScript"""
        metrics = {
            'complexity': 0,
            'functions_count': 0,
            'classes_count': 0,
            'function_names': [],
            'class_names': []
        }
        
        # Analyse par regex (simple)
        metrics.update(self._analyze_by_regex(content, 'javascript'))
        
        return metrics
    
    def _analyze_java_file(self, content: str) -> Dict[str, Any]:
        """Analyser un fichier Java"""
        metrics = {
            'complexity': 0,
            'functions_count': 0,
            'classes_count': 0,
            'function_names': [],
            'class_names': []
        }
        
        # Analyse par regex
        metrics.update(self._analyze_by_regex(content, 'java'))
        
        return metrics
    
    def _analyze_by_regex(self, content: str, language: str) -> Dict[str, Any]:
        """Analyse par expressions régulières"""
        metrics = {
            'complexity': 0,
            'functions_count': 0,
            'classes_count': 0,
            'function_names': [],
            'class_names': []
        }
        
        patterns = {
            'python': {
                'function': r'def\s+(\w+)',
                'class': r'class\s+(\w+)',
                'complexity': r'\b(if|elif|while|for|except|and|or)\b'
            },
            'javascript': {
                'function': r'function\s+(\w+)|(\w+)\s*=\s*(?:function|\(.*?\)\s*=>)',
                'class': r'class\s+(\w+)',
                'complexity': r'\b(if|else|while|for|switch|case|catch|&&|\|\|)\b'
            },
            'java': {
                'function': r'(?:public|private|protected)?\s*\w+\s+(\w+)\s*\(',
                'class': r'(?:public\s+)?class\s+(\w+)',
                'complexity': r'\b(if|else|while|for|switch|case|catch|&&|\|\|)\b'
            }
        }
        
        if language in patterns:
            lang_patterns = patterns[language]
            
            # Compter les fonctions
            functions = re.findall(lang_patterns['function'], content, re.MULTILINE)
            metrics['functions_count'] = len(functions)
            if isinstance(functions[0], tuple) if functions else False:
                metrics['function_names'] = [f[0] or f[1] for f in functions if f[0] or f[1]]
            else:
                metrics['function_names'] = functions
            
            # Compter les classes
            classes = re.findall(lang_patterns['class'], content, re.MULTILINE)
            metrics['classes_count'] = len(classes)
            metrics['class_names'] = classes
            
            # Complexité cyclomatique simple
            complexity_matches = re.findall(lang_patterns['complexity'], content, re.IGNORECASE)
            metrics['complexity'] = len(complexity_matches)
        
        return metrics
    
    def _calculate_python_complexity(self, node: ast.FunctionDef) -> int:
        """Calculer la complexité cyclomatique d'une fonction Python"""
        complexity = 1  # Complexité de base
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1
        
        return complexity
    
    def _calculate_technical_debt(self, metrics: Dict[str, Any]) -> float:
        """Calculer le ratio de dette technique (estimation)"""
        # Formule simplifiée basée sur différents facteurs
        total_lines = metrics.get('code_lines', 1)
        
        # Facteurs de dette
        complexity_debt = min(metrics.get('avg_complexity', 0) / 10, 1.0)
        comment_ratio = metrics.get('comment_lines', 0) / max(total_lines, 1)
        test_ratio = metrics.get('test_files', 0) / max(metrics.get('total_files', 1), 1)
        
        # Score de dette (0 = pas de dette, 1 = dette maximale)
        debt_score = (
            complexity_debt * 0.4 +
            (1 - min(comment_ratio * 5, 1.0)) * 0.3 +
            (1 - min(test_ratio * 2, 1.0)) * 0.3
        )
        
        return round(debt_score, 3)
    
    def _calculate_maintainability_index(self, metrics: Dict[str, Any]) -> float:
        """Calculer l'index de maintenabilité (formule simplifiée)"""
        # Formule inspirée de Microsoft Maintainability Index
        total_lines = max(metrics.get('code_lines', 1), 1)
        avg_complexity = metrics.get('avg_complexity', 1)
        comment_ratio = metrics.get('comment_lines', 0) / total_lines
        
        # Index sur 100
        index = (
            171 -
            5.2 * np.log(avg_complexity) -
            0.23 * avg_complexity -
            16.2 * np.log(total_lines) +
            50 * np.sin(np.sqrt(2.4 * comment_ratio))
        )
        
        return round(max(0, min(100, index)), 1)
    
    def _estimate_duplication(self, function_names: List[str]) -> int:
        """Estimation simple de la duplication basée sur les noms de fonctions"""
        if not function_names:
            return 0
        
        # Compter les noms similaires
        name_counts = {}
        for name in function_names:
            # Normaliser le nom (sans suffixes comme _test, _v2, etc.)
            normalized = re.sub(r'(_test|_v\d+|_\d+)$', '', name.lower())
            name_counts[normalized] = name_counts.get(normalized, 0) + 1
        
        # Estimer les lignes dupliquées
        duplicated = sum(count - 1 for count in name_counts.values() if count > 1)
        return duplicated * 10  # Estimation: 10 lignes par fonction dupliquée

# Import numpy avec fallback
try:
    import numpy as np
except ImportError:
    # Fallback simple si numpy n'est pas disponible
    class np:
        @staticmethod
        def log(x):
            import math
            return math.log(max(x, 0.001))
        
        @staticmethod
        def sin(x):
            import math
            return math.sin(x)
        
        @staticmethod
        def sqrt(x):
            import math
            return math.sqrt(max(x, 0))

class QualityAnalyzer:
    """Analyseur de qualité de code"""
    
    def __init__(self):
        self.metrics_calculator = CodeMetricsCalculator()
    
    def analyze_quality(self, project_path: str, language: str) -> Dict[str, Any]:
        """Analyser la qualité globale d'un projet"""
        metrics = self.metrics_calculator.calculate_project_metrics(project_path, language)
        
        quality_analysis = {
            'metrics': metrics,
            'quality_score': self._calculate_quality_score(metrics),
            'recommendations': self._generate_recommendations(metrics),
            'hotspots': self._identify_hotspots(metrics),
            'trends': self._analyze_trends(metrics)
        }
        
        return quality_analysis
    
    def _calculate_quality_score(self, metrics: Dict[str, Any]) -> float:
        """Calculer un score de qualité global (0-10)"""
        score = 5.0  # Score de base
        
        # Facteur test coverage
        total_files = metrics.get('total_files', 1)
        test_files = metrics.get('test_files', 0)
        test_coverage = test_files / total_files if total_files > 0 else 0
        score += min(2.0, test_coverage * 4)  # +2 points max
        
        # Facteur complexité
        avg_complexity = metrics.get('avg_complexity', 0)
        if avg_complexity < 3:
            score += 1.5
        elif avg_complexity > 7:
            score -= 2.0
        
        # Facteur documentation
        code_lines = metrics.get('code_lines', 1)
        comment_lines = metrics.get('comment_lines', 0)
        doc_ratio = comment_lines / code_lines if code_lines > 0 else 0
        if doc_ratio > 0.2:
            score += 1.0
        elif doc_ratio < 0.05:
            score -= 1.0
        
        # Facteur dette technique
        tech_debt = metrics.get('technical_debt_ratio', 0)
        score -= tech_debt * 2
        
        return round(max(0.0, min(10.0, score)), 1)
    
    def _generate_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Générer des recommandations d'amélioration"""
        recommendations = []
        
        # Recommandations basées sur les métriques
        total_files = metrics.get('total_files', 1)
        test_files = metrics.get('test_files', 0)
        test_ratio = test_files / total_files if total_files > 0 else 0
        
        if test_ratio < 0.3:
            recommendations.append("🧪 Augmenter la couverture de tests (actuellement {:.1%})".format(test_ratio))
        
        avg_complexity = metrics.get('avg_complexity', 0)
        if avg_complexity > 5:
            recommendations.append(f"🧠 Réduire la complexité moyenne (actuellement {avg_complexity:.1f})")
        
        code_lines = metrics.get('code_lines', 1)
        comment_lines = metrics.get('comment_lines', 0)
        doc_ratio = comment_lines / code_lines if code_lines > 0 else 0
        
        if doc_ratio < 0.1:
            recommendations.append("📚 Améliorer la documentation du code")
        
        tech_debt = metrics.get('technical_debt_ratio', 0)
        if tech_debt > 0.5:
            recommendations.append("🔧 Réduire la dette technique")
        
        duplicated = metrics.get('duplicated_lines', 0)
        if duplicated > 50:
            recommendations.append("🔄 Éliminer la duplication de code")
        
        return recommendations if recommendations else ["✅ Code de bonne qualité!"]
    
    def _identify_hotspots(self, metrics: Dict[str, Any]) -> List[str]:
        """Identifier les points chauds du code"""
        hotspots = []
        
        max_complexity = metrics.get('max_complexity', 0)
        if max_complexity > 10:
            hotspots.append(f"⚠️ Complexité maximale élevée: {max_complexity}")
        
        functions_count = metrics.get('functions_count', 0)
        total_files = metrics.get('total_files', 1)
        functions_per_file = functions_count / total_files if total_files > 0 else 0
        
        if functions_per_file > 20:
            hotspots.append(f"📁 Trop de fonctions par fichier: {functions_per_file:.1f}")
        
        return hotspots
    
    def _analyze_trends(self, metrics: Dict[str, Any]) -> Dict[str, str]:
        """Analyser les tendances (simulation)"""
        # Dans un vrai projet, ceci comparerait avec l'historique
        return {
            'complexity': 'stable',
            'test_coverage': 'improving',
            'code_size': 'growing',
            'quality': 'stable'
        }