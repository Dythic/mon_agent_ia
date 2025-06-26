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
        
        # Modèle Ollama
        self.llm = OllamaLLM(model="deepseek-coder:6.7b", temperature=0.1)
        
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
        
        # Template pour questions générales
        self.general_template = f"""Tu es un EXPERT SÉNIOR en architecture hexagonale, spécialisé sur ce projet Node.js spécifique.

{base_context}

CONTEXTE DU CODE:
{{context}}

QUESTION: {{question}}

INSTRUCTIONS:
- Utilise ton analyse experte complète du projet
- Référence les patterns architecturaux détectés
- Mentionne les violations si pertinentes
- Donne des conseils concrets et spécifiques au projet
- Utilise les métriques pour contextualiser tes réponses

RÉPONSE EXPERTE:"""
        
        # Template pour refactoring
        self.refactoring_template = f"""Tu es un EXPERT en refactoring et architecture hexagonale.

{base_context}

ANALYSE DU CODE À REFACTORISER:
{{context}}

DEMANDE DE REFACTORING: {{question}}

APPROCHE EXPERTE:
1. Identifie les violations des principes hexagonaux
2. Propose des améliorations basées sur les patterns détectés
3. Considère les métriques de complexité actuelles
4. Assure la compatibilité avec l'architecture existante

PLAN DE REFACTORING DÉTAILLÉ:"""

        # Template pour tests
        self.testing_template = f"""Tu es un EXPERT en tests pour architecture hexagonale.

{base_context}

COUVERTURE ACTUELLE: {metrics.get('test_ratio', 0):.1%}

CODE À TESTER:
{{context}}

DEMANDE DE TESTS: {{question}}

STRATÉGIE DE TESTS EXPERTE:
- Respecte les principes de l'architecture hexagonale
- Adapte selon la couche (Domain/Infrastructure/Application)
- Utilise les patterns de test appropriés
- Vise 100% de couverture

TESTS PROPOSÉS:"""
        
        self.prompts = {
            'general': PromptTemplate(template=self.general_template, input_variables=["context", "question"]),
            'refactoring': PromptTemplate(template=self.refactoring_template, input_variables=["context", "question"]),
            'testing': PromptTemplate(template=self.testing_template, input_variables=["context", "question"])
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
        """Détecter le type de question"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['test', 'jest', 'coverage', 'mock', 'given when then']):
            return 'testing'
        elif any(word in question_lower for word in ['refactor', 'improve', 'optimize', 'clean', 'restructure']):
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
        print("2. 🔧 Conseils de refactoring spécialisés")
        print("3. 🧪 Stratégies de tests avancées")
        print("4. 📊 Analyse basée sur les métriques du projet")
        print("5. 🏗️  Recommandations architecturales")

def main():
    agent = MasterHexagonalAgent()
    
    print("\n" + "="*70)
    print("🧠 AGENT EXPERT HEXAGONAL - NIVEAU MAÎTRE")
    print("="*70)
    
    # Afficher le résumé du projet
    print(agent.get_project_summary())
    
    print("\n💬 EXEMPLES DE QUESTIONS:")
    print("- 'Analyse les violations architecturales de ce projet'")
    print("- 'Comment refactoriser UserService selon les bonnes pratiques?'")
    print("- 'Génère tous les tests manquants pour atteindre 100% de coverage'")
    print("- 'Explique les patterns détectés dans ce projet'")
    
    while True:
        question = input("\n🎯 Votre question experte (ou 'quit'): ")
        if question.lower() in ['quit', 'exit', 'q']:
            break
        
        query_type = agent.detect_query_type(question)
        print(f"\n🔍 Type détecté: {query_type}")
        print("💭 Analyse experte en cours...")
        
        answer = agent.ask_expert(question, query_type)
        print(f"\n🧠 Expert Hexagonal ({query_type}):\n{answer}")

if __name__ == "__main__":
    main()