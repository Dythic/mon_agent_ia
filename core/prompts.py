"""
Templates de prompts pour l'agent
"""
from typing import Dict, Any
from utils.imports import PromptTemplate, LANGCHAIN_AVAILABLE

class PromptManager:
    """Gestionnaire de prompts"""
    
    def __init__(self, project_info: Dict[str, Any] = None):
        self.project_info = project_info or {}
        self.project_context = self._build_project_context()
        self.templates = self._setup_templates()
    
    def _build_project_context(self) -> str:
        """Construire le contexte du projet"""
        if not self.project_info:
            return "PROJET: Non spécifié - Mode générique activé"
        
        info = self.project_info
        metrics = info.get('metrics', {})
        
        context = f"""PROJET ANALYSÉ:
📁 Langage principal: {info.get('language', 'Non détecté')}
🏗️ Framework: {info.get('framework', 'Standard')}
🧪 Framework de test: {info.get('test_framework', 'Non détecté')}
📊 Fichiers: {metrics.get('total_files', 0)} total, {metrics.get('test_files', 0)} tests
🎯 Conventions: {', '.join(info.get('conventions', ['Standard']))}
📈 Complexité: {metrics.get('avg_complexity', 0):.1f}
🔧 Patterns détectés: {', '.join(info.get('patterns', ['Standard']))}"""
        
        return context
    
    def _setup_templates(self) -> Dict[str, Any]:
        """Configurer les templates"""
        base_template = f"""Tu es un EXPERT DÉVELOPPEUR polyvalent.

{self.project_context}

CONTEXTE: {{context}}
DEMANDE: {{question}}

INSTRUCTIONS:
1. Adapte-toi au langage/framework détecté
2. Respecte les conventions du projet
3. Génère du code complet et fonctionnel
4. Applique les bonnes pratiques (SOLID, DRY, KISS)
5. Inclus la documentation appropriée

RÉPONSE:"""

        if LANGCHAIN_AVAILABLE and PromptTemplate:
            return {
                'general': PromptTemplate(
                    template=base_template,
                    input_variables=["context", "question"]
                ),
                'code_generation': self._create_code_template(),
                'test_generation': self._create_test_template(),
                'refactoring': self._create_refactor_template()
            }
        else:
            # Templates simples sans PromptTemplate
            return {
                'general': base_template,
                'code_generation': base_template,
                'test_generation': base_template,
                'refactoring': base_template
            }
    
    def _create_code_template(self):
        """Template pour génération de code"""
        template = f"""Tu es un GÉNÉRATEUR DE CODE EXPERT.

{self.project_context}

CONTEXTE: {{context}}
DEMANDE DE CODE: {{question}}

GÉNÉRATION ADAPTATIVE:
1. Utilise le langage/framework détecté
2. Code prêt pour la production
3. Inclus tous les imports nécessaires
4. Gestion d'erreurs appropriée
5. Performance optimisée

CODE GÉNÉRÉ:"""

        if LANGCHAIN_AVAILABLE and PromptTemplate:
            return PromptTemplate(template=template, input_variables=["context", "question"])
        return template
    
    def _create_test_template(self):
        """Template pour génération de tests"""
        template = f"""Tu es un EXPERT EN TESTS.

{self.project_context}

CODE À TESTER: {{context}}
DEMANDE DE TESTS: {{question}}

GÉNÉRATION DE TESTS:
1. Framework adaptatif (pytest/Jest/JUnit/etc.)
2. Couverture complète
3. Format Given-When-Then
4. Mocking intelligent
5. Cas limites inclus

TESTS GÉNÉRÉS:"""

        if LANGCHAIN_AVAILABLE and PromptTemplate:
            return PromptTemplate(template=template, input_variables=["context", "question"])
        return template
    
    def _create_refactor_template(self):
        """Template pour refactoring"""
        template = f"""Tu es un EXPERT EN REFACTORING.

{self.project_context}

CODE ACTUEL: {{context}}
DEMANDE DE REFACTORING: {{question}}

REFACTORING INTELLIGENT:
1. Applique SOLID, DRY, KISS
2. Patterns appropriés
3. Performance optimisée
4. Lisibilité améliorée
5. Compatibilité préservée

CODE REFACTORISÉ:"""

        if LANGCHAIN_AVAILABLE and PromptTemplate:
            return PromptTemplate(template=template, input_variables=["context", "question"])
        return template
    
    def get_template(self, template_type: str):
        """Obtenir un template"""
        return self.templates.get(template_type, self.templates['general'])
    
    def format_prompt(self, template_type: str, context: str, question: str) -> str:
        """Formater un prompt"""
        template = self.get_template(template_type)
        
        if LANGCHAIN_AVAILABLE and hasattr(template, 'format'):
            return template.format(context=context, question=question)
        elif isinstance(template, str):
            return template.format(context=context, question=question)
        else:
            return f"{template}\n\nContexte: {context}\nQuestion: {question}"