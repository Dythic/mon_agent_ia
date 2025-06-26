import yaml
import os
from typing import Dict, Any, List
from dataclasses import dataclass, field

@dataclass
class LanguageConfig:
    """Configuration pour un langage spécifique"""
    name: str
    extensions: List[str]
    frameworks: List[str] = field(default_factory=list)
    test_frameworks: List[str] = field(default_factory=list)
    conventions: List[str] = field(default_factory=list)
    patterns: List[str] = field(default_factory=list)
    separators: List[str] = field(default_factory=list)
    excluded_dirs: List[str] = field(default_factory=list)

class UniversalConfig:
    """Configuration universelle pour l'agent"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        self.languages = self._setup_languages()
    
    def _load_config(self) -> Dict[str, Any]:
        """Charger la configuration depuis le fichier YAML"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                print(f"⚠️ Erreur lecture config {self.config_path}: {e}")
        
        # Configuration par défaut si fichier absent
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Configuration par défaut"""
        return {
            'agent': {
                'model': 'deepseek-coder:6.7b',
                'temperature': 0.2,
                'max_tokens': 2048
            },
            'indexing': {
                'chunk_size': 1200,
                'chunk_overlap': 200,
                'max_files': 10000
            },
            'embeddings': {
                'model': 'sentence-transformers/all-MiniLM-L6-v2',
                'device': 'cpu'
            },
            'languages': self._get_default_languages()
        }
    
    def _get_default_languages(self) -> Dict[str, Any]:
        """Configuration par défaut des langages"""
        return {
            'python': {
                'extensions': ['.py', '.pyw', '.pyx'],
                'frameworks': ['django', 'flask', 'fastapi', 'tornado', 'pyramid'],
                'test_frameworks': ['pytest', 'unittest', 'nose2'],
                'conventions': ['pep8', 'black', 'flake8', 'pylint'],
                'patterns': ['mvc', 'repository', 'factory', 'singleton'],
                'separators': ['\nclass ', '\ndef ', '\n\n', '\n', ' '],
                'excluded_dirs': ['venv', 'env', '.venv', 'site-packages', '.tox']
            },
            'javascript': {
                'extensions': ['.js', '.jsx', '.mjs'],
                'frameworks': ['react', 'vue', 'angular', 'express', 'nestjs', 'nextjs'],
                'test_frameworks': ['jest', 'mocha', 'vitest', 'cypress'],
                'conventions': ['eslint', 'prettier', 'standard'],
                'patterns': ['mvc', 'component', 'observer', 'module'],
                'separators': ['\nclass ', '\nfunction ', '\nconst ', '\n\n', '\n', ' '],
                'excluded_dirs': ['node_modules', 'dist', 'build', '.next', '.nuxt']
            },
            'typescript': {
                'extensions': ['.ts', '.tsx'],
                'frameworks': ['angular', 'nestjs', 'nextjs', 'express'],
                'test_frameworks': ['jest', 'mocha', 'vitest'],
                'conventions': ['eslint', 'prettier', 'tslint'],
                'patterns': ['mvc', 'component', 'decorator', 'observer'],
                'separators': ['\nclass ', '\nfunction ', '\ninterface ', '\n\n', '\n', ' '],
                'excluded_dirs': ['node_modules', 'dist', 'build']
            },
            'java': {
                'extensions': ['.java'],
                'frameworks': ['spring', 'springboot', 'maven', 'gradle'],
                'test_frameworks': ['junit', 'testng', 'mockito'],
                'conventions': ['checkstyle', 'spotbugs', 'pmd'],
                'patterns': ['mvc', 'repository', 'factory', 'adapter', 'dependency_injection'],
                'separators': ['\npublic class ', '\npublic ', '\nprivate ', '\n\n', '\n', ' '],
                'excluded_dirs': ['target', 'build', '.gradle']
            },
            'csharp': {
                'extensions': ['.cs'],
                'frameworks': ['dotnet', 'aspnet', 'blazor'],
                'test_frameworks': ['xunit', 'nunit', 'mstest'],
                'conventions': ['stylecop', 'editorconfig'],
                'patterns': ['mvc', 'repository', 'factory', 'dependency_injection'],
                'separators': ['\npublic class ', '\npublic ', '\nprivate ', '\n\n', '\n', ' '],
                'excluded_dirs': ['bin', 'obj', 'packages']
            },
            'go': {
                'extensions': ['.go'],
                'frameworks': ['gin', 'echo', 'fiber'],
                'test_frameworks': ['testing', 'ginkgo', 'testify'],
                'conventions': ['gofmt', 'golint', 'golangci-lint'],
                'patterns': ['repository', 'factory', 'adapter'],
                'separators': ['\nfunc ', '\ntype ', '\n\n', '\n', ' '],
                'excluded_dirs': ['vendor']
            },
            'rust': {
                'extensions': ['.rs'],
                'frameworks': ['actix', 'rocket', 'warp'],
                'test_frameworks': ['cargo test', 'rstest'],
                'conventions': ['rustfmt', 'clippy'],
                'patterns': ['repository', 'factory', 'builder'],
                'separators': ['\nfn ', '\nstruct ', '\nimpl ', '\n\n', '\n', ' '],
                'excluded_dirs': ['target']
            }
        }
    
    def _setup_languages(self) -> Dict[str, LanguageConfig]:
        """Configurer les langages"""
        languages = {}
        
        for lang_name, lang_config in self.config.get('languages', {}).items():
            languages[lang_name] = LanguageConfig(
                name=lang_name,
                extensions=lang_config.get('extensions', []),
                frameworks=lang_config.get('frameworks', []),
                test_frameworks=lang_config.get('test_frameworks', []),
                conventions=lang_config.get('conventions', []),
                patterns=lang_config.get('patterns', []),
                separators=lang_config.get('separators', []),
                excluded_dirs=lang_config.get('excluded_dirs', [])
            )
        
        return languages
    
    def get_language_config(self, language: str) -> LanguageConfig:
        """Obtenir la configuration d'un langage"""
        return self.languages.get(language, LanguageConfig(name=language, extensions=[]))
    
    def get_supported_languages(self) -> List[str]:
        """Obtenir la liste des langages supportés"""
        return list(self.languages.keys())
    
    def get_agent_config(self) -> Dict[str, Any]:
        """Obtenir la configuration de l'agent"""
        return self.config.get('agent', {})
    
    def get_indexing_config(self) -> Dict[str, Any]:
        """Obtenir la configuration d'indexation"""
        return self.config.get('indexing', {})
    
    def get_embeddings_config(self) -> Dict[str, Any]:
        """Obtenir la configuration des embeddings"""
        return self.config.get('embeddings', {})
    
    def save_config(self):
        """Sauvegarder la configuration actuelle"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
            print(f"✅ Configuration sauvegardée dans {self.config_path}")
        except Exception as e:
            print(f"❌ Erreur sauvegarde config: {e}")
    
    def add_language(self, language: str, config: Dict[str, Any]):
        """Ajouter un nouveau langage"""
        self.config['languages'][language] = config
        self.languages[language] = LanguageConfig(
            name=language,
            **config
        )
    
    def update_language_config(self, language: str, updates: Dict[str, Any]):
        """Mettre à jour la configuration d'un langage"""
        if language in self.config['languages']:
            self.config['languages'][language].update(updates)
            # Recréer l'objet LanguageConfig
            self.languages[language] = LanguageConfig(
                name=language,
                **self.config['languages'][language]
            )

def create_default_config_file(path: str = "config.yaml"):
    """Créer un fichier de configuration par défaut"""
    config = UniversalConfig()
    
    try:
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(config.config, f, default_flow_style=False, allow_unicode=True)
        print(f"✅ Fichier de configuration créé: {path}")
        return True
    except Exception as e:
        print(f"❌ Erreur création config: {e}")
        return False

if __name__ == "__main__":
    # Créer un fichier de configuration par défaut
    create_default_config_file()