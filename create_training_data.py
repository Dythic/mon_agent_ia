import os
import json
import torch
from pathlib import Path
from datetime import datetime

def get_all_files(project_path="/home/dythic/projet/hexagonal-nodejs-example"):
    """Récupérer tous les fichiers du projet"""
    files = []
    extensions = ['.js', '.ts', '.jsx', '.tsx', '.json', '.md', '.test.js']
    excluded_dirs = ['node_modules', '.git', 'dist', 'build', 'coverage']
    
    for root, dirs, file_list in os.walk(project_path):
        dirs[:] = [d for d in dirs if d not in excluded_dirs]
        
        for file in file_list:
            if any(file.endswith(ext) for ext in extensions):
                files.append(os.path.join(root, file))
    
    return files

def read_file(file_path):
    """Lire le contenu d'un fichier"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        print(f"Erreur lecture {file_path}: {e}")
        return ""

def detect_file_type(file_path):
    """Détecter le type de fichier (entity, service, controller, etc.)"""
    if 'entities' in file_path:
        return 'entity'
    elif 'services' in file_path:
        return 'service'
    elif 'controllers' in file_path or 'Controller' in file_path:
        return 'controller'
    elif 'repositories' in file_path or 'Repository' in file_path:
        return 'repository'
    elif 'test' in file_path.lower():
        return 'test'
    elif 'middleware' in file_path:
        return 'middleware'
    else:
        return 'utility'

def detect_layer(file_path):
    """Détecter la couche architecturale"""
    if 'domain' in file_path:
        return 'domain'
    elif 'infrastructure' in file_path:
        return 'infrastructure'
    elif 'application' in file_path:
        return 'application'
    else:
        return 'other'

def generate_expert_answer(content, question, file_path):
    """Générer une réponse experte basée sur le contenu"""
    file_type = detect_file_type(file_path)
    layer = detect_layer(file_path)
    filename = os.path.basename(file_path)
    
    if "explique-moi le fichier" in question.lower():
        return f"""Ce fichier {filename} est un {file_type} de la couche {layer} dans l'architecture hexagonale.

Structure du fichier:
- Type: {file_type}
- Couche: {layer}
- Localisation: {file_path}

Fonctionnalités principales:
{extract_main_functions(content)}

Dans l'architecture hexagonale, ce fichier joue le rôle de {get_hexagonal_role(file_type, layer)}.
"""
    
    elif "comment fonctionne" in question.lower():
        return f"""Le {file_type} {filename} fonctionne selon les principes de l'architecture hexagonale:

Méthodes principales:
{extract_methods(content)}

Dépendances:
{extract_dependencies(content)}

Pattern utilisé: {get_pattern_description(file_type, layer)}
"""
    
    elif "comment tester" in question.lower():
        return f"""Pour tester {filename} ({file_type} de la couche {layer}):

1. **Type de tests recommandés:**
{get_test_strategy(file_type, layer)}

2. **Mocking strategy:**
{get_mocking_strategy(layer)}

3. **Structure de test Given-When-Then:**
```javascript
describe('{filename.replace('.js', '')}', () => {{
  describe('methodName', () => {{
    test('should [behavior] when [condition]', () => {{
      // Given
      // When  
      // Then
    }});
  }});
}});
```"""
    
    return f"Analyse du fichier {filename}: {content[:200]}..."

def extract_main_functions(content):
    """Extraire les fonctions principales"""
    functions = []
    lines = content.split('\n')
    
    for line in lines:
        if 'function ' in line or 'const ' in line and '=>' in line:
            functions.append(line.strip())
    
    return '\n'.join(functions[:5]) if functions else "Aucune fonction détectée"

def extract_methods(content):
    """Extraire les méthodes"""
    methods = []
    lines = content.split('\n')
    
    for line in lines:
        if line.strip().endswith('{') and ('(' in line and ')' in line):
            methods.append(line.strip())
    
    return '\n'.join(methods[:5]) if methods else "Aucune méthode détectée"

def extract_dependencies(content):
    """Extraire les dépendances"""
    dependencies = []
    lines = content.split('\n')
    
    for line in lines:
        if 'require(' in line or 'import ' in line:
            dependencies.append(line.strip())
    
    return '\n'.join(dependencies) if dependencies else "Aucune dépendance détectée"

def get_hexagonal_role(file_type, layer):
    """Décrire le rôle dans l'architecture hexagonale"""
    roles = {
        ('entity', 'domain'): "une entité métier qui encapsule les règles business",
        ('service', 'domain'): "un service de domaine qui orchestre la logique métier",
        ('repository', 'infrastructure'): "un adaptateur qui implémente la persistance",
        ('controller', 'infrastructure'): "un adaptateur web qui gère les requêtes HTTP",
        ('test', 'domain'): "un test unitaire qui valide les règles métier"
    }
    return roles.get((file_type, layer), f"un composant {file_type} de la couche {layer}")

def get_test_strategy(file_type, layer):
    """Stratégie de test selon le type et la couche"""
    if layer == 'domain':
        return "- Tests unitaires purs sans mocks\n- Validation des règles métier\n- Tests des edge cases"
    elif layer == 'infrastructure':
        return "- Tests d'intégration avec mocks\n- Tests des adapters\n- Tests de contrat"
    else:
        return "- Tests unitaires et d'intégration\n- Validation du comportement"

def get_mocking_strategy(layer):
    """Stratégie de mocking selon la couche"""
    if layer == 'domain':
        return "Pas de mocks externes, seulement des doubles de test simples"
    elif layer == 'infrastructure':
        return "Mock des services externes (DB, APIs, etc.)"
    else:
        return "Mock selon les dépendances"

def get_pattern_description(file_type, layer):
    """Description du pattern utilisé"""
    patterns = {
        ('entity', 'domain'): "Domain Entity Pattern",
        ('service', 'domain'): "Domain Service Pattern",
        ('repository', 'infrastructure'): "Repository Pattern",
        ('controller', 'infrastructure'): "Adapter Pattern"
    }
    return patterns.get((file_type, layer), "Pattern standard")

def create_training_dataset():
    """Créer le dataset d'entraînement"""
    print("🔍 Création du dataset d'entraînement...")
    
    training_data = []
    files = get_all_files()
    
    print(f"📁 Trouvé {len(files)} fichiers")
    
    for file_path in files:
        content = read_file(file_path)
        if not content.strip():
            continue
            
        # Questions types pour chaque fichier
        questions = [
            f"Explique-moi le fichier {os.path.basename(file_path)}",
            f"Comment fonctionne la classe dans {os.path.basename(file_path)}?",
            f"Quelles sont les dépendances de {os.path.basename(file_path)}?",
            f"Comment tester le code dans {os.path.basename(file_path)}?"
        ]
        
        for question in questions:
            answer = generate_expert_answer(content, question, file_path)
            training_data.append({
                "instruction": question,
                "input": f"Fichier: {file_path}\nContenu:\n{content[:1500]}...",
                "output": answer
            })
    
    # Sauvegarder le dataset
    with open('hexagonal_training_data.json', 'w', encoding='utf-8') as f:
        json.dump(training_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Dataset créé: {len(training_data)} exemples")
    print(f"💾 Sauvegardé dans: hexagonal_training_data.json")
    
    return training_data

if __name__ == "__main__":
    # Vérifier que torch est disponible
    if torch.cuda.is_available():
        print(f"🔥 GPU détecté: {torch.cuda.get_device_name(0)}")
    else:
        print("💻 Mode CPU")
    
    # Créer le dataset
    dataset = create_training_dataset()
    
    print("\n📊 Statistiques du dataset:")
    print(f"- Total exemples: {len(dataset)}")
    print(f"- Première entrée: {dataset[0]['instruction']}")