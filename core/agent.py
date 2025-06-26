"""
Agent principal simplifié
"""
from typing import Dict, Optional
from core.llm_handler import LLMHandler
from core.vectorstore import VectorStoreHandler
from core.prompts import PromptManager
from generators.templates import CodeTemplateGenerator
from analyzers.project_analyzer import ProjectAnalyzer
from utils.imports import RetrievalQA, LANGCHAIN_AVAILABLE

class UniversalCodeAgent:
    """Agent IA universel simplifié"""
    
    def __init__(self, project_path: str = None, config_path: str = "config.yaml"):
        self.project_path = project_path
        
        print("🤖 Initialisation de l'Agent Universel...")
        
        # Analyser le projet
        self.project_info = {}
        if project_path:
            analyzer = ProjectAnalyzer()
            self.project_info = analyzer.analyze_project(project_path)
        
        # Initialiser les composants
        self.llm_handler = LLMHandler()
        self.vectorstore_handler = VectorStoreHandler()
        self.prompt_manager = PromptManager(self.project_info)
        self.template_generator = CodeTemplateGenerator(self.project_info)
        
        print("✅ Agent Universel prêt!")
    
    def detect_query_type(self, question: str) -> str:
        """Détecter le type de requête"""
        question_lower = question.lower()
        
        code_keywords = ['génère', 'crée', 'écris', 'code', 'classe', 'fonction']
        test_keywords = ['test', 'tests', 'pytest', 'junit']
        refactor_keywords = ['refactor', 'améliore', 'optimise', 'solid']
        
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
        
        # Mode RAG si disponible
        if LANGCHAIN_AVAILABLE and self.vectorstore_handler.is_available():
            return self._ask_with_rag(question, query_type)
        else:
            return self._ask_direct(question, query_type)
    
    def _ask_with_rag(self, question: str, query_type: str) -> str:
        """Question avec RAG"""
        try:
            prompt = self.prompt_manager.get_template(query_type)
            retriever = self.vectorstore_handler.get_retriever()
            
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm_handler.llm,
                chain_type="stuff",
                retriever=retriever,
                chain_type_kwargs={"prompt": prompt} if hasattr(prompt, 'format') else {},
                return_source_documents=False
            )
            
            result = qa_chain.invoke({"query": question})
            
            if isinstance(result, dict):
                for key in ["result", "answer", "output"]:
                    if key in result:
                        return result[key]
            return str(result)
            
        except Exception as e:
            print(f"⚠️ Erreur RAG: {e}")
            return self._ask_direct(question, query_type)
    
    def _ask_direct(self, question: str, query_type: str) -> str:
        """Question directe"""
        context = "Aucun contexte de code disponible."
        
        # Si LLM disponible, utiliser les prompts
        if self.llm_handler.is_available():
            formatted_prompt = self.prompt_manager.format_prompt(query_type, context, question)
            return self.llm_handler.invoke(formatted_prompt)
        else:
            # Fallback vers templates
            return self._generate_fallback_response(question, query_type)
    
    def _generate_fallback_response(self, question: str, query_type: str) -> str:
        """Réponse de fallback avec templates"""
        question_lower = question.lower()
        
        if 'classe' in question_lower or 'class' in question_lower:
            return self.template_generator.generate_class_template()
        elif 'fonction' in question_lower or 'function' in question_lower:
            return self.template_generator.generate_function_template()
        elif 'test' in question_lower:
            return self.template_generator.generate_test_template()
        else:
            return """
🤖 **Conseils de Développement Génériques**

Pour une aide spécifique, installez Ollama et relancez votre question.

**Bonnes pratiques:**
1. Code lisible et bien documenté
2. Tests avec bonne couverture
3. Respect des principes SOLID
4. Gestion d'erreurs appropriée
5. Performance optimisée
"""
    
    def generate_code(self, specification: str, code_type: str = None) -> str:
        """Générer du code"""
        question = f"Génère un {code_type or 'code'} : {specification}"
        return self.ask(question, 'code_generation')
    
    def generate_tests(self, code_or_specification: str) -> str:
        """Générer des tests"""
        question = f"Génère des tests pour : {code_or_specification}"
        return self.ask(question, 'test_generation')
    
    def refactor_code(self, code: str, improvements: str = "") -> str:
        """Refactoriser du code"""
        question = f"Refactorise ce code {improvements}: {code}"
        return self.ask(question, 'refactoring')
    
    def get_project_summary(self) -> str:
        """Obtenir un résumé du projet"""
        if not self.project_info:
            return "Aucun projet analysé."
        
        info = self.project_info
        metrics = info.get('metrics', {})
        
        return f"""
🏗️ RÉSUMÉ DU PROJET:
📁 Langage: {info.get('language', 'Non détecté')}
🛠️ Framework: {info.get('framework', 'Standard')}
📊 Fichiers: {metrics.get('total_files', 0)} total
🧪 Tests: {metrics.get('test_files', 0)} fichiers
⭐ Score qualité: {info.get('quality_score', 0)}/10
"""