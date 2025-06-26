import os
import json
import re
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict, Counter
from datetime import datetime
import pickle

class HexagonalExpertSystem:
    def __init__(self, project_path="/home/dythic/projet/hexagonal-nodejs-example"):
        self.project_path = project_path
        self.knowledge_graph = nx.DiGraph()
        self.code_patterns = {}
        self.best_practices = {}
        self.violations = []
        self.metrics = {}
        
    def analyze_codebase(self):
        """Analyse complète de la codebase"""
        print("🔍 Analyse complète de la codebase...")
        
        self.map_dependencies()
        self.detect_patterns()
        self.check_best_practices()
        self.calculate_metrics()
        self.detect_code_smells()
        
        print("✅ Analyse terminée")
        
    def map_dependencies(self):
        """Mapper les dépendances entre fichiers"""
        print("🗺️  Mapping des dépendances...")
        
        for root, dirs, files in os.walk(self.project_path):
            if any(excluded in root for excluded in ['node_modules', '.git']):
                continue
                
            for file in files:
                if file.endswith('.js'):
                    file_path = os.path.join(root, file)
                    self.analyze_file_dependencies(file_path)
    
    def analyze_file_dependencies(self, file_path):
        """Analyser les dépendances d'un fichier"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Ajouter le nœud
            rel_path = os.path.relpath(file_path, self.project_path)
            self.knowledge_graph.add_node(rel_path, type=self.classify_file(file_path))
            
            # Analyser les imports
            imports = self.extract_imports(content)
            for imp in imports:
                if imp.startswith('.'):  # Dépendance interne
                    # Résoudre le chemin relatif
                    dep_path = self.resolve_import_path(file_path, imp)
                    if dep_path:
                        dep_rel_path = os.path.relpath(dep_path, self.project_path)
                        self.knowledge_graph.add_edge(rel_path, dep_rel_path, type='import')
                        
        except Exception as e:
            print(f"Erreur analyse {file_path}: {e}")
    
    def classify_file(self, file_path):
        """Classifier un fichier selon l'architecture hexagonale"""
        if 'domain' in file_path:
            if 'entities' in file_path:
                return 'domain-entity'
            elif 'services' in file_path:
                return 'domain-service'
            elif 'ports' in file_path:
                return 'domain-port'
        elif 'infrastructure' in file_path:
            if 'web' in file_path:
                return 'infrastructure-web'
            elif 'database' in file_path:
                return 'infrastructure-database'
            elif 'auth' in file_path:
                return 'infrastructure-auth'
        elif 'test' in file_path:
            return 'test'
        
        return 'other'
    
    def extract_imports(self, content):
        """Extraire les imports d'un fichier"""
        imports = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            # ES6 imports
            if line.startswith('import '):
                match = re.search(r"from\s+['\"]([^'\"]+)['\"]", line)
                if match:
                    imports.append(match.group(1))
            # CommonJS requires
            elif 'require(' in line:
                match = re.search(r"require\(['\"]([^'\"]+)['\"]\)", line)
                if match:
                    imports.append(match.group(1))
        
        return imports
    
    def resolve_import_path(self, from_file, import_path):
        """Résoudre un chemin d'import relatif"""
        if not import_path.startswith('.'):
            return None
            
        from_dir = os.path.dirname(from_file)
        resolved = os.path.normpath(os.path.join(from_dir, import_path))
        
        # Essayer différentes extensions
        for ext in ['.js', '.ts', '/index.js', '/index.ts']:
            candidate = resolved + ext
            if os.path.exists(candidate):
                return candidate
        
        return None
    
    def detect_patterns(self):
        """Détecter les patterns architecturaux"""
        print("🔍 Détection des patterns...")
        
        patterns = {
            'repository_pattern': self.detect_repository_pattern(),
            'service_pattern': self.detect_service_pattern(),
            'dependency_injection': self.detect_dependency_injection(),
            'adapter_pattern': self.detect_adapter_pattern(),
            'factory_pattern': self.detect_factory_pattern()
        }
        
        self.code_patterns = patterns
    
    def detect_repository_pattern(self):
        """Détecter le pattern Repository"""
        repositories = []
        
        for node in self.knowledge_graph.nodes():
            if 'repository' in node.lower():
                file_path = os.path.join(self.project_path, node)
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    # Vérifier les caractéristiques du pattern Repository
                    has_crud = any(method in content.lower() for method in ['save', 'find', 'delete', 'update'])
                    has_interface = 'class ' in content or 'function ' in content
                    
                    if has_crud and has_interface:
                        repositories.append({
                            'file': node,
                            'methods': self.extract_methods(content),
                            'score': 'good' if has_crud and has_interface else 'partial'
                        })
                except:
                    continue
        
        return repositories
    
    def detect_service_pattern(self):
        """Détecter le pattern Service"""
        services = []
        
        for node in self.knowledge_graph.nodes():
            if 'service' in node.lower() and 'domain' in node:
                file_path = os.path.join(self.project_path, node)
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    methods = self.extract_methods(content)
                    business_logic = any(keyword in content.lower() for keyword in 
                                       ['validate', 'process', 'calculate', 'business', 'rule'])
                    
                    services.append({
                        'file': node,
                        'methods': methods,
                        'has_business_logic': business_logic,
                        'dependencies': list(self.knowledge_graph.successors(node))
                    })
                except:
                    continue
        
        return services
    
    def detect_dependency_injection(self):
        """Détecter l'injection de dépendances"""
        di_files = []
        
        for node in self.knowledge_graph.nodes():
            file_path = os.path.join(self.project_path, node)
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Patterns d'injection de dépendances
                constructor_injection = 'constructor(' in content and 'this.' in content
                method_injection = any(pattern in content for pattern in [
                    'inject(', 'dependency', 'Container', 'DI'
                ])
                
                if constructor_injection or method_injection:
                    di_files.append({
                        'file': node,
                        'type': 'constructor' if constructor_injection else 'method',
                        'score': 'good' if constructor_injection else 'partial'
                    })
            except:
                continue
        
        return di_files
    
    def detect_adapter_pattern(self):
        """Détecter le pattern Adapter"""
        adapters = []
        
        infrastructure_nodes = [n for n in self.knowledge_graph.nodes() 
                              if 'infrastructure' in n]
        
        for node in infrastructure_nodes:
            file_path = os.path.join(self.project_path, node)
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Caractéristiques d'un adapter
                implements_interface = any(keyword in content for keyword in [
                    'implements', 'extends', 'class', 'prototype'
                ])
                external_dependency = any(lib in content for lib in [
                    'mongodb', 'mongoose', 'express', 'nodemailer', 'bcrypt', 'jwt'
                ])
                
                if implements_interface and external_dependency:
                    adapters.append({
                        'file': node,
                        'external_deps': self.extract_external_dependencies(content),
                        'interface_methods': self.extract_methods(content)
                    })
            except:
                continue
        
        return adapters
    
    def detect_factory_pattern(self):
        """Détecter le pattern Factory"""
        factories = []
        
        for node in self.knowledge_graph.nodes():
            file_path = os.path.join(self.project_path, node)
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Patterns de factory
                has_create_method = any(method in content.lower() for method in [
                    'create', 'build', 'make', 'factory'
                ])
                returns_instances = 'new ' in content or 'return ' in content
                
                if has_create_method and returns_instances:
                    factories.append({
                        'file': node,
                        'factory_methods': [m for m in self.extract_methods(content) 
                                          if any(keyword in m.lower() for keyword in 
                                               ['create', 'build', 'make'])]
                    })
            except:
                continue
        
        return factories
    
    def extract_methods(self, content):
        """Extraire les méthodes d'un fichier"""
        methods = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            # Méthodes de classe
            if (line.endswith('{') and '(' in line and ')' in line 
                and not line.startswith('if') and not line.startswith('for')):
                method_name = line.split('(')[0].strip()
                if method_name and not method_name.startswith('//'):
                    methods.append(method_name)
        
        return methods[:10]  # Limiter pour éviter le spam
    
    def extract_external_dependencies(self, content):
        """Extraire les dépendances externes"""
        external_deps = []
        
        for line in content.split('\n'):
            if 'require(' in line or 'import ' in line:
                for lib in ['mongodb', 'mongoose', 'express', 'nodemailer', 'bcrypt', 'jsonwebtoken']:
                    if lib in line:
                        external_deps.append(lib)
        
        return list(set(external_deps))
    
    def check_best_practices(self):
        """Vérifier les bonnes pratiques"""
        print("✅ Vérification des bonnes pratiques...")
        
        practices = {
            'single_responsibility': self.check_single_responsibility(),
            'dependency_direction': self.check_dependency_direction(),
            'layer_isolation': self.check_layer_isolation(),
            'test_coverage': self.check_test_coverage(),
            'naming_conventions': self.check_naming_conventions()
        }
        
        self.best_practices = practices
    
    def check_single_responsibility(self):
        """Vérifier le principe de responsabilité unique"""
        violations = []
        
        for node in self.knowledge_graph.nodes():
            if 'service' in node.lower():
                file_path = os.path.join(self.project_path, node)
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    methods = self.extract_methods(content)
                    
                    # Heuristique: trop de méthodes = violation SRP
                    if len(methods) > 7:
                        violations.append({
                            'file': node,
                            'issue': f'Trop de méthodes ({len(methods)})',
                            'severity': 'medium'
                        })
                except:
                    continue
        
        return violations
    
    def check_dependency_direction(self):
        """Vérifier la direction des dépendances (hexagonale)"""
        violations = []
        
        # Les dépendances doivent aller vers l'intérieur
        for edge in self.knowledge_graph.edges():
            source, target = edge
            source_layer = self.get_layer_level(source)
            target_layer = self.get_layer_level(target)
            
            # Violation si infrastructure dépend du domain (inverse attendu)
            if source_layer > target_layer:
                violations.append({
                    'source': source,
                    'target': target,
                    'issue': 'Dépendance dans le mauvais sens',
                    'severity': 'high'
                })
        
        return violations
    
    def get_layer_level(self, file_path):
        """Obtenir le niveau de couche (plus bas = plus central)"""
        if 'domain' in file_path:
            return 1  # Centre
        elif 'application' in file_path:
            return 2  # Milieu
        elif 'infrastructure' in file_path:
            return 3  # Extérieur
        else:
            return 2  # Par défaut
    
    def check_layer_isolation(self):
        """Vérifier l'isolation entre couches"""
        violations = []
        
        # Domain ne devrait pas importer d'infrastructure
        domain_nodes = [n for n in self.knowledge_graph.nodes() if 'domain' in n]
        
        for domain_node in domain_nodes:
            dependencies = list(self.knowledge_graph.successors(domain_node))
            for dep in dependencies:
                if 'infrastructure' in dep:
                    violations.append({
                        'file': domain_node,
                        'dependency': dep,
                        'issue': 'Domain dépend d\'Infrastructure',
                        'severity': 'critical'
                    })
        
        return violations
    
    def check_test_coverage(self):
        """Vérifier la couverture de tests"""
        coverage_info = {}
        
        # Lister tous les fichiers de production
        prod_files = [n for n in self.knowledge_graph.nodes() 
                     if not 'test' in n.lower() and n.endswith('.js')]
        
        # Lister tous les fichiers de test
        test_files = [n for n in self.knowledge_graph.nodes() 
                     if 'test' in n.lower()]
        
        for prod_file in prod_files:
            base_name = os.path.basename(prod_file).replace('.js', '')
            
            # Chercher un test correspondant
            has_test = any(base_name in test_file for test_file in test_files)
            
            coverage_info[prod_file] = {
                'has_test': has_test,
                'test_files': [t for t in test_files if base_name in t]
            }
        
        return coverage_info
    
    def check_naming_conventions(self):
        """Vérifier les conventions de nommage"""
        violations = []
        
        for node in self.knowledge_graph.nodes():
            filename = os.path.basename(node)
            
            # Vérifications de nommage
            if 'service' in filename.lower():
                if not filename.endswith('Service.js'):
                    violations.append({
                        'file': node,
                        'issue': 'Service devrait finir par "Service.js"',
                        'severity': 'low'
                    })
            
            elif 'repository' in filename.lower():
                if not filename.endswith('Repository.js'):
                    violations.append({
                        'file': node,
                        'issue': 'Repository devrait finir par "Repository.js"',
                        'severity': 'low'
                    })
        
        return violations
    
    def detect_code_smells(self):
        """Détecter les code smells"""
        print("👃 Détection des code smells...")
        
        smells = []
        
        for node in self.knowledge_graph.nodes():
            if not node.endswith('.js'):
                continue
                
            file_path = os.path.join(self.project_path, node)
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Détecter différents smells
                file_smells = []
                
                # Fichier trop long
                lines = len(content.split('\n'))
                if lines > 200:
                    file_smells.append({
                        'type': 'long_file',
                        'severity': 'medium',
                        'details': f'{lines} lignes'
                    })
                
                # Méthodes trop longues
                methods = self.extract_methods(content)
                if len(methods) > 10:
                    file_smells.append({
                        'type': 'too_many_methods',
                        'severity': 'medium', 
                        'details': f'{len(methods)} méthodes'
                    })
                
                if file_smells:
                    smells.append({
                        'file': node,
                        'smells': file_smells
                    })
                    
            except:
                continue
        
        self.violations.extend(smells)
        return smells
    
    def calculate_metrics(self):
        """Calculer les métriques du projet"""
        print("📊 Calcul des métriques...")
        
        js_files = [n for n in self.knowledge_graph.nodes() if n.endswith('.js')]
        test_files = [n for n in js_files if 'test' in n.lower()]
        domain_files = [n for n in js_files if 'domain' in n]
        infrastructure_files = [n for n in js_files if 'infrastructure' in n]
        
        metrics = {
            'total_files': len(js_files),
            'test_files': len(test_files),
            'domain_files': len(domain_files),
            'infrastructure_files': len(infrastructure_files),
            'cyclomatic_complexity': self.calculate_cyclomatic_complexity(),
            'coupling_metrics': self.calculate_coupling(),
        }
        
        # Ratios
        if metrics['total_files'] > 0:
            metrics['test_ratio'] = metrics['test_files'] / metrics['total_files']
            metrics['domain_ratio'] = metrics['domain_files'] / metrics['total_files']
        
        self.metrics = metrics
    
    def calculate_cyclomatic_complexity(self):
        """Calculer la complexité cyclomatique moyenne"""
        total_complexity = 0
        file_count = 0
        
        for node in self.knowledge_graph.nodes():
            if not node.endswith('.js') or 'test' in node.lower():
                continue
                
            file_path = os.path.join(self.project_path, node)
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Complexité basique: compter les points de décision
                complexity = (content.count('if ') + content.count('else ') + 
                            content.count('for ') + content.count('while ') +
                            content.count('case ') + content.count('catch ') + 1)
                
                total_complexity += complexity
                file_count += 1
                
            except:
                continue
        
        return total_complexity / file_count if file_count > 0 else 0
    
    def calculate_coupling(self):
        """Calculer les métriques de couplage"""
        coupling_scores = {}
        
        for node in self.knowledge_graph.nodes():
            in_degree = self.knowledge_graph.in_degree(node)  # Qui dépend de moi
            out_degree = self.knowledge_graph.out_degree(node)  # De qui je dépends
            
            coupling_scores[node] = {
                'afferent': in_degree,
                'efferent': out_degree,
                'instability': out_degree / (in_degree + out_degree) if (in_degree + out_degree) > 0 else 0
            }
        
        return coupling_scores
    
    def generate_report(self):
        """Générer un rapport complet"""
        print("📋 Génération du rapport...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'project_path': self.project_path,
            'metrics': self.metrics,
            'patterns': self.code_patterns,
            'best_practices': self.best_practices,
            'violations': self.violations,
            'recommendations': self.generate_recommendations()
        }
        
        # Sauvegarder en JSON
        with open('hexagonal_expert_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        # Sauvegarder le graphe
        with open('knowledge_graph.pkl', 'wb') as f:
            pickle.dump(self.knowledge_graph, f)
        
        print("✅ Rapport sauvegardé dans hexagonal_expert_report.json")
        return report
    
    def generate_recommendations(self):
        """Générer des recommandations"""
        recommendations = []
        
        # Recommandations basées sur les métriques
        if self.metrics.get('test_ratio', 0) < 0.8:
            recommendations.append({
                'type': 'testing',
                'priority': 'high',
                'message': 'Augmenter la couverture de tests (actuellement {:.1%})'.format(
                    self.metrics.get('test_ratio', 0)
                ),
                'action': 'Ajouter des tests pour les fichiers sans couverture'
            })
        
        # Recommandations basées sur la complexité
        if self.metrics.get('cyclomatic_complexity', 0) > 15:
            recommendations.append({
                'type': 'complexity',
                'priority': 'medium',
                'message': 'Complexité cyclomatique élevée ({:.1f})'.format(
                    self.metrics.get('cyclomatic_complexity', 0)
                ),
                'action': 'Refactoriser les méthodes complexes'
            })
        
        return recommendations
    
    def visualize_architecture(self):
        """Visualiser l'architecture"""
        print("📊 Génération de la visualisation...")
        
        try:
            plt.figure(figsize=(15, 10))
            
            # Positions basées sur les couches
            pos = {}
            layer_y = {'domain': 2, 'application': 1, 'infrastructure': 0, 'test': -1, 'other': 0.5}
            layer_counts = defaultdict(int)
            
            for node in self.knowledge_graph.nodes():
                layer = 'other'
                for l in layer_y.keys():
                    if l in node:
                        layer = l
                        break
                
                x = layer_counts[layer] * 2
                y = layer_y[layer] + (layer_counts[layer] % 3) * 0.3
                pos[node] = (x, y)
                layer_counts[layer] += 1
            
            # Couleurs par couche
            colors = {'domain': 'red', 'application': 'yellow', 'infrastructure': 'blue', 
                     'test': 'green', 'other': 'gray'}
            node_colors = [colors.get(next((l for l in colors.keys() if l in node), 'other'), 'gray') 
                          for node in self.knowledge_graph.nodes()]
            
            # Dessiner le graphe
            nx.draw(self.knowledge_graph, pos, 
                   node_color=node_colors,
                   node_size=100,
                   with_labels=False,
                   arrows=True,
                   edge_color='gray',
                   alpha=0.7)
            
            plt.title('Architecture Hexagonale - Graphe de Dépendances')
            plt.savefig('architecture_graph.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            print("✅ Graphe sauvegardé dans architecture_graph.png")
        except Exception as e:
            print(f"⚠️  Erreur lors de la visualisation: {e}")
            print("💡 Installez matplotlib: pip install matplotlib")

def main():
    print("🚀 Construction du système expert hexagonal...")
    
    expert_system = HexagonalExpertSystem()
    
    # Analyse complète
    expert_system.analyze_codebase()
    
    # Génération du rapport
    report = expert_system.generate_report()
    
    # Visualisation
    expert_system.visualize_architecture()
    
    # Résumé
    print("\n📊 RÉSUMÉ DE L'ANALYSE:")
    print(f"📁 Fichiers analysés: {expert_system.metrics.get('total_files', 0)}")
    print(f"🧪 Fichiers de test: {expert_system.metrics.get('test_files', 0)}")
    print(f"📈 Ratio de tests: {expert_system.metrics.get('test_ratio', 0):.1%}")
    print(f"🔧 Complexité moyenne: {expert_system.metrics.get('cyclomatic_complexity', 0):.1f}")
    print(f"⚠️  Violations trouvées: {len(expert_system.violations)}")
    print(f"💡 Recommandations: {len(report['recommendations'])}")
    
    print("\n🎉 Système expert construit avec succès!")
    print("📋 Consultez hexagonal_expert_report.json pour le rapport détaillé")

if __name__ == "__main__":
    main()