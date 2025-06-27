"""
Configuration centralisée de l'application
"""
import os
import yaml
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class AgentConfig:
    """Configuration de l'agent"""
    model: str = "deepseek-coder:6.7b"
    temperature: float = 0.2
    max_tokens: int = 2048
    timeout: int = 30

@dataclass
class VectorStoreConfig:
    """Configuration du vectorstore"""
    chunk_size: int = 1200
    chunk_overlap: int = 200
    max_docs: int = 10000
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    device: str = "cpu"

@dataclass
class LanguageConfig:
    """Configuration pour un langage spécifique"""
    name: str
    extensions: List[str] = field(default_factory=list)
    frameworks: List[str] = field(default_factory=list)
    test_frameworks: List[str] = field(default_factory=list)
    conventions: List[str] = field(default_factory=list)
    patterns: List[str] = field(default_factory=list)
    excluded_dirs: List[str] = field(default_factory=list)

@dataclass
class QualityConfig:
    """Configuration des métriques de qualité"""
    max_complexity: int = 10
    min_test_coverage: float = 0.8
    max_function_length: int = 50
    max_file_length: int = 500
    min_comment_ratio: float = 0.1

@dataclass
class WebConfig:
    """Configuration interface web"""
    port: int = 8501
    host: str = "localhost"
    debug: bool = False
    theme: str = "light"
    max_upload_size: int = 200  # MB

class Settings:
    """Gestionnaire de configuration global"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._find_config_file()
        self._config_data = self._load_config()
        
        # Initialiser les configurations
        self.agent = self._create_agent_config()
        self.vectorstore = self._create_vectorstore_config()
        self.languages = self._create_languages_config()
        self.quality = self._create_quality_config()
        self.web = self._create_web_config()
    
    def _find_config_file(self) -> str:
        """Trouver le fichier de configuration"""
        possible_paths = [
            "config.yaml",
            "config/config.yaml",
            os.path.expanduser("~/.universal-agent/config.yaml"),
            "/etc/universal-agent/config.yaml"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # Créer un fichier par défaut
        default_path = "config.yaml"
        self._create_default_config(default_path)
        return default_path
    
    def _load_config(self) -> Dict[str, Any]:
        """Charger la configuration depuis le fichier"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                print(f"⚠️ Erreur lecture config {self.config_path}: {e}")
        
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Configuration par défaut"""
        return {
            'agent': {
                'model': 'deepseek-coder:6.7b',
                'temperature': 0.2,
                'max_tokens': 2048,
                'timeout': 30
            },
            'vectorstore': {
                'chunk_size': 1200,
                'chunk_overlap': 200,
                'max_docs': 10000,
                'embedding_model': 'sentence-transformers/all-MiniLM-L6-v2',
                'device': 'cpu'
            },
            'quality': {
                'max_complexity': 10,
                'min_test_coverage': 0.8,
                'max_function_length': 50,
                'max_file_length': 500,
                'min_comment_ratio': 0.1
            },
            'web': {
                'port': 8501,
                'host': 'localhost',
                'debug': False,
                'theme': 'light',
                'max_upload_size': 200
            },
            'languages': self._get_default_languages()
        }
    
    def _get_default_languages(self) -> Dict[str, Any]:
        """Configuration par défaut des langages"""
        return {
            'python': {
                'extensions': ['.py', '.pyw', '.pyx'],
                'frameworks': ['django', 'flask', 'fastapi', 'tornado'],
                'test_frameworks': ['pytest', 'unittest', 'nose2'],
                'conventions': ['pep8', 'black', 'flake8'],
                'patterns': ['mvc', 'repository', 'factory'],
                'excluded_dirs': ['venv', 'env', '.venv', '__pycache__']
            },
            'javascript': {
                'extensions': ['.js', '.jsx', '.mjs'],
                'frameworks': ['react', 'vue', 'angular', 'express'],
                'test_frameworks': ['jest', 'mocha', 'vitest'],
                'conventions': ['eslint', 'prettier'],
                'patterns': ['mvc', 'component', 'observer'],
                'excluded_dirs': ['node_modules', 'dist', 'build']
            },
            'typescript': {
                'extensions': ['.ts', '.tsx'],
                'frameworks': ['angular', 'nestjs', 'nextjs'],
                'test_frameworks': ['jest', 'mocha', 'vitest'],
                'conventions': ['eslint', 'prettier', 'tslint'],
                'patterns': ['mvc', 'component', 'decorator'],
                'excluded_dirs': ['node_modules', 'dist', 'build']
            },
            'java': {
                'extensions': ['.java'],
                'frameworks': ['spring', 'springboot', 'maven'],
                'test_frameworks': ['junit', 'testng', 'mockito'],
                'conventions': ['checkstyle', 'spotbugs'],
                'patterns': ['mvc', 'repository', 'factory'],
                'excluded_dirs': ['target', 'build', '.gradle']
            }
        }
    
    def _create_agent_config(self) -> AgentConfig:
        """Créer la configuration de l'agent"""
        agent_data = self._config_data.get('agent', {})
        return AgentConfig(
            model=agent_data.get('model', 'deepseek-coder:6.7b'),
            temperature=agent_data.get('temperature', 0.2),
            max_tokens=agent_data.get('max_tokens', 2048),
            timeout=agent_data.get('timeout', 30)
        )
    
    def _create_vectorstore_config(self) -> VectorStoreConfig:
        """Créer la configuration du vectorstore"""
        vs_data = self._config_data.get('vectorstore', {})
        return VectorStoreConfig(
            chunk_size=vs_data.get('chunk_size', 1200),
            chunk_overlap=vs_data.get('chunk_overlap', 200),
            max_docs=vs_data.get('max_docs', 10000),
            embedding_model=vs_data.get('embedding_model', 'sentence-transformers/all-MiniLM-L6-v2'),
            device=vs_data.get('device', 'cpu')
        )
    
    def _create_languages_config(self) -> Dict[str, LanguageConfig]:
        """Créer la configuration des langages"""
        languages = {}
        languages_data = self._config_data.get('languages', {})
        
        for lang_name, lang_data in languages_data.items():
            languages[lang_name] = LanguageConfig(
                name=lang_name,
                extensions=lang_data.get('extensions', []),
                frameworks=lang_data.get('frameworks', []),
                test_frameworks=lang_data.get('test_frameworks', []),
                conventions=lang_data.get('conventions', []),
                patterns=lang_data.get('patterns', []),
                excluded_dirs=lang_data.get('excluded_dirs', [])
            )
        
        return languages
    
    def _create_quality_config(self) -> QualityConfig:
        """Créer la configuration qualité"""
        quality_data = self._config_data.get('quality', {})
        return QualityConfig(
            max_complexity=quality_data.get('max_complexity', 10),
            min_test_coverage=quality_data.get('min_test_coverage', 0.8),
            max_function_length=quality_data.get('max_function_length', 50),
            max_file_length=quality_data.get('max_file_length', 500),
            min_comment_ratio=quality_data.get('min_comment_ratio', 0.1)
        )
    
    def _create_web_config(self) -> WebConfig:
        """Créer la configuration web"""
        web_data = self._config_data.get('web', {})
        return WebConfig(
            port=web_data.get('port', 8501),
            host=web_data.get('host', 'localhost'),
            debug=web_data.get('debug', False),
            theme=web_data.get('theme', 'light'),
            max_upload_size=web_data.get('max_upload_size', 200)
        )
    
    def _create_default_config(self, path: str):
        """Créer un fichier de configuration par défaut"""
        default_config = self._get_default_config()
        
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True)
            print(f"✅ Configuration par défaut créée: {path}")
        except Exception as e:
            print(f"❌ Erreur création config: {e}")
    
    def get_language_config(self, language: str) -> Optional[LanguageConfig]:
        """Obtenir la configuration d'un langage"""
        return self.languages.get(language)
    
    def get_supported_languages(self) -> List[str]:
        """Obtenir la liste des langages supportés"""
        return list(self.languages.keys())
    
    def save_config(self):
        """Sauvegarder la configuration actuelle"""
        config_data = {
            'agent': {
                'model': self.agent.model,
                'temperature': self.agent.temperature,
                'max_tokens': self.agent.max_tokens,
                'timeout': self.agent.timeout
            },
            'vectorstore': {
                'chunk_size': self.vectorstore.chunk_size,
                'chunk_overlap': self.vectorstore.chunk_overlap,
                'max_docs': self.vectorstore.max_docs,
                'embedding_model': self.vectorstore.embedding_model,
                'device': self.vectorstore.device
            },
            'quality': {
                'max_complexity': self.quality.max_complexity,
                'min_test_coverage': self.quality.min_test_coverage,
                'max_function_length': self.quality.max_function_length,
               'max_file_length': self.quality.max_file_length,
               'min_comment_ratio': self.quality.min_comment_ratio
           },
           'web': {
               'port': self.web.port,
               'host': self.web.host,
               'debug': self.web.debug,
               'theme': self.web.theme,
               'max_upload_size': self.web.max_upload_size
           },
           'languages': {}
       }
       
       # Sérialiser les langages
       for name, lang_config in self.languages.items():
           config_data['languages'][name] = {
               'extensions': lang_config.extensions,
               'frameworks': lang_config.frameworks,
               'test_frameworks': lang_config.test_frameworks,
               'conventions': lang_config.conventions,
               'patterns': lang_config.patterns,
               'excluded_dirs': lang_config.excluded_dirs
           }
       
       try:
           with open(self.config_path, 'w', encoding='utf-8') as f:
               yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
           print(f"✅ Configuration sauvegardée: {self.config_path}")
       except Exception as e:
           print(f"❌ Erreur sauvegarde: {e}")
   
   def update_config(self, section: str, updates: Dict[str, Any]):
       """Mettre à jour une section de la configuration"""
       if section == 'agent':
           for key, value in updates.items():
               if hasattr(self.agent, key):
                   setattr(self.agent, key, value)
       elif section == 'vectorstore':
           for key, value in updates.items():
               if hasattr(self.vectorstore, key):
                   setattr(self.vectorstore, key, value)
       elif section == 'quality':
           for key, value in updates.items():
               if hasattr(self.quality, key):
                   setattr(self.quality, key, value)
       elif section == 'web':
           for key, value in updates.items():
               if hasattr(self.web, key):
                   setattr(self.web, key, value)
   
   def validate_config(self) -> List[str]:
       """Valider la configuration"""
       errors = []
       
       # Validation agent
       if self.agent.temperature < 0 or self.agent.temperature > 2:
           errors.append("Temperature doit être entre 0 et 2")
       
       if self.agent.max_tokens < 100 or self.agent.max_tokens > 10000:
           errors.append("max_tokens doit être entre 100 et 10000")
       
       # Validation vectorstore
       if self.vectorstore.chunk_size < 100:
           errors.append("chunk_size doit être >= 100")
       
       if self.vectorstore.chunk_overlap >= self.vectorstore.chunk_size:
           errors.append("chunk_overlap doit être < chunk_size")
       
       # Validation qualité
       if self.quality.min_test_coverage < 0 or self.quality.min_test_coverage > 1:
           errors.append("min_test_coverage doit être entre 0 et 1")
       
       return errors

# Instance globale
settings = Settings()

def get_settings() -> Settings:
   """Obtenir l'instance de configuration globale"""
   return settings

def reload_settings(config_path: Optional[str] = None):
   """Recharger la configuration"""
   global settings
   settings = Settings(config_path)
   return settings