import os
import re
import ast
import json
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document

class EnhancedCodeIndexer:
    def __init__(self, project_path="/home/dythic/projet/hexagonal-nodejs-example"):
        self.project_path = project_path
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        
    def extract_js_functions(self, content):
        """Extraire les fonctions JavaScript/TypeScript"""
        functions = []
        
        # Patterns pour différents types de fonctions
        patterns = [
            r'function\s+(\w+)\s*\([^)]*\)\s*\{',  # function name() {}
            r'const\s+(\w+)\s*=\s*\([^)]*\)\s*=>\s*\{',  # const name = () => {}
            r'(\w+)\s*:\s*function\s*\([^)]*\)\s*\{',  # name: function() {}
            r'(\w+)\s*\([^)]*\)\s*\{',  # name() {} (méthodes de classe)
            r'async\s+(\w+)\s*\([^)]*\)\s*\{',  # async name() {}
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                functions.append(match.group(1))
        
        return list(set(functions))  # Supprimer les doublons
    
    def extract_dependencies(self, content):
        """Extraire les dépendances avec plus de détails"""
        all_deps = []
        internal_deps = []
        external_deps = []
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            
            # ES6 imports
            if line.startswith('import '):
                dep_match = re.search(r"from\s+['\"]([^'\"]+)['\"]", line)
                if dep_match:
                    dep = dep_match.group(1)
                    all_deps.append(dep)
                    if dep.startswith('.'):
                        internal_deps.append(dep)
                    else:
                        external_deps.append(dep)
            
            # CommonJS requires
            elif 'require(' in line:
                req_match = re.search(r"require\(['\"]([^'\"]+)['\"]\)", line)
                if req_match:
                    dep = req_match.group(1)
                    all_deps.append(dep)
                    if dep.startswith('.'):
                        internal_deps.append(dep)
                    else:
                        external_deps.append(dep)
        
        return {
            'all_deps_count': len(all_deps),
            'internal_deps_count': len(internal_deps),
            'external_deps_count': len(external_deps),
            'has_internal_deps': len(internal_deps) > 0,
            'has_external_deps': len(external_deps) > 0
        }
    
    def extract_exports(self, content):
        """Extraire les exports"""
        exports = []
        
        # Patterns pour les exports
        patterns = [
            r'module\.exports\s*=\s*(\w+)',  # module.exports = Something
            r'exports\.(\w+)',  # exports.something
            r'export\s+(?:default\s+)?(?:class\s+)?(\w+)',  # export class/function Name
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                exports.append(match.group(1))
        
        # Export destructuré
        export_block_match = re.search(r'export\s*\{\s*([^}]+)\s*\}', content)
        if export_block_match:
            exports_list = export_block_match.group(1).split(',')
            exports.extend([exp.strip() for exp in exports_list])
        
        return list(set(exports))  # Supprimer les doublons
    
    def calculate_complexity(self, content):
        """Calculer la complexité du code"""
        complexity_indicators = {
            'lines': len(content.split('\n')),
            'functions_count': len(self.extract_js_functions(content)),
            'conditionals': content.count('if ') + content.count('else ') + content.count('switch '),
            'loops': content.count('for ') + content.count('while ') + content.count('forEach'),
            'try_catch': content.count('try ') + content.count('catch '),
            'async_await': content.count('async ') + content.count('await '),
        }
        
        # Score de complexité simple
        complexity_score = (
            complexity_indicators['conditionals'] * 2 +
            complexity_indicators['loops'] * 2 +
            complexity_indicators['functions_count'] * 1 +
            complexity_indicators['try_catch'] * 3
        )
        
        level = 'low' if complexity_score < 10 else 'medium' if complexity_score < 25 else 'high'
        
        return {
            'score': complexity_score,
            'level': level,
            'lines': complexity_indicators['lines'],
            'functions_count': complexity_indicators['functions_count'],
            'conditionals': complexity_indicators['conditionals'],
            'loops': complexity_indicators['loops'],
            'try_catch': complexity_indicators['try_catch'],
            'async_await': complexity_indicators['async_await']
        }
    
    def detect_layer(self, file_path):
        """Détecter la couche architecturale avec plus de précision"""
        path_lower = file_path.lower()
        
        if 'domain' in path_lower:
            if 'entities' in path_lower:
                return 'domain-entity'
            elif 'services' in path_lower:
                return 'domain-service'
            elif 'ports' in path_lower:
                return 'domain-port'
            else:
                return 'domain'
        elif 'infrastructure' in path_lower:
            if 'web' in path_lower or 'controller' in path_lower:
                return 'infrastructure-web'
            elif 'database' in path_lower or 'repository' in path_lower:
                return 'infrastructure-database'
            elif 'auth' in path_lower:
                return 'infrastructure-auth'
            elif 'email' in path_lower:
                return 'infrastructure-email'
            else:
                return 'infrastructure'
        elif 'application' in path_lower:
            return 'application'
        elif 'test' in path_lower:
            return 'test'
        else:
            return 'other'
    
    def detect_file_type(self, file_path, content):
        """Détecter le type de fichier avec analyse du contenu"""
        filename = os.path.basename(file_path).lower()
        
        # Analyse basée sur le nom
        if 'controller' in filename:
            return 'controller'
        elif 'service' in filename:
            return 'service'
        elif 'repository' in filename:
            return 'repository'
        elif 'middleware' in filename:
            return 'middleware'
        elif 'entity' in filename or 'entities' in file_path:
            return 'entity'
        elif 'test' in filename:
            return 'test'
        
        # Analyse basée sur le contenu
        if 'class ' in content and 'constructor' in content:
            return 'class'
        elif 'describe(' in content and 'test(' in content:
            return 'test'
        elif 'module.exports' in content or 'export ' in content:
            return 'module'
        else:
            return 'utility'
    
    def serialize_metadata_for_chroma(self, metadata):
        """Convertir les métadonnées pour ChromaDB (seulement types simples)"""
        serialized = {}
        
        for key, value in metadata.items():
            if isinstance(value, (str, int, float, bool)) or value is None:
                serialized[key] = value
            elif isinstance(value, list):
                # Convertir les listes en chaînes
                serialized[f"{key}_count"] = len(value)
                serialized[f"{key}_first"] = value[0] if value else None
                serialized[f"has_{key}"] = len(value) > 0
            elif isinstance(value, dict):
                # Aplatir les dictionnaires
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, (str, int, float, bool)) or sub_value is None:
                        serialized[f"{key}_{sub_key}"] = sub_value
            else:
                # Convertir en string pour tout le reste
                serialized[key] = str(value)
        
        return serialized
    
    def smart_chunk_by_functions(self, content, metadata):
        """Découpage intelligent par fonctions"""
        chunks = []
        functions = self.extract_js_functions(content)
        
        if not functions or len(content.split('\n')) < 50:
            # Fallback: découpage classique pour les petits fichiers
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            docs = splitter.create_documents([content], [metadata])
            return docs
        
        # Tentative de découpage par fonction
        lines = content.split('\n')
        current_chunk = []
        current_function = None
        brace_count = 0
        in_function = False
        
        for i, line in enumerate(lines):
            current_chunk.append(line)
            
            # Détecter le début d'une fonction
            for func in functions:
                if func in line and ('function' in line or '=>' in line or 
                                   (line.strip().endswith('{') and '(' in line)):
                    if current_function and len(current_chunk) > 20:
                        # Sauvegarder le chunk précédent
                        chunk_content = '\n'.join(current_chunk[:-1])
                        if chunk_content.strip():
                            chunk_metadata = metadata.copy()
                            chunk_metadata['function_name'] = current_function
                            chunk_metadata['chunk_type'] = 'function'
                            chunks.append(Document(
                                page_content=chunk_content, 
                                metadata=self.serialize_metadata_for_chroma(chunk_metadata)
                            ))
                        current_chunk = [line]
                    current_function = func
                    in_function = True
                    brace_count = 0
                    break
            
            # Compter les accolades pour détecter la fin de fonction
            if in_function:
                brace_count += line.count('{') - line.count('}')
                
                # Si on ferme toutes les accolades et qu'on a une fonction
                if brace_count <= 0 and current_function and len(current_chunk) > 5:
                    chunk_content = '\n'.join(current_chunk)
                    if chunk_content.strip():
                        chunk_metadata = metadata.copy()
                        chunk_metadata['function_name'] = current_function
                        chunk_metadata['chunk_type'] = 'function'
                        chunks.append(Document(
                            page_content=chunk_content,
                            metadata=self.serialize_metadata_for_chroma(chunk_metadata)
                        ))
                    current_chunk = []
                    current_function = None
                    in_function = False
        
        # Ajouter le dernier chunk s'il reste du contenu
        if current_chunk and any(line.strip() for line in current_chunk):
            chunk_content = '\n'.join(current_chunk)
            chunk_metadata = metadata.copy()
            chunk_metadata['function_name'] = current_function or 'remainder'
            chunk_metadata['chunk_type'] = 'remainder'
            chunks.append(Document(
                page_content=chunk_content,
                metadata=self.serialize_metadata_for_chroma(chunk_metadata)
            ))
        
        # Si aucun chunk n'a été créé, utiliser le découpage classique
        if not chunks:
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            return splitter.create_documents([content], [metadata])
        
        return chunks
    
    def load_files_with_enhanced_metadata(self):
        """Chargement avec métadonnées enrichies"""
        documents = []
        extensions = ['.js', '.ts', '.jsx', '.tsx', '.json', '.md', '.yml', '.yaml']
        excluded_dirs = ['node_modules', '.git', 'dist', 'build', 'coverage', '.next']
        
        print(f"🔍 Indexation avancée de : {self.project_path}")
        
        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if d not in excluded_dirs]
            
            for file in files:
                if any(file.endswith(ext) for ext in extensions) or 'test' in file.lower():
                    file_path = os.path.join(root, file)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        if not content.strip():
                            continue
                        
                        # Extraire les informations
                        functions = self.extract_js_functions(content)
                        dependencies = self.extract_dependencies(content)
                        exports = self.extract_exports(content)
                        complexity = self.calculate_complexity(content)
                        layer = self.detect_layer(file_path)
                        file_type = self.detect_file_type(file_path, content)
                        
                        # Métadonnées compatibles ChromaDB
                        metadata = {
                            'source': file_path,
                            'filename': file,
                            'layer': layer,
                            'file_type': file_type,
                            'functions_count': len(functions),
                            'functions_first': functions[0] if functions else None,
                            'has_functions': len(functions) > 0,
                            'exports_count': len(exports),
                            'exports_first': exports[0] if exports else None,
                            'has_exports': len(exports) > 0,
                            'lines_count': complexity['lines'],
                            'complexity_score': complexity['score'],
                            'complexity_level': complexity['level'],
                            'is_test': 'test' in file.lower() or '__tests__' in root,
                            'relative_path': os.path.relpath(file_path, self.project_path)
                        }
                        
                        # Ajouter les métriques de dépendances
                        metadata.update(dependencies)
                        
                        # Ajouter les métriques de complexité
                        for key, value in complexity.items():
                            if key != 'level':  # level déjà ajouté
                                metadata[f"complexity_{key}"] = value
                        
                        # Découpage intelligent
                        chunks = self.smart_chunk_by_functions(content, metadata)
                        documents.extend(chunks)
                        
                        print(f"✅ {file_path} ({len(chunks)} chunks)")
                        
                    except Exception as e:
                        print(f"⚠️  Erreur avec {file_path}: {e}")
        
        return documents
    
    def create_enhanced_vectorstore(self, db_path="./enhanced_chroma_db"):
        """Créer la base vectorielle optimisée"""
        # Supprimer l'ancienne base si elle existe
        if os.path.exists(db_path):
            import shutil
            shutil.rmtree(db_path)
            print(f"🗑️  Ancienne base supprimée")
        
        documents = self.load_files_with_enhanced_metadata()
        
        print(f"📦 Total documents: {len(documents)}")
        
        if len(documents) == 0:
            print("❌ Aucun document trouvé !")
            return None
        
        # Créer la base vectorielle
        print("🧠 Création des embeddings optimisés...")
        vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=db_path
        )
        
        print(f"🎉 Base vectorielle optimisée créée dans {db_path}")
        
        # Statistiques
        self.print_statistics(documents)
        
        return vectorstore
    
    def print_statistics(self, documents):
        """Afficher les statistiques"""
        stats = {
            'total_docs': len(documents),
            'layers': {},
            'file_types': {},
            'complexity_levels': {},
            'test_files': 0
        }
        
        for doc in documents:
            metadata = doc.metadata
            
            # Stats par couche
            layer = metadata.get('layer', 'unknown')
            stats['layers'][layer] = stats['layers'].get(layer, 0) + 1
            
            # Stats par type
            file_type = metadata.get('file_type', 'unknown')
            stats['file_types'][file_type] = stats['file_types'].get(file_type, 0) + 1
            
            # Stats complexité
            complexity = metadata.get('complexity_level', 'unknown')
            stats['complexity_levels'][complexity] = stats['complexity_levels'].get(complexity, 0) + 1
            
            # Tests
            if metadata.get('is_test', False):
                stats['test_files'] += 1
        
        print("\n📊 Statistiques de l'indexation:")
        print(f"📁 Total documents: {stats['total_docs']}")
        print(f"🧪 Fichiers de test: {stats['test_files']}")
        print(f"🏗️  Couches: {dict(stats['layers'])}")
        print(f"📄 Types: {dict(stats['file_types'])}")
        print(f"🔧 Complexité: {dict(stats['complexity_levels'])}")

if __name__ == "__main__":
    indexer = EnhancedCodeIndexer()
    vectorstore = indexer.create_enhanced_vectorstore()
    
    if vectorstore:
        # Test de recherche
        print("\n🧪 Test de recherche avancée:")
        docs = vectorstore.similarity_search("UserService authentication", k=3)
        for i, doc in enumerate(docs):
            print(f"{i+1}. {doc.metadata.get('filename', 'Unknown')} - {doc.metadata.get('layer', 'Unknown')}")