import json
import os
import pickle
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

class MasterHexagonalAgent:
    def __init__(self):
        print("🧠 Initialisation de l'agent expert maître...")
        
        # Charger le rapport d'analyse
        with open('hexagonal_expert_report.json', 'r') as f:
            self.expert_report = json.load(f)
        
        # Charger le graphe de connaissances
        with open('knowledge_graph.pkl', 'rb') as f:
            self.knowledge_graph = pickle.load(f)
        
        # Charger les données d'entraînement
        if os.path.exists('hexagonal_training_data.json'):
            with open('hexagonal_training_data.json', 'r') as f:
                self.training_data = json.load(f)
        else:
            self.training_data = []
        
        # Base vectorielle optimisée
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        
        db_path = "./enhanced_chroma_db" if os.path.exists("./enhanced_chroma_db") else "./chroma_db"
        self.vectorstore = Chroma(
            persist_directory=db_path,
            embedding_function=self.embeddings
        )
        
        # Modèle Ollama optimisé pour la génération de code
        self.llm = OllamaLLM(model="deepseek-coder:6.7b", temperature=0.2)  # Température plus basse pour du code
        
        # Configuration des prompts spécialisés
        self.setup_specialized_prompts()
        
        print("✅ Agent expert maître prêt!")
        self.print_capabilities()
    
    def setup_specialized_prompts(self):
        """Configurer des prompts spécialisés selon le contexte"""
        
        # Extraire les insights du rapport
        metrics = self.expert_report.get('metrics', {})
        patterns = self.expert_report.get('patterns', {})
        violations = self.expert_report.get('violations', [])
        
        # Template de base enrichi avec l'analyse
        base_context = f"""
ANALYSE EXPERT DU PROJET:
- Fichiers analysés: {metrics.get('total_files', 0)}
- Ratio de tests: {metrics.get('test_ratio', 0):.1%}
- Complexité moyenne: {metrics.get('cyclomatic_complexity', 0):.1f}
- Patterns détectés: {len([p for p in patterns.values() if p])} types
- Violations: {len(violations)} détectées

PATTERNS ARCHITECTURAUX IDENTIFIÉS:
{self.format_patterns(patterns)}

VIOLATIONS PRINCIPALES:
{self.format_violations(violations[:3])}
"""
        
        # Template pour génération de code
        self.code_generation_template = f"""Tu es un EXPERT DÉVELOPPEUR en architecture hexagonale Node.js, spécialisé sur ce projet.

{base_context}

CONTEXTE DU PROJET:
{{context}}

DEMANDE DE CODE: {{question}}

INSTRUCTIONS POUR LA GÉNÉRATION DE CODE:
1. Respecte STRICTEMENT l'architecture hexagonale du projet
2. Utilise les patterns et conventions détectés dans le projet existant
3. Génère du code complet, fonctionnel et testé
4. Inclus les imports nécessaires
5. Respecte les bonnes pratiques détectées dans l'analyse
6. Ajoute des commentaires explicatifs
7. Inclus la gestion d'erreurs appropriée

STYLE DE CODE À RESPECTER:
- CommonJS (require/module.exports) comme dans le projet
- Conventions de nommage existantes
- Structure des classes et méthodes du projet
- Patterns d'injection de dépendances détectés

CODE GÉNÉRÉ:"""

        # Template pour tests Given-When-Then
        self.test_generation_template = f"""Tu es un EXPERT en tests Jest pour architecture hexagonale.

{base_context}

COUVERTURE ACTUELLE: {metrics.get('test_ratio', 0):.1%}

CODE À TESTER:
{{context}}

DEMANDE DE TESTS: {{question}}

INSTRUCTIONS POUR LES TESTS:
1. Format STRICT Given-When-Then dans TOUS les tests
2. Couverture 100% de toutes les méthodes et branches
3. Tests unitaires pour Domain, tests d'intégration pour Infrastructure
4. Mocking approprié selon la couche architecturale
5. Edge cases et gestion d'erreurs
6. Tests de performance si nécessaire
7. Validation des contracts pour les ports

TEMPLATE DE TEST À RESPECTER:
```javascript
describe('ClassName', () => {{
  describe('methodName', () => {{
    test('should [expected behavior] when [condition]', () => {{
      // Given (Arrange)
      const input = 'test data';
      const mockDependency = jest.fn().mockReturnValue(expectedOutput);
      
      // When (Act)
      const result = methodUnderTest(input);
      
      // Then (Assert)
      expect(result).toBe(expectedOutput);
      expect(mockDependency).toHaveBeenCalledWith(input);
    }});
  }});
}});
TESTS COMPLETS GÉNÉRÉS:"""
    # Template pour refactoring avec code
    self.refactoring_template = f"""Tu es un EXPERT en refactoring d'architecture hexagonale.
{base_context}
CODE ACTUEL À REFACTORISER:
{{context}}
DEMANDE DE REFACTORING: {{question}}
APPROCHE DE REFACTORING:

Identifie les violations des principes SOLID et hexagonaux
Propose le code refactorisé complet
Explique les améliorations apportées
Maintient la compatibilité avec l'architecture existante
Améliore les métriques de qualité
Inclus les tests mis à jour si nécessaire

CODE REFACTORISÉ COMPLET:"""
    # Template général amélioré
    self.general_template = f"""Tu es un EXPERT SÉNIOR en architecture hexagonale, spécialisé sur ce projet Node.js.
{base_context}
CONTEXTE DU CODE:
{{context}}
QUESTION: {{question}}
INSTRUCTIONS:

Utilise ton analyse experte complète du projet
Si on demande du code, génère du code complet et fonctionnel
Référence les patterns architecturaux détectés
Mentionne les violations si pertinentes
Donne des conseils concrets avec exemples de code
Utilise les métriques pour contextualiser tes réponses

RÉPONSE EXPERTE (avec code si demandé):"""
    self.prompts = {
        'general': PromptTemplate(template=self.general_template, input_variables=["context", "question"]),
        'code_generation': PromptTemplate(template=self.code_generation_template, input_variables=["context", "question"]),
        'test_generation': PromptTemplate(template=self.test_generation_template, input_variables=["context", "question"]),
        'refactoring': PromptTemplate(template=self.refactoring_template, input_variables=["context", "question"])
    }

def format_patterns(self, patterns):
    """Formater les patterns pour l'affichage"""
    formatted = []
    for pattern_name, pattern_data in patterns.items():
        if pattern_data:
            count = len(pattern_data) if isinstance(pattern_data, list) else 1
            formatted.append(f"- {pattern_name}: {count} instances")
    return "\n".join(formatted) if formatted else "Aucun pattern spécifique détecté"

def format_violations(self, violations):
    """Formater les violations pour l'affichage"""
    if not violations:
        return "Aucune violation majeure"
    
    formatted = []
    for violation in violations:
        if isinstance(violation, dict):
            severity = violation.get('severity', 'unknown')
            issue = violation.get('issue', 'Unknown issue')
            formatted.append(f"- {severity.upper()}: {issue}")
    return "\n".join(formatted)

def detect_query_type(self, question):
    """Détecter le type de question avec génération de code"""
    question_lower = question.lower()
    
    # Détection spécifique pour génération de code
    code_keywords = ['génère', 'crée', 'écris', 'code', 'implémente', 'développe', 'programme']
    test_keywords = ['test', 'jest', 'coverage', 'mock', 'given when then', 'spec']
    refactor_keywords = ['refactor', 'improve', 'optimize', 'clean', 'restructure', 'réorganise']
    
    if any(keyword in question_lower for keyword in test_keywords):
        return 'test_generation'
    elif any(keyword in question_lower for keyword in code_keywords):
        return 'code_generation'
    elif any(keyword in question_lower for keyword in refactor_keywords):
        return 'refactoring'
    else:
        return 'general'

def ask_expert(self, question, query_type=None):
    """Poser une question à l'expert"""
    if not query_type:
        query_type = self.detect_query_type(question)
    
    prompt = self.prompts.get(query_type, self.prompts['general'])
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=self.llm,
        chain_type="stuff",
        retriever=self.vectorstore.as_retriever(search_kwargs={"k": 8}),
        chain_type_kwargs={"prompt": prompt}
    )
    
    return qa_chain.invoke({"query": question})["result"]

def generate_specific_code(self, code_type, specifications):
    """Générer du code spécifique selon le type demandé"""
    templates = {
        'entity': self._generate_entity_code,
        'service': self._generate_service_code,
        'repository': self._generate_repository_code,
        'controller': self._generate_controller_code,
        'test': self._generate_test_code,
        'middleware': self._generate_middleware_code
    }
    
    generator = templates.get(code_type)
    if generator:
        return generator(specifications)
    else:
        return self.ask_expert(f"Génère du code {code_type} avec ces spécifications: {specifications}", 'code_generation')

def _generate_entity_code(self, specs):
    """Générer une entité du domain"""
    question = f"Génère une entité du domain pour {specs}. Inclus toutes les validations métier et méthodes nécessaires."
    return self.ask_expert(question, 'code_generation')

def _generate_service_code(self, specs):
    """Générer un service du domain"""
    question = f"Génère un service du domain pour {specs}. Inclus la logique métier et l'injection de dépendances."
    return self.ask_expert(question, 'code_generation')

def _generate_repository_code(self, specs):
    """Générer un repository d'infrastructure"""
    question = f"Génère un repository d'infrastructure pour {specs}. Inclus l'implémentation du port et la gestion d'erreurs."
    return self.ask_expert(question, 'code_generation')

def _generate_controller_code(self, specs):
    """Générer un controller web"""
    question = f"Génère un controller web pour {specs}. Inclus les routes, validation et gestion d'erreurs."
    return self.ask_expert(question, 'code_generation')

def _generate_test_code(self, specs):
    """Générer des tests"""
    question = f"Génère tous les tests Jest au format Given-When-Then pour {specs}. Vise 100% de couverture."
    return self.ask_expert(question, 'test_generation')

def _generate_middleware_code(self, specs):
    """Générer un middleware"""
    question = f"Génère un middleware pour {specs}. Inclus la logique de validation et gestion d'erreurs."
    return self.ask_expert(question, 'code_generation')

def get_project_summary(self):
    """Obtenir un résumé du projet"""
    metrics = self.expert_report.get('metrics', {})
    recommendations = self.expert_report.get('recommendations', [])
    
    summary = f"""
🏗️  RÉSUMÉ ARCHITECTURAL:
📁 Fichiers: {metrics.get('total_files', 0)} total, {metrics.get('test_files', 0)} tests
📊 Métriques: Complexité {metrics.get('cyclomatic_complexity', 0):.1f}, Coverage {metrics.get('test_ratio', 0):.1%}
🎯 État: {"✅ Bonne architecture" if metrics.get('test_ratio', 0) > 0.8 else "⚠️ Améliorations possibles"}
💡 RECOMMANDATIONS PRIORITAIRES:
"""
for rec in recommendations:
summary += f"- {rec.get('priority', 'medium').upper()}: {rec.get('message', 'N/A')}\n"
    return summary

def print_capabilities(self):
    """Afficher les capacités de l'agent"""
    print("\n🎯 CAPACITÉS DE L'AGENT EXPERT:")
    print("1. 💬 Questions générales sur l'architecture")
    print("2. 🔧 Conseils de refactoring avec code complet")
    print("3. 🧪 Génération de tests Given-When-Then")
    print("4. 💻 Génération de code (entités, services, repositories, controllers)")
    print("5. 📊 Analyse basée sur les métriques du projet")
    print("6. 🏗️  Recommandations architecturales avec exemples")
def main():
agent = MasterHexagonalAgent()
print("\n" + "="*70)
print("🧠 AGENT EXPERT HEXAGONAL - GÉNÉRATEUR DE CODE")
print("="*70)

# Afficher le résumé du projet
print(agent.get_project_summary())

print("\n💻 EXEMPLES DE GÉNÉRATION DE CODE:")
print("- 'Génère une entité Product avec validations métier'")
print("- 'Crée un service OrderService avec injection de dépendances'")
print("- 'Implémente un ProductRepository avec MongoDB'")
print("- 'Écris tous les tests pour UserService au format Given-When-Then'")
print("- 'Développe un middleware d'authentification JWT'")
print("- 'Refactorise AuthController selon les bonnes pratiques'")

while True:
    question = input("\n🎯 Votre demande de code (ou 'quit'): ")
    if question.lower() in ['quit', 'exit', 'q']:
        break
    
    query_type = agent.detect_query_type(question)
    print(f"\n🔍 Type détecté: {query_type}")
    print("💭 Génération en cours...")
    
    answer = agent.ask_expert(question, query_type)
    print(f"\n💻 Code Généré ({query_type}):\n{answer}")
if name == "main":
main()

## 🎯 Mise à jour de l'interface Streamlit pour la génération de code

Ajoutez ces sections à `expert_app.py` :

```python
# Ajoutez cet onglet dans la fonction main() après les autres tabs
tab5 = st.tabs(["💬 Chat Expert", "📊 Dashboard", "🔍 Analyse", "🎯 Recommandations", "💻 Générateur de Code"])[4]

with tab5:
    code_generator_interface()

# Ajoutez cette fonction à expert_app.py
def code_generator_interface():
    """Interface de génération de code"""
    st.header("💻 Générateur de Code Expert")
    st.markdown("*Génération de code respectant l'architecture hexagonale de votre projet*")
    
    # Charger l'agent
    agent = load_expert_agent()
    if not agent:
        st.error("❌ Impossible de charger l'agent expert")
        return
    
    # Types de code prédéfinis
    st.subheader("🚀 Génération Rapide")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🏗️ Domain Layer**")
        if st.button("📦 Nouvelle Entité", help="Génère une entité du domain"):
            st.session_state.code_type = "entity"
        if st.button("⚙️ Nouveau Service", help="Génère un service du domain"):
            st.session_state.code_type = "service"
    
    with col2:
        st.markdown("**🔌 Infrastructure**")
        if st.button("💾 Nouveau Repository", help="Génère un repository"):
            st.session_state.code_type = "repository"
        if st.button("🌐 Nouveau Controller", help="Génère un controller web"):
            st.session_state.code_type = "controller"
    
    with col3:
        st.markdown("**🧪 Tests & Utils**")
        if st.button("🧪 Tests Complets", help="Génère des tests Given-When-Then"):
            st.session_state.code_type = "test"
        if st.button("🛡️ Middleware", help="Génère un middleware"):
            st.session_state.code_type = "middleware"
    
    # Formulaire de spécifications
    st.subheader("📝 Spécifications")
    
    # Type de code sélectionné
    if 'code_type' in st.session_state:
        code_type = st.session_state.code_type
        del st.session_state.code_type
    else:
        code_type = st.selectbox(
            "Type de code à générer:",
            ["entity", "service", "repository", "controller", "test", "middleware", "custom"],
            format_func=lambda x: {
                "entity": "📦 Entité Domain",
                "service": "⚙️ Service Domain", 
                "repository": "💾 Repository Infrastructure",
                "controller": "🌐 Controller Web",
                "test": "🧪 Tests Jest",
                "middleware": "🛡️ Middleware",
                "custom": "🎨 Code Personnalisé"
            }[x]
        )
    
    # Spécifications détaillées
    if code_type != "custom":
        specs = st.text_area(
            f"Spécifications pour {code_type}:",
            placeholder=f"Ex: {get_placeholder_for_type(code_type)}",
            height=100
        )
    else:
        specs = st.text_area(
            "Description détaillée du code à générer:",
            placeholder="Décrivez précisément le code que vous souhaitez générer...",
            height=150
        )
    
    # Options avancées
    with st.expander("⚙️ Options Avancées"):
        include_tests = st.checkbox("Inclure les tests", value=True)
        include_docs = st.checkbox("Inclure la documentation", value=True)
        follow_existing = st.checkbox("Suivre les patterns existants", value=True)
    
    # Génération
    if st.button("🚀 Générer le Code", type="primary"):
        if specs.strip():
            with st.spinner("💻 Génération du code en cours..."):
                try:
                    if code_type == "custom":
                        question = f"Génère le code suivant: {specs}"
                        if include_tests:
                            question += " Inclus les tests Jest au format Given-When-Then."
                        if include_docs:
                            question += " Inclus la documentation complète."
                        
                        code = agent.ask_expert(question, 'code_generation')
                    else:
                        full_specs = specs
                        if include_tests:
                            full_specs += " Inclus les tests complets."
                        if include_docs:
                            full_specs += " Inclus la documentation."
                        
                        code = agent.generate_specific_code(code_type, full_specs)
                    
                    # Affichage du code généré
                    st.subheader("💻 Code Généré")
                    st.code(code, language='javascript')
                    
                    # Bouton de téléchargement
                    st.download_button(
                        label="💾 Télécharger le code",
                        data=code,
                        file_name=f"{code_type}_{specs.split()[0] if specs.split() else 'generated'}.js",
                        mime="text/javascript"
                    )
                    
                except Exception as e:
                    st.error(f"❌ Erreur lors de la génération: {e}")
        else:
            st.warning("⚠️ Veuillez fournir des spécifications")

def get_placeholder_for_type(code_type):
    """Obtenir un placeholder selon le type de code"""
    placeholders = {
        "entity": "Product avec propriétés name, price, description et validations métier",
        "service": "OrderService pour gérer les commandes avec calcul des totaux",
        "repository": "ProductRepository avec MongoDB pour les opérations CRUD",
        "controller": "ProductController avec routes GET, POST, PUT, DELETE",
        "test": "UserService avec tous les cas de test et 100% de couverture",
        "middleware": "Authentification JWT avec validation des tokens"
    }
    return placeholders.get(code_type, "Décrivez votre besoin...")