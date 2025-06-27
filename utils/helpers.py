"""
Fonctions utilitaires générales
"""
import os
import re
import hashlib
import json
import yaml
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import tempfile
import shutil
from datetime import datetime

class FileUtils:
    """Utilitaires pour les fichiers"""
    
    @staticmethod
    def read_file_safe(file_path: str, encoding: str = 'utf-8') -> Optional[str]:
        """Lire un fichier de manière sécurisée"""
        encodings = [encoding, 'utf-8', 'latin-1', 'cp1252']
        
        for enc in encodings:
            try:
                with open(file_path, 'r', encoding=enc, errors='ignore') as f:
                    return f.read()
            except (UnicodeDecodeError, FileNotFoundError):
                continue
        return None
    
    @staticmethod
    def write_file_safe(file_path: str, content: str, encoding: str = 'utf-8') -> bool:
        """Écrire un fichier de manière sécurisée"""
        try:
            # Créer le dossier parent si nécessaire
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"❌ Erreur écriture {file_path}: {e}")
            return False
    
    @staticmethod
    def get_file_extension(file_path: str) -> str:
        """Obtenir l'extension d'un fichier"""
        return Path(file_path).suffix.lower()
    
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """Obtenir la taille d'un fichier en octets"""
        try:
            return os.path.getsize(file_path)
        except OSError:
            return 0
    
    @staticmethod
    def is_text_file(file_path: str) -> bool:
        """Vérifier si un fichier est un fichier texte"""
        text_extensions = {
            '.py', '.js', '.ts', '.java', '.cs', '.go', '.rs', '.cpp', '.c', '.h',
            '.html', '.css', '.scss', '.less', '.vue', '.jsx', '.tsx',
            '.json', '.yaml', '.yml', '.toml', '.xml', '.ini', '.conf',
            '.md', '.rst', '.txt', '.log'
        }
        return FileUtils.get_file_extension(file_path) in text_extensions
    
    @staticmethod
    def backup_file(file_path: str, backup_dir: str = None) -> Optional[str]:
        """Créer une sauvegarde d'un fichier"""
        if not os.path.exists(file_path):
            return None
        
        if backup_dir is None:
            backup_dir = os.path.join(os.path.dirname(file_path), '.backups')
        
        os.makedirs(backup_dir, exist_ok=True)
        
        # Nom de sauvegarde avec timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.basename(file_path)
        backup_name = f"{timestamp}_{filename}"
        backup_path = os.path.join(backup_dir, backup_name)
        
        try:
            shutil.copy2(file_path, backup_path)
            return backup_path
        except Exception as e:
            print(f"❌ Erreur sauvegarde: {e}")
            return None

class StringUtils:
    """Utilitaires pour les chaînes de caractères"""
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Nettoyer un nom de fichier"""
        # Remplacer les caractères problématiques
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Limiter la longueur
        if len(sanitized) > 100:
            name, ext = os.path.splitext(sanitized)
            sanitized = name[:100-len(ext)] + ext
        return sanitized
    
    @staticmethod
    def camel_to_snake(name: str) -> str:
        """Convertir CamelCase en snake_case"""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    @staticmethod
    def snake_to_camel(name: str) -> str:
        """Convertir snake_case en CamelCase"""
        components = name.split('_')
        return ''.join(word.capitalize() for word in components)
    
    @staticmethod
    def pascal_case(name: str) -> str:
        """Convertir en PascalCase"""
        return StringUtils.snake_to_camel(name)
    
    @staticmethod
    def kebab_case(name: str) -> str:
        """Convertir en kebab-case"""
        return StringUtils.camel_to_snake(name).replace('_', '-')
    
    @staticmethod
    def extract_words(text: str) -> List[str]:
        """Extraire les mots d'un texte"""
        return re.findall(r'\b\w+\b', text.lower())
    
    @staticmethod
    def calculate_similarity(text1: str, text2: str) -> float:
        """Calculer la similarité entre deux textes (simple)"""
        words1 = set(StringUtils.extract_words(text1))
        words2 = set(StringUtils.extract_words(text2))
        
        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    @staticmethod
    def truncate(text: str, max_length: int, suffix: str = "...") -> str:
        """Tronquer un texte"""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix

class DataUtils:
    """Utilitaires pour les données"""
    
    @staticmethod
    def deep_merge(dict1: Dict, dict2: Dict) -> Dict:
        """Fusion profonde de dictionnaires"""
        result = dict1.copy()
        
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = DataUtils.deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    @staticmethod
    def flatten_dict(d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
        """Aplatir un dictionnaire imbriqué"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(DataUtils.flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
    
    @staticmethod
    def safe_get(data: Dict, path: str, default: Any = None, sep: str = '.') -> Any:
        """Accès sécurisé aux données imbriquées"""
        try:
            keys = path.split(sep)
            for key in keys:
                data = data[key]
            return data
        except (KeyError, TypeError):
            return default
    
    @staticmethod
    def filter_dict(data: Dict, keys: List[str]) -> Dict:
        """Filtrer un dictionnaire par clés"""
        return {k: v for k, v in data.items() if k in keys}
    
    @staticmethod
    def exclude_dict(data: Dict, keys: List[str]) -> Dict:
        """Exclure des clés d'un dictionnaire"""
        return {k: v for k, v in data.items() if k not in keys}
    
    @staticmethod
    def serialize_for_storage(data: Any) -> str:
        """Sérialiser des données pour stockage"""
        try:
            return json.dumps(data, ensure_ascii=False, default=str)
        except (TypeError, ValueError):
            return str(data)
    
    @staticmethod
    def deserialize_from_storage(data: str) -> Any:
        """Désérialiser des données depuis le stockage"""
        try:
            return json.loads(data)
        except (json.JSONDecodeError, TypeError):
            return data

class ValidationUtils:
    """Utilitaires de validation"""
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Valider une adresse email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Valider une URL"""
        pattern = r'^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$'
        return re.match(pattern, url) is not None
    
    @staticmethod
    def is_valid_identifier(name: str) -> bool:
        """Valider un identificateur de programmation"""
        pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*$'
        return re.match(pattern, name) is not None
    
    @staticmethod
    def validate_file_path(path: str) -> bool:
        """Valider un chemin de fichier"""
        try:
            # Vérifier que le chemin est valide
            Path(path).resolve()
            return True
        except (OSError, ValueError):
            return False
    
    @staticmethod
    def validate_json(text: str) -> bool:
        """Valider du JSON"""
        try:
            json.loads(text)
            return True
        except json.JSONDecodeError:
            return False
    
    @staticmethod
    def validate_yaml(text: str) -> bool:
        """Valider du YAML"""
        try:
            yaml.safe_load(text)
            return True
        except yaml.YAMLError:
            return False

class HashUtils:
    """Utilitaires de hachage"""
    
    @staticmethod
    def md5_hash(text: str) -> str:
        """Calculer le hash MD5"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    @staticmethod
    def sha256_hash(text: str) -> str:
        """Calculer le hash SHA256"""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    @staticmethod
    def file_hash(file_path: str, algorithm: str = 'sha256') -> Optional[str]:
        """Calculer le hash d'un fichier"""
        try:
            hash_obj = hashlib.new(algorithm)
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except (OSError, ValueError):
            return None
    
    @staticmethod
    def short_hash(text: str, length: int = 8) -> str:
        """Générer un hash court"""
        full_hash = HashUtils.sha256_hash(text)
        return full_hash[:length]

class ProjectUtils:
    """Utilitaires spécifiques au projet"""
    
    @staticmethod
    def detect_project_type(project_path: str) -> str:
        """Détecter le type de projet"""
        indicators = {
            'python': ['requirements.txt', 'setup.py', 'pyproject.toml', '.py'],
            'node': ['package.json', 'node_modules', '.js', '.ts'],
            'java': ['pom.xml', 'build.gradle', '.java'],
            'dotnet': ['*.csproj', '*.sln', '.cs'],
            'go': ['go.mod', 'go.sum', '.go'],
            'rust': ['Cargo.toml', 'Cargo.lock', '.rs']
        }
        
        project_files = []
        for root, dirs, files in os.walk(project_path):
            # Limiter la profondeur
            if root.count(os.sep) - project_path.count(os.sep) > 2:
                continue
            project_files.extend(files)
            break  # Ne regarder que le niveau racine pour les fichiers indicateurs
        
        scores = {}
        for project_type, patterns in indicators.items():
            score = 0
            for pattern in patterns:
                if pattern.startswith('.'):
                    # Extension de fichier
                    score += sum(1 for f in project_files if f.endswith(pattern))
                else:
                    # Nom de fichier exact
                    score += sum(1 for f in project_files if f == pattern)
            scores[project_type] = score
        
        return max(scores.items(), key=lambda x: x[1])[0] if scores else 'unknown'
    
    @staticmethod
    def find_config_files(project_path: str) -> List[str]:
        """Trouver les fichiers de configuration"""
        config_patterns = [
            '*.json', '*.yaml', '*.yml', '*.toml', '*.ini', '*.conf',
            'config.*', '.env*', 'settings.*'
        ]
        
        config_files = []
        for root, dirs, files in os.walk(project_path):
            # Exclure certains dossiers
            dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', 'venv', '__pycache__']]
            
            for file in files:
                file_lower = file.lower()
                if any(
                    file_lower.endswith(pattern.replace('*', '')) or
                    file_lower.startswith(pattern.replace('*', ''))
                    for pattern in config_patterns
                ):
                    config_files.append(os.path.join(root, file))
        
        return config_files
    
    @staticmethod
    def get_project_stats(project_path: str) -> Dict[str, Any]:
        """Obtenir des statistiques sur le projet"""
        stats = {
            'total_files': 0,
            'total_size': 0,
            'file_types': {},
            'largest_files': [],
            'directories': 0
        }
        
        file_sizes = []
        
        for root, dirs, files in os.walk(project_path):
            stats['directories'] += len(dirs)
            
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    size = os.path.getsize(file_path)
                    stats['total_files'] += 1
                    stats['total_size'] += size
                    
                    # Type de fichier
                    ext = FileUtils.get_file_extension(file)
                    stats['file_types'][ext] = stats['file_types'].get(ext, 0) + 1
                    
                    # Garder les plus gros fichiers
                    file_sizes.append((file_path, size))
                    
                except OSError:
                    continue
        
        # Top 10 des plus gros fichiers
        file_sizes.sort(key=lambda x: x[1], reverse=True)
        stats['largest_files'] = file_sizes[:10]
        
        return stats

class TemporaryUtils:
    """Utilitaires pour les fichiers temporaires"""
    
    @staticmethod
    def create_temp_file(content: str = "", suffix: str = ".txt") -> str:
        """Créer un fichier temporaire"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=suffix) as f:
            f.write(content)
            return f.name
    
    @staticmethod
    def create_temp_dir() -> str:
        """Créer un dossier temporaire"""
        return tempfile.mkdtemp()
    
    @staticmethod
    def cleanup_temp_file(file_path: str):
        """Nettoyer un fichier temporaire"""
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except OSError:
            pass
    
    @staticmethod
    def cleanup_temp_dir(dir_path: str):
        """Nettoyer un dossier temporaire"""
        try:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
        except OSError:
            pass

# Fonctions utilitaires globales
def format_file_size(size_bytes: int) -> str:
    """Formater une taille de fichier"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

def format_duration(seconds: float) -> str:
    """Formater une durée en secondes"""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"

def ensure_directory(path: str) -> bool:
    """S'assurer qu'un dossier existe"""
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except OSError:
        return False

def get_relative_path(file_path: str, base_path: str) -> str:
    """Obtenir un chemin relatif"""
    try:
        return os.path.relpath(file_path, base_path)
    except ValueError:
        return file_path

def is_binary_file(file_path: str) -> bool:
    """Vérifier si un fichier est binaire"""
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            return b'\0' in chunk
    except OSError:
        return True

def count_lines_in_file(file_path: str) -> int:
    """Compter les lignes dans un fichier"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in f)
    except OSError:
        return 0