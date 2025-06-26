import os
import re
import ast
import json
from typing import Dict, List, Set, Optional, Any
from pathlib import Path
from collections import defaultdict, Counter
import networkx as nx

class UniversalCodeAnalyzer:
    """Analyseur de code universel multi-langages"""
    
    def __init__(self, config):
        self.config = config
        self.language_detectors = {
            'python': self._detect_python_framework,
            'javascript': self._detect_js_framework,
            'typescript': self._detect_js_framework,
            'java': self._detect_java_framework,
            'csharp': self._detect_csharp_framework,
            'go': self._detect_go_framework,
            'rust': self._detect_rust_framework
        }
    
    def analyze_project(self, project_path: str) -> Dict[str, Any]:
        """Analyse complète d'un projet"""
        print(f"🔍 Analyse du projet: {project_path}")
        
        # Détection du langage principal
        language_stats = self._detect_languages(project_path)
        main_language = max(language_stats.items(), key=lambda x: x[1])[0] if language_stats else 'unknown'
        
        # Analyse selon le langage
        analysis = {
            'language': main_language,
            'language_stats': language_stats,
            'framework': self._detect_framework(project_path, main_language),
            'test_framework': self._detect_test_framework(project_path, main_language),
            'conventions': self._detect_conventions(project_path, main_language),
            'patterns': self._detect_patterns(project_path, main_language),
            'metrics': self._calculate_metrics(project_path),
            'structure': self._analyze_structure(project_path),
            'dependencies': self._analyze_dependencies(project_path, main_language),
            'quality_score': 0  # Calculé à la fin
        }
        
        # Score de qualité global
        analysis['quality_score'] = self._calculate_quality_score(analysis)
        
        print(f"✅ Analyse terminée: {main_language} ({analysis['framework']})")
        return analysis
    
    def _detect_languages(self, project_path: str) -> Dict[str, int]:
        """Détecter les langages utilisés dans le projet"""
        extensions = {
            '.py': 'python',
            '.js': 'javascript', 
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.cs': 'csharp',
            '.go': 'go',
            '.rs': 'rust',
            '.cpp': 'cpp',
            '.c': 'c',
            '.php': 'php',
            '.rb': 'ruby',
            '.swift': 'swift',
            '.kt': 'kotlin'
        }
        
        language_counts = defaultdict(int)
        
        for root, dirs, files in os.walk(project_path):
            # Ignorer les dossiers standards
            dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', 'venv', '__pycache__', 'target', 'build', 'dist']]
            
            for file in files:
                ext = Path(file).suffix.lower()
                if ext in extensions:
                    language_counts[extensions[ext]] += 1
        
        return dict(language_counts)
    
    def _detect_framework(self, project_path: str, language: str) -> str:
        """Détecter le framework principal"""
        if language in self.language_detectors:
            return self.language_detectors[language](project_path)
        return 'standard'
    
    def _detect_python_framework(self, project_path: str) -> str:
        """Détecter le framework Python"""
        # Vérifier les fichiers de configuration
        config_files = {
            'django': ['manage.py', 'settings.py', 'wsgi.py'],
            'flask': ['app.py', 'application.py'],
            'fastapi': ['main.py', 'app.py'],
            'tornado': ['tornado'],
            'pyramid': ['pyramid']
        }
        
        # Vérifier requirements.txt/pyproject.toml
        dep_indicators = {
            'django': ['django', 'Django'],
            'flask': ['flask', 'Flask'],
            'fastapi': ['fastapi', 'FastAPI'],
            'tornado': ['tornado'],
            'pyramid': ['pyramid']
        }
        
        return self._check_framework_indicators(project_path, config_files, dep_indicators)
    
    def _detect_js_framework(self, project_path: str) -> str:
        """Détecter le framework JavaScript/TypeScript"""
        config_files = {
            'react': ['src/App.js', 'src/App.tsx', 'public/index.html'],
            'vue': ['src/App.vue', 'vue.config.js'],
            'angular': ['angular.json', 'src/app/app.module.ts'],
            'express': ['app.js', 'server.js', 'index.js'],
            'nestjs': ['nest-cli.json', 'src/main.ts'],
            'nextjs': ['next.config.js', 'pages/_app.js'],
            'nuxtjs': ['nuxt.config.js']
        }
        
        dep_indicators = {
            'react': ['react', 'react-dom'],
            'vue': ['vue'],
            'angular': ['@angular/core'],
            'express': ['express'],
            'nestjs': ['@nestjs/core'],
            'nextjs': ['next'],
            'nuxtjs': ['nuxt']
        }
        
        return self._check_framework_indicators(project_path, config_files, dep_indicators, 'package.json')
    
    def _detect_java_framework(self, project_path: str) -> str:
        """Détecter le framework Java"""
        config_files = {
            'spring': ['src/main/java', 'application.properties', 'application.yml'],
            'springboot': ['src/main/java', 'application.properties'],
            'maven': ['pom.xml'],
            'gradle': ['build.gradle', 'build.gradle.kts']
        }
        
        dep_indicators = {
            'spring': ['spring-boot', 'spring-framework', 'springframework'],
            'maven': ['maven'],
            'gradle': ['gradle']
        }
        
        return self._check_framework_indicators(project_path, config_files, dep_indicators, 'pom.xml')
    
    def _detect_csharp_framework(self, project_path: str) -> str:
        """Détecter le framework C#"""
        config_files = {
            'dotnet': ['*.csproj', '*.sln'],
            'aspnet': ['Program.cs', 'Startup.cs'],
            'blazor': ['_Imports.razor', 'App.razor']
        }
        
        return self._check_framework_indicators(project_path, config_files, {})
    
    def _detect_go_framework(self, project_path: str) -> str:
        """Détecter le framework Go"""
        config_files = {
            'gin': ['main.go'],
            'echo': ['main.go'],
            'fiber': ['main.go']
        }
        
        dep_indicators = {
            'gin': ['gin-gonic/gin'],
            'echo': ['labstack/echo'],
            'fiber': ['gofiber/fiber']
        }
        
        return self._check_framework_indicators(project_path, config_files, dep_indicators, 'go.mod')
    
    def _detect_rust_framework(self, project_path: str) -> str:
        """Détecter le framework Rust"""
        config_files = {
            'actix': ['src/main.rs'],
            'rocket': ['src/main.rs'],
            'warp': ['src/main.rs']
        }
        
        dep_indicators = {
            'actix': ['actix-web'],
            'rocket': ['rocket'],
            'warp': ['warp']
        }
        
        return self._check_framework_indicators(project_path, config_files, dep_indicators, 'Cargo.toml')
    
    def _check_framework_indicators(self, project_path: str, config_files: Dict, dep_indicators: Dict, dep_file: str = None) -> str:
        """Vérifier les indicateurs de framework"""
        # Vérifier les fichiers de configuration
        for framework, files in config_files.items():
            for file_pattern in files:
                if self._file_exists_pattern(project_path, file_pattern):
                    return framework
        
        # Vérifier les dépendances
        if dep_file:
            dep_path = os.path.join(project_path, dep_file)
            if os.path.exists(dep_path):
                try:
                    with open(dep_path, 'r', encoding='utf-8') as f:
                        content = f.read().lower()
                    
                    for framework, deps in dep_indicators.items():
                        if any(dep.lower() in content for dep in deps):
                            return framework
                except:
                    pass
        
        return 'standard'
    
    def _file_exists_pattern(self, project_path: str, pattern: str) -> bool:
        """Vérifier si un fichier existe selon un pattern"""
        if '*' in pattern:
            # Pattern avec wildcard
            from glob import glob
            matches = glob(os.path.join(project_path, '**', pattern), recursive=True)
            return len(matches) > 0
        else:
            # Fichier exact
            return os.path.exists(os.path.join(project_path, pattern))
    
    def _detect_test_framework(self, project_path: str, language: str) -> str:
        """Détecter le framework de test"""
        test_frameworks = {
            'python': ['pytest', 'unittest', 'nose2'],
            'javascript': ['jest', 'mocha', 'vitest', 'cypress'],
            'typescript': ['jest', 'mocha', 'vitest'],
            'java': ['junit', 'testng', 'mockito'],
            'csharp': ['xunit', 'nunit', 'mstest'],
            'go': ['testing', 'ginkgo', 'testify'],
            'rust': ['cargo test', 'rstest']
        }
        
        if language not in test_frameworks:
            return 'standard'
        
        # Chercher des indices dans les fichiers
        for framework in test_frameworks[language]:
            if self._search_in_files(project_path, framework):
                return framework
        
        return 'standard'
    
    def _detect_conventions(self, project_path: str, language: str) -> List[str]:
        """Détecter les conventions de code utilisées"""
        conventions = []
        
        # Conventions par langage
        lang_conventions = {
            'python': ['pep8', 'black', 'flake8', 'pylint'],
            'javascript': ['eslint', 'prettier', 'standard'],
            'java': ['checkstyle', 'spotbugs', 'pmd'],
            'csharp': ['stylecop', 'editorconfig'],
            'go': ['gofmt', 'golint'],
            'rust': ['rustfmt', 'clippy']
        }
        
        if language in lang_conventions:
            for convention in lang_conventions[language]:
                if self._search_in_files(project_path, convention):
                    conventions.append(convention)
        
        return conventions if conventions else ['standard']
    
    def _detect_patterns(self, project_path: str, language: str) -> List[str]:
        """Détecter les patterns de design utilisés"""
        patterns = []
        
        # Patterns universels à rechercher
        pattern_indicators = {
            'mvc': ['controller', 'model', 'view'],
            'repository': ['repository', 'repo'],
            'factory': ['factory', 'create'],
            'singleton': ['singleton', 'instance'],
            'observer': ['observer', 'subscribe', 'event'],
            'adapter': ['adapter', 'wrapper'],
            'strategy': ['strategy', 'algorithm'],
            'decorator': ['decorator', 'wrap'],
            'dependency_injection': ['inject', 'dependency', 'di']
        }
        
        for pattern, indicators in pattern_indicators.items():
            if any(self._search_in_files(project_path, indicator) for indicator in indicators):
                patterns.append(pattern)
        
        return patterns if patterns else ['standard']
    
    def _search_in_files(self, project_path: str, term: str) -> bool:
        """Rechercher un terme dans les fichiers du projet"""
        try:
            for root, dirs, files in os.walk(project_path):
                dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', 'venv']]
                
                for file in files:
                    if file.endswith(('.py', '.js', '.ts', '.java', '.cs', '.go', '.rs', '.json', '.yml', '.yaml', '.toml')):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read().lower()
                                if term.lower() in content:
                                    return True
                        except:
                            continue
        except:
            pass
        return False
    
    def _calculate_metrics(self, project_path: str) -> Dict[str, Any]:
        """Calculer les métriques du projet"""
        metrics = {
            'total_files': 0,
            'test_files': 0,
            'code_lines': 0,
            'comment_lines': 0,
            'avg_complexity': 0,
            'test_coverage': 0
        }
        
        for root, dirs, files in os.walk(project_path):
            dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', 'venv']]
            
            for file in files:
                if file.endswith(('.py', '.js', '.ts', '.java', '.cs', '.go', '.rs')):
                    metrics['total_files'] += 1
                    
                    if any(test_indicator in file.lower() for test_indicator in ['test', 'spec']):
                        metrics['test_files'] += 1
                    
                    # Analyser le fichier
                    file_path = os.path.join(root, file)
                    file_metrics = self._analyze_file_metrics(file_path)
                    metrics['code_lines'] += file_metrics['code_lines']
                    metrics['comment_lines'] += file_metrics['comment_lines']
        
        # Calculer les ratios
        if metrics['total_files'] > 0:
            metrics['test_coverage'] = metrics['test_files'] / metrics['total_files']
        
        # Complexité moyenne (estimation simple)
        metrics['avg_complexity'] = min(10, metrics['code_lines'] / max(1, metrics['total_files']) / 20)
        
        return metrics
    
    def _analyze_file_metrics(self, file_path: str) -> Dict[str, int]:
        """Analyser les métriques d'un fichier"""
        metrics = {'code_lines': 0, 'comment_lines': 0}
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        if line.startswith(('#', '//', '/*', '*', '<!--')):
                            metrics['comment_lines'] += 1
                        else:
                            metrics['code_lines'] += 1
        except:
            pass
        
        return metrics
    
    def _analyze_structure(self, project_path: str) -> Dict[str, Any]:
        """Analyser la structure du projet"""
        structure = {
            'directories': [],
            'depth': 0,
            'organization': 'standard'
        }
        
        # Compter la profondeur et les dossiers
        for root, dirs, files in os.walk(project_path):
            level = root.replace(project_path, '').count(os.sep)
            structure['depth'] = max(structure['depth'], level)
            
            for dir_name in dirs:
                if dir_name not in ['node_modules', '.git', 'venv', '__pycache__']:
                    structure['directories'].append(dir_name)
        
        # Détecter le type d'organisation
        common_patterns = {
            'mvc': ['models', 'views', 'controllers'],
            'layered': ['domain', 'infrastructure', 'application'],
            'feature': ['features', 'modules', 'components'],
            'flat': []
        }
        
        dirs_lower = [d.lower() for d in structure['directories']]
        for pattern_name, pattern_dirs in common_patterns.items():
            if all(d in dirs_lower for d in pattern_dirs):
                structure['organization'] = pattern_name
                break
        
        return structure
    
    def _analyze_dependencies(self, project_path: str, language: str) -> Dict[str, Any]:
        """Analyser les dépendances"""
        deps = {'external': [], 'internal': 0, 'total': 0}
        
        dependency_files = {
            'python': ['requirements.txt', 'pyproject.toml', 'Pipfile'],
            'javascript': ['package.json'],
            'java': ['pom.xml', 'build.gradle'],
            'csharp': ['*.csproj', 'packages.config'],
            'go': ['go.mod'],
            'rust': ['Cargo.toml']
        }
        
        if language in dependency_files:
            for dep_file in dependency_files[language]:
                file_path = os.path.join(project_path, dep_file)
                if os.path.exists(file_path):
                    deps.update(self._parse_dependency_file(file_path, language))
        
        return deps
    
    def _parse_dependency_file(self, file_path: str, language: str) -> Dict[str, Any]:
        """Parser un fichier de dépendances"""
        deps = {'external': [], 'total': 0}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if file_path.endswith('.json'):
                # package.json
                import json
                data = json.loads(content)
                if 'dependencies' in data:
                    deps['external'] = list(data['dependencies'].keys())
                if 'devDependencies' in data:
                    deps['external'].extend(data['devDependencies'].keys())
            
            elif file_path.endswith('.txt'):
                # requirements.txt
                deps['external'] = [line.split('==')[0].split('>=')[0].strip() 
                                  for line in content.split('\n') 
                                  if line.strip() and not line.startswith('#')]
            
            deps['total'] = len(deps['external'])
            
        except:
            pass
        
        return deps
    
    def _calculate_quality_score(self, analysis: Dict[str, Any]) -> float:
        """Calculer un score de qualité global (0-10)"""
        score = 5.0  # Score de base
        
        metrics = analysis.get('metrics', {})
        
        # Bonus pour les tests
        test_coverage = metrics.get('test_coverage', 0)
        score += min(2.0, test_coverage * 4)  # +2 points max pour 50%+ de tests
        
        # Bonus pour la complexité raisonnable
        complexity = metrics.get('avg_complexity', 5)
        if complexity < 3:
            score += 1.0
        elif complexity > 7:
            score -= 1.0
        
        # Bonus pour les conventions
        conventions = analysis.get('conventions', [])
        if len(conventions) > 1:
            score += 0.5
        
        # Bonus pour les patterns
        patterns = analysis.get('patterns', [])
        if len(patterns) > 2:
            score += 0.5
        
        # Bonus pour l'organisation
        if analysis.get('structure', {}).get('organization') != 'standard':
            score += 0.5
        
        return round(min(10.0, max(0.0, score)), 1)