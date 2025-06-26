import os
import argparse
from pathlib import Path
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
from code_analyzer import UniversalCodeAnalyzer
from config import UniversalConfig
import shutil

class UniversalCodeIndexer:
    """Indexeur de code universel multi-langages"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config = UniversalConfig(config_path)
        self.analyzer = UniversalCodeAnalyzer(self.config)
        
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        
        # Extensions supportées par langage
        self.extensions = {
            'python': ['.py', '.pyw', '.pyx'],
            'javascript': ['.js', '.jsx', '.mjs'],
            'typescript': ['.ts', '.tsx'],
            'java': ['.java'],
            'csharp': ['.cs'],
            'go': ['.go'],
            'rust': ['.rs'],
            'cpp': ['.cpp', '.cxx', '.cc', '.c'],
            'php': ['.php'],
            'ruby': ['.rb'],
            'swift': ['.swift'],
            'kotlin': ['.kt', '.kts'],
            'config': ['.json', '.yaml', '.yml', '.toml', '.xml', '.ini'],
            'docs': ['.md', '.rst', '.txt']
        }
        
        # Dossiers à exclure
        self.excluded_dirs = {
            'common': ['.git', 'node_modules', '__pycache__', '.pytest_cache', 'dist', 'build'],
            'python': ['venv', 'env', '.venv', 'site-packages', '.tox'],
            'javascript': ['node_modules', 'dist', 'build', '.next', '.nuxt'],
            'java': ['target', 'build', '.gradle'],
            'csharp': ['bin', 'obj', 'packages'],
            'go': ['vendor'],
            'rust': ['target']
        }
    
    def index_project(self, project_path: str, db_path: str = "./universal_chroma_db", force: bool = False) -> bool:
        """Indexer un projet complet"""
        print(f"🔍 Indexation universelle de: {project_path}")
        
        if not os.path.exists(project_path):
            print(f"❌ Le projet {project_path} n'existe pas!")
            return False
        
        # Supprimer l'ancienne base si force
        if force and os.path.exists(db_path):
            shutil.rmtree(db_path)
            print("🗑️ Ancienne base supprimée")
        
        # Analyser le projet
        project_info = self.analyzer.analyze_project(project_path)
        main_language = project_info.get('language', 'unknown')
        
        print(f"📁 Langage détecté: {main_language}")
        print(f"🏗️ Framework: {project_info.get('framework', 'standard')}")
        
        # Charger les fichiers
        documents = self._load_files_with_metadata(project_path, project_info)
        
        if not documents:
            print("❌ Aucun fichier valide trouvé!")
            return False
        
        print(f"📄 {len(documents)} documents chargés")
        
        # Découpage intelligent
        chunks = self._smart_chunking(documents, main_language)
        print(f"📦 {len(chunks)} chunks créés")
        
        # Créer la base vectorielle
        print("🧠 Création des embeddings...")
        try:
            vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory=db_path
            )
            
            print(f"✅ Base vectorielle créée dans {db_path}")
            self._print_statistics(chunks, project_info)
            
            # Sauvegarder les métadonnées du projet
            self._save_project_metadata(db_path, project_info)
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de la création de la base: {e}")
            return False
    
    def _load_files_with_metadata(self, project_path: str, project_info: Dict) -> List[Document]:
        """Charger les fichiers avec métadonnées enrichies"""
        documents = []
        main_language = project_info.get('language', 'unknown')
        
        # Extensions à traiter selon le langage détecté
        relevant_extensions = self._get_relevant_extensions(main_language)
        excluded_dirs = self._get_excluded_dirs(main_language)
        
        print(f"🔍 Extensions: {relevant_extensions}")
        
        for root, dirs, files in os.walk(project_path):
            # Filtrer les dossiers exclus
            dirs[:] = [d for d in dirs if d not in excluded_dirs]
            
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = Path(file).suffix.lower()
                
                if file_ext in relevant_extensions or self._is_important_file(file):
                    try:
                        content = self._read_file_safe(file_path)
                        if not content.strip():
                            continue
                        
                        # Métadonnées enrichies
                        metadata = self._extract_file_metadata(file_path, content, project_path, project_info)
                        
                        document = Document(
                            page_content=content,
                            metadata=metadata
                        )
                        documents.append(document)
                        
                        if len(documents) % 50 == 0:
                            print(f"📄 {len(documents)} fichiers traités...")
                            
                    except Exception as e:
                        print(f"⚠️ Erreur avec {file_path}: {e}")
        
        return documents
    
    def _get_relevant_extensions(self, language: str) -> List[str]:
        """Obtenir les extensions pertinentes selon le langage"""
        extensions = []
        
        # Extensions principales
        if language in self.extensions:
            extensions.extend(self.extensions[language])
        
        # Extensions secondaires communes
        extensions.extend(self.extensions['config'])
        extensions.extend(self.extensions['docs'])
        
        # Extensions de test
        test_extensions = ['.test.js', '.spec.js', '.test.py', '.spec.py', 
                          '.test.ts', '.spec.ts', '.test.java']
        extensions.extend(test_extensions)
        
        return list(set(extensions))
    
    def _get_excluded_dirs(self, language: str) -> List[str]:
        """Obtenir les dossiers à exclure selon le langage"""
        excluded = self.excluded_dirs['common'].copy()
        
        if language in self.excluded_dirs:
            excluded.extend(self.excluded_dirs[language])
        
        return excluded
    
    def _is_important_file(self, filename: str) -> bool:
        """Vérifier si un fichier est important même sans extension"""
        important_files = [
            'Dockerfile', 'Makefile', 'README', 'LICENSE', 'CHANGELOG',
            'requirements.txt', 'package.json', 'pom.xml', 'Cargo.toml',
            'go.mod', 'composer.json', '.gitignore', '.env'
        ]
        
        return any(filename.startswith(important) for important in important_files)
    
    def _read_file_safe(self, file_path: str) -> str:
        """Lire un fichier de manière sécurisée"""
        encodings = ['utf-8', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        
        return ""
    
    def _extract_file_metadata(self, file_path: str, content: str, project_path: str, project_info: Dict) -> Dict:
        """Extraire les métadonnées d'un fichier"""
        relative_path = os.path.relpath(file_path, project_path)
        filename = os.path.basename(file_path)
        file_ext = Path(file_path).suffix.lower()
        
        # Métadonnées de base
        metadata = {
            'source': file_path,
            'relative_path': relative_path,
            'filename': filename,
            'extension': file_ext,
            'language': self._detect_file_language(file_ext, content),
            'project_language': project_info.get('language', 'unknown'),
            'framework': project_info.get('framework', 'standard')
        }
        
        # Classification du fichier
        metadata.update(self._classify_file(relative_path, content, project_info))
        
        # Métriques du fichier
        metadata.update(self._calculate_file_metrics(content))
        
        # Éléments extraits
        metadata.update(self._extract_code_elements(content, metadata['language']))
        
        return self._serialize_metadata(metadata)
    
    def _detect_file_language(self, extension: str, content: str) -> str:
        """Détecter le langage d'un fichier"""
        lang_map = {
            '.py': 'python', '.js': 'javascript', '.ts': 'typescript',
            '.java': 'java', '.cs': 'csharp', '.go': 'go', '.rs': 'rust',
            '.cpp': 'cpp', '.c': 'c', '.php': 'php', '.rb': 'ruby',
            '.swift': 'swift', '.kt': 'kotlin'
        }
        
        return lang_map.get(extension, 'other')
    
    def _classify_file(self, relative_path: str, content: str, project_info: Dict) -> Dict:
        """Classifier un fichier selon son rôle"""
        path_lower = relative_path.lower()
        content_lower = content.lower()
        
        classification = {
            'file_type': 'unknown',
            'layer': 'unknown',
            'is_test': False,
            'is_config': False,
            'is_documentation': False
        }
        
        # Type de fichier
        if any(indicator in path_lower for indicator in ['test', 'spec', '__test__']):
            classification['file_type'] = 'test'
            classification['is_test'] = True
        elif any(indicator in path_lower for indicator in ['controller', 'handler']):
            classification['file_type'] = 'controller'
        elif any(indicator in path_lower for indicator in ['service', 'business']):
            classification['file_type'] = 'service'
        elif any(indicator in path_lower for indicator in ['model', 'entity']):
            classification['file_type'] = 'model'
        elif any(indicator in path_lower for indicator in ['repository', 'dao']):
            classification['file_type'] = 'repository'
        elif any(indicator in path_lower for indicator in ['util', 'helper']):
            classification['file_type'] = 'utility'
        elif any(indicator in path_lower for indicator in ['config', 'setting']):
            classification['file_type'] = 'config'
            classification['is_config'] = True
        elif relative_path.endswith(('.md', '.rst', '.txt')):
            classification['file_type'] = 'documentation'
            classification['is_documentation'] = True
        
        # Couche architecturale
        if any(layer in path_lower for layer in ['domain', 'core', 'business']):
            classification['layer'] = 'domain'
        elif any(layer in path_lower for layer in ['infrastructure', 'data', 'external']):
            classification['layer'] = 'infrastructure'
        elif any(layer in path_lower for layer in ['application', 'app', 'use_case']):
            classification['layer'] = 'application'
        elif any(layer in path_lower for layer in ['presentation', 'ui', 'web', 'api']):
            classification['layer'] = 'presentation'
        
        return classification
    
    def _calculate_file_metrics(self, content: str) -> Dict:
        """Calculer les métriques d'un fichier"""
        lines = content.split('\n')
        
        metrics = {
            'lines_total': len(lines),
            'lines_code': 0,
            'lines_comment': 0,
            'lines_blank': 0,
            'complexity_estimate': 1
        }
        
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                metrics['lines_blank'] += 1
            elif line_stripped.startswith(('#', '//', '/*', '*', '<!--', '--')):
                metrics['lines_comment'] += 1
            else:
                metrics['lines_code'] += 1
                
                # Estimation simple de complexité
                complexity_indicators = ['if ', 'for ', 'while ', 'case ', 'catch ', 'elif ']
                if any(indicator in line_stripped for indicator in complexity_indicators):
                    metrics['complexity_estimate'] += 1
        
        return metrics
    
    def _extract_code_elements(self, content: str, language: str) -> Dict:
        """Extraire les éléments de code (fonctions, classes, etc.)"""
        elements = {
            'functions': [],
            'classes': [],
            'imports': [],
            'exports': []
        }
        
        try:
            if language == 'python':
                elements.update(self._extract_python_elements(content))
            elif language in ['javascript', 'typescript']:
                elements.update(self._extract_js_elements(content))
            elif language == 'java':
                elements.update(self._extract_java_elements(content))
            # Ajouter d'autres langages selon les besoins
            
        except Exception as e:
            pass  # Ignorer les erreurs de parsing
        
        # Limiter le nombre d'éléments pour éviter des métadonnées trop lourdes
        for key in elements:
            if isinstance(elements[key], list) and len(elements[key]) > 10:
                elements[key] = elements[key][:10]
        
        return {
            f'has_{key}': len(elements[key]) > 0,
            f'{key}_count': len(elements[key]),
            f'{key}_first': elements[key][0] if elements[key] else None
        }
    
    def _extract_python_elements(self, content: str) -> Dict:
        """Extraire les éléments Python"""
        elements = {'functions': [], 'classes': [], 'imports': []}
        
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    elements['functions'].append(node.name)
                elif isinstance(node, ast.ClassDef):
                    elements['classes'].append(node.name)
                elif isinstance(node, ast.Import):
                    elements['imports'].extend([alias.name for alias in node.names])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        elements['imports'].append(node.module)
        except:
            pass
        
        return elements
    
    def _extract_js_elements(self, content: str) -> Dict:
        """Extraire les éléments JavaScript/TypeScript"""
        elements = {'functions': [], 'classes': [], 'imports': [], 'exports': []}
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            
            # Fonctions
            if 'function ' in line:
                match = re.search(r'function\s+(\w+)', line)
                if match:
                    elements['functions'].append(match.group(1))
            
            # Classes
            if line.startswith('class '):
                match = re.search(r'class\s+(\w+)', line)
                if match:
                    elements['classes'].append(match.group(1))
            
            # Imports
            if line.startswith('import '):
                match = re.search(r'from\s+[\'"]([^\'"]+)[\'"]', line)
                if match:
                    elements['imports'].append(match.group(1))
            
            # Exports
            if line.startswith('export '):
                match = re.search(r'export\s+(?:default\s+)?(?:class\s+|function\s+)?(\w+)', line)
                if match:
                    elements['exports'].append(match.group(1))
        
        return elements
    
    def _extract_java_elements(self, content: str) -> Dict:
        """Extraire les éléments Java"""
        elements = {'functions': [], 'classes': [], 'imports': []}
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            
            # Classes
            if line.startswith('public class ') or line.startswith('class '):
                match = re.search(r'class\s+(\w+)', line)
                if match:
                    elements['classes'].append(match.group(1))
            
            # Méthodes
            if 'public ' in line and '(' in line and ')' in line:
                match = re.search(r'(\w+)\s*\(', line)
                if match and match.group(1) not in ['class', 'if', 'for', 'while']:
                    elements['functions'].append(match.group(1))
            
            # Imports
            if line.startswith('import '):
                match = re.search(r'import\s+([^;]+);', line)
                if match:
                    elements['imports'].append(match.group(1))
        
        return elements
    
    def _serialize_metadata(self, metadata: Dict) -> Dict:
        """Sérialiser les métadonnées pour ChromaDB"""
        serialized = {}
        
        for key, value in metadata.items():
            if isinstance(value, (str, int, float, bool)) or value is None:
                serialized[key] = value
            else:
                serialized[key] = str(value)
        
        return serialized
    
    def _smart_chunking(self, documents: List[Document], language: str) -> List[Document]:
        """Découpage intelligent selon le langage"""
        chunks = []
        
        for doc in documents:
            file_type = doc.metadata.get('file_type', 'unknown')
            content_length = len(doc.page_content)
            
            # Stratégie de découpage selon le type de fichier
            if file_type == 'documentation':
                chunk_size = 1500
                overlap = 300
            elif file_type == 'config':
                chunk_size = 800
                overlap = 100
            elif content_length < 500:
                # Petits fichiers : pas de découpage
                chunks.append(doc)
                continue
            else:
                chunk_size = 1200
                overlap = 200
            
            # Découpage
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=overlap,
                separators=self._get_separators(language)
            )
            
            file_chunks = splitter.split_documents([doc])
            
            # Ajouter des métadonnées de chunk
            for i, chunk in enumerate(file_chunks):
                chunk.metadata.update({
                    'chunk_index': i,
                    'chunk_total': len(file_chunks),
                    'chunk_size': len(chunk.page_content)
                })
            
            chunks.extend(file_chunks)
        
        return chunks
    
    def _get_separators(self, language: str) -> List[str]:
        """Obtenir les séparateurs pour le découpage selon le langage"""
        separators = {
            'python': ['\nclass ', '\ndef ', '\n\n', '\n', ' '],
            'javascript': ['\nclass ', '\nfunction ', '\nconst ', '\n\n', '\n', ' '],
            'java': ['\npublic class ', '\npublic ', '\nprivate ', '\n\n', '\n', ' '],
            'csharp': ['\npublic class ', '\npublic ', '\nprivate ', '\n\n', '\n', ' '],
            'go': ['\nfunc ', '\ntype ', '\n\n', '\n', ' '],
            'rust': ['\nfn ', '\nstruct ', '\nimpl ', '\n\n', '\n', ' ']
        }
        
        return separators.get(language, ['\n\n', '\n', ' '])
    
    def _save_project_metadata(self, db_path: str, project_info: Dict):
        """Sauvegarder les métadonnées du projet"""
        metadata_file = os.path.join(db_path, 'project_metadata.json')
        
        try:
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(project_info, f, indent=2, ensure_ascii=False, default=str)
            print(f"📊 Métadonnées sauvegardées dans {metadata_file}")
        except Exception as e:
            print(f"⚠️ Erreur sauvegarde métadonnées: {e}")
    
    def _print_statistics(self, chunks: List[Document], project_info: Dict):
        """Afficher les statistiques d'indexation"""
        stats = {
            'total_chunks': len(chunks),
            'languages': {},
            'file_types': {},
            'layers': {},
            'test_files': 0
        }
        
        for chunk in chunks:
            metadata = chunk.metadata
            
            # Stats par langage
            lang = metadata.get('language', 'unknown')
            stats['languages'][lang] = stats['languages'].get(lang, 0) + 1
            
            # Stats par type
            file_type = metadata.get('file_type', 'unknown')
            stats['file_types'][file_type] = stats['file_types'].get(file_type, 0) + 1
            
            # Stats par couche
            layer = metadata.get('layer', 'unknown')
            stats['layers'][layer] = stats['layers'].get(layer, 0) + 1
            
            # Tests
            if metadata.get('is_test', False):
                stats['test_files'] += 1
        
        print("\n📊 STATISTIQUES D'INDEXATION:")
        print(f"📁 Projet: {project_info.get('language', 'Unknown')} ({project_info.get('framework', 'Standard')})")
        print(f"📦 Total chunks: {stats['total_chunks']}")
        print(f"🧪 Fichiers de test: {stats['test_files']}")
        print(f"🗣️ Langages: {dict(stats['languages'])}")
        print(f"📄 Types: {dict(stats['file_types'])}")
        print(f"🏗️ Couches: {dict(stats['layers'])}")

def main():
    """Interface en ligne de commande"""
    parser = argparse.ArgumentParser(description='Indexeur de code universel')
    parser.add_argument('project', help='Chemin vers le projet à indexer')
    parser.add_argument('--output', '-o', default='./universal_chroma_db', 
                       help='Chemin de sortie pour la base vectorielle')
    parser.add_argument('--config', '-c', default='config.yaml',
                       help='Fichier de configuration')
    parser.add_argument('--force', '-f', action='store_true',
                       help='Forcer la recréation de la base')
    
    args = parser.parse_args()
    
    try:
        indexer = UniversalCodeIndexer(args.config)
        success = indexer.index_project(args.project, args.output, args.force)
        
        if success:
            print(f"\n✅ Indexation réussie!")
            print(f"🚀 Vous pouvez maintenant utiliser:")
            print(f"   python universal_agent.py --project {args.project}")
            print(f"   streamlit run app.py")
        else:
            print(f"\n❌ Indexation échouée!")
            exit(1)
    
    except Exception as e:
        print(f"❌ Erreur: {e}")
        exit(1)

if __name__ == "__main__":
    main()