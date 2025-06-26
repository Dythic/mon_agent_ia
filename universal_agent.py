import os
import json
import pickle
from typing import Dict, List, Optional, Any
from pathlib import Path
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from code_analyzer import UniversalCodeAnalyzer
from config import UniversalConfig
import requests
import time

class UniversalCodeAgent:
    """Agent IA universel pour analyse et génération de code"""
    
    def __init__(self, project_path: str = None, config_path: str = "config.yaml"):
        self.project_path = project_path
        self.config = UniversalConfig(config_path)
        self.analyzer = UniversalCodeAnalyzer(self.config)
        
        print("🤖 Initialisation de l'Agent Universel...")
        
        # Analyse du projet si fourni
        self.project_info = {}
        if project_path and os.path.exists(project_path):
            self.project_info = self.analyzer.analyze_project(project_path)
            print(f"📁 Projet analysé: {self.project_info.get('language', 'Unknown')}")
        
        # Initialisation des composants
        self._setup_llm()
        self._setup_vectorstore()
        self._setup_prompts()
        
        print("✅ Agent Universel prêt!")
    
    def _setup_llm(self):
        """Configurer le modèle de langage"""
        self._wait_for_ollama()
        self.llm = OllamaLLM(
            model="deepseek-coder:6.7b", 
            temperature=0.2  # Plus déterministe pour le code
        )
    
    def _wait_for_ollama(self, max_retries: int = 30):
        """Attendre qu'Ollama soit disponible"""
        print("⏳ Connexion à Ollama...")
        for i in range(max_retries):
            try:
                response = requests.get("http://localhost:11434/api/version", timeout=2)
                if response.status_code == 200:
                    print("✅ Ollama connecté")
                    return
            except:
                pass
            if i == 0:
                print("⏳ Attente de la connexion...")
            time.sleep(1)
        raise Exception("❌ Ollama non disponible. Lancez 'ollama serve'")
    
    def _setup_vectorstore(self):
        """Configurer la base vectorielle"""
        print("📚 Configuration de la base vectorielle...")
        
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        
        # Chercher une base existante
        db_paths = ["./enhanced_chroma_db", "./chroma_db", "./vector_db"]
        db_path = None
        
        for path in db_paths:
            if os.path.exists(path):
                db_path = path
                break
        
        if db_path:
            self.vectorstore = Chroma(
                persist_directory=db_path,
                embedding_function=self.embeddings
            )
            count = self.vectorstore._collection.count()
            print(f"📊 Base vectorielle chargée: {count} documents")
        else:
            print("⚠️ Aucune base vectorielle trouvée. Lancez code_indexer.py d'abord.")
            self.vectorstore = None
    
    def _setup_prompts(self):
        """Configurer les prompts selon le projet"""
        
        # Contexte du projet détecté
        project_context = self._build_project_context()
        
        # Template principal universel
        self.main_template = f"""Tu es un EXPERT DÉVELOPPEUR polyvalent, spécialisé en génération de code de qualité.

{project_context}

CONTEXTE DU CODE:
{{context}}

DEMANDE: {{question}}

INSTRUCTIONS UNIVERSELLES:
1. **Adaptation automatique** : Utilise le langage/framework détecté du projet
2. **Respect des conventions** : Suis les patterns et styles existants
3. **Code complet** : Génère du code fonctionnel avec imports/dépendances
4. **Qualité** : Applique les principes SOLID, DRY, KISS appropriés
5. **Tests** : Inclus des tests si demandé (selon framework détecté)
6. **Documentation** : Ajoute des commentaires explicatifs

GÉNÉRATION INTELLIGENTE:"""

        # Templates spécialisés
        self.templates = {
            'general': PromptTemplate(
                template=self.main_template,
                input_variables=["context", "question"]
            ),
            'code_generation': self._create_code_generation_template(project_context),
            'test_generation': self._create_test_generation_template(project_context),
            'refactoring': self._create_refactoring_template(project_context)
        }
    
    def _build_project_context(self) -> str:
        """Construire le contexte du projet détecté"""
        if not self.project_info:
            return "PROJET: Non spécifié - Mode générique activé"
        
        info = self.project_info
        context = f"""PROJET ANALYSÉ:
📁 Langage principal: {info.get('language', 'Non détecté')}
🏗️ Framework: {info.get('framework', 'Standard')}
🧪 Framework de test: {info.get('test_framework', 'Non détecté')}
📊 Fichiers: {info.get('total_files', 0)} total, {info.get('test_files', 0)} tests
🎯 Conventions: {', '.join(info.get('conventions', ['Standard']))}
📈 Complexité: {info.get('avg_complexity', 0):.1f}
🔧 Patterns détectés: {', '.join(info.get('patterns', ['Standard']))}"""
        
        return context
    
    def _create_code_generation_template(self, project_context: str) -> PromptTemplate:
        """Template pour génération de code"""
        template = f"""Tu es un GÉNÉRATEUR DE CODE EXPERT qui s'adapte automatiquement au projet.

{project_context}

CONTEXTE DU CODE:
{{context}}

DEMANDE DE CODE: {{question}}

GÉNÉRATION ADAPTATIVE:
1. **Détection auto** : Utilise le langage/framework détecté ci-dessus
2. **Style cohérent** : Respecte les conventions du projet existant
3. **Code production** : Génère du code prêt à l'emploi
4. **Imports** : Inclus toutes les dépendances nécessaires
5. **Robustesse** : Gestion d'erreurs et validation
6. **Performance** : Code optimisé et bonnes pratiques

CODE GÉNÉRÉ ADAPTATIF:"""

        return PromptTemplate(template=template, input_variables=["context", "question"])
    
    def _create_test_generation_template(self, project_context: str) -> PromptTemplate:
        """Template pour génération de tests"""
        template = f"""Tu es un EXPERT EN TESTS qui génère des tests adaptés au framework détecté.

{project_context}

CODE À TESTER:
{{context}}

DEMANDE DE TESTS: {{question}}

GÉNÉRATION DE TESTS INTELLIGENTE:
1. **Framework adaptatif** : Utilise le framework de test détecté (pytest/Jest/JUnit/etc.)
2. **Couverture 100%** : Teste toutes les méthodes et cas limites
3. **Format standardisé** : Given-When-Then ou AAA selon les conventions
4. **Mocking intelligent** : Mock approprié selon l'architecture
5. **Tests d'intégration** : Si applicable au contexte
6. **Performance** : Tests de charge si pertinents

TESTS GÉNÈRES ADAPTÉS:"""

        return PromptTemplate(template=template, input_variables=["context", "question"])
    
    def _create_refactoring_template(self, project_context: str) -> PromptTemplate:
        """Template pour refactoring"""
        template = f"""Tu es un EXPERT EN REFACTORING qui améliore le code selon les bonnes pratiques.

{project_context}

CODE ACTUEL:
{{context}}

DEMANDE DE REFACTORING: {{question}}

REFACTORING INTELLIGENT:
1. **Principes universels** : Applique SOLID, DRY, KISS selon le langage
2. **Patterns appropriés** : Utilise les design patterns adaptés
3. **Performance** : Optimise selon les spécificités du langage/framework
4. **Lisibilité** : Améliore la structure et nommage
5. **Maintenabilité** : Réduit la complexité et le couplage
6. **Compatibilité** : Préserve l'API existante si possible

CODE REFACTORISÉ:"""

        return PromptTemplate(template=template, input_variables=["context", "question"])
    
    def detect_query_type(self, question: str) -> str:
        """Détecter le type de requête"""
        question_lower = question.lower()
        
        # Mots-clés pour chaque type
        code_keywords = ['génère', 'crée', 'écris', 'code', 'implémente', 'développe', 'classe', 'fonction']
        test_keywords = ['test', 'tests', 'jest', 'pytest', 'junit', 'coverage', 'mock', 'given when then']
        refactor_keywords = ['refactor', 'améliore', 'optimise', 'clean', 'restructure', 'solid', 'dry']
        
        if any(keyword in question_lower for keyword in test_keywords):
            return 'test_generation'
        elif any(keyword in question_lower for keyword in refactor_keywords):
            return 'refactoring'
        elif any(keyword in question_lower for keyword in code_keywords):
            return 'code_generation'
        else:
            return 'general'
    
    def ask(self, question: str, query_type: str = None) -> str:
        """Poser une question à l'agent"""
        if not query_type:
            query_type = self.detect_query_type(question)
        
        # Sélectionner le prompt approprié
        prompt = self.templates.get(query_type, self.templates['general'])
        
        # Si pas de vectorstore, réponse directe
        if not self.vectorstore:
            return self._direct_response(question, prompt)
        
        # Utiliser RAG avec vectorstore
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 8}),
            chain_type_kwargs={"prompt": prompt}
        )
        
        try:
            result = qa_chain.invoke({"query": question})
            return result["result"]
        except Exception as e:
            return f"❌ Erreur: {e}"
    
    def _direct_response(self, question: str, prompt: PromptTemplate) -> str:
        """Réponse directe sans RAG"""
        context = "Aucun contexte de code disponible - génération basée sur les bonnes pratiques universelles."
        formatted_prompt = prompt.format(context=context, question=question)
        
        try:
            return self.llm(formatted_prompt)
        except Exception as e:
            return f"❌ Erreur: {e}"
    
    def generate_code(self, specification: str, code_type: str = None) -> str:
        """Générer du code selon une spécification"""
        if code_type:
            question = f"Génère un {code_type} : {specification}"
        else:
            question = f"Génère le code suivant : {specification}"
        
        return self.ask(question, 'code_generation')
    
    def generate_tests(self, code_or_specification: str) -> str:
        """Générer des tests pour du code"""
        question = f"Génère tous les tests pour : {code_or_specification}"
        return self.ask(question, 'test_generation')
    
    def refactor_code(self, code: str, improvements: str = "") -> str:
        """Refactoriser du code"""
        question = f"Refactorise ce code {improvements}: {code}"
        return self.ask(question, 'refactoring')
    
    def get_project_summary(self) -> str:
        """Obtenir un résumé du projet"""
        if not self.project_info:
            return "Aucun projet analysé. Utilisez code_indexer.py pour analyser votre projet."
        
        info = self.project_info
        return f"""
🏗️ RÉSUMÉ DU PROJET:
📁 Langage: {info.get('language', 'Non détecté')}
🛠️ Framework: {info.get('framework', 'Standard')}
📊 Fichiers: {info.get('total_files', 0)} total, {info.get('test_files', 0)} tests
🧪 Tests: {info.get('test_coverage', 0):.1%} de couverture
📈 Complexité: {info.get('avg_complexity', 0):.1f} (moyenne)
🎯 État: {"✅ Bonne qualité" if info.get('quality_score', 0) > 7 else "⚠️ Améliorations possibles"}
🔧 Patterns: {', '.join(info.get('patterns', ['Standard']))}
"""

def main():
    """Interface en ligne de commande"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Agent IA Universel pour génération de code')
    parser.add_argument('--project', '-p', help='Chemin vers le projet à analyser')
    parser.add_argument('--config', '-c', default='config.yaml', help='Fichier de configuration')
    args = parser.parse_args()
    
    try:
        # Initialiser l'agent
        agent = UniversalCodeAgent(args.project, args.config)
        
        print("\n" + "="*70)
        print("🤖 AGENT IA UNIVERSEL - GÉNÉRATION DE CODE")
        print("="*70)
        
        # Afficher le résumé du projet
        print(agent.get_project_summary())
        
        print("\n💡 EXEMPLES D'UTILISATION:")
        print("- 'Génère une classe User avec validation'")
        print("- 'Crée des tests pour cette fonction'") 
        print("- 'Refactorise ce code selon SOLID'")
        print("- 'Explique ce pattern de code'")
        
        # Boucle interactive
        while True:
            question = input("\n🎯 Votre demande (ou 'quit'): ")
            if question.lower() in ['quit', 'exit', 'q']:
                break
            
            query_type = agent.detect_query_type(question)
            print(f"🔍 Type détecté: {query_type}")
            print("💭 Traitement...")
            
            answer = agent.ask(question, query_type)
            print(f"\n🤖 Agent ({query_type}):\n{answer}")
    
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    main()