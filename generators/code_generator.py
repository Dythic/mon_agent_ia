"""
Générateur de code avancé
"""
from typing import Dict, List, Optional, Any
from core.llm_handler import LLMHandler
from generators.templates import CodeTemplateGenerator
from config.settings import get_settings

class CodeGenerator:
    """Générateur de code intelligent"""
    
    def __init__(self, project_info: Dict[str, Any] = None):
        self.project_info = project_info or {}
        self.settings = get_settings()
        self.llm_handler = LLMHandler()
        self.template_generator = CodeTemplateGenerator(project_info)
        
        # Détection du langage et framework
        self.language = self.project_info.get('language', 'python')
        self.framework = self.project_info.get('framework', 'standard')
    
    def generate_class(self, 
                      name: str, 
                      description: str = "", 
                      attributes: List[str] = None,
                      methods: List[str] = None,
                      inheritance: str = None,
                      interfaces: List[str] = None) -> str:
        """Générer une classe complète"""
        
        if not self.llm_handler.is_available():
            return self.template_generator.generate_class_template(name)
        
        prompt = self._build_class_prompt(name, description, attributes, methods, inheritance, interfaces)
        return self.llm_handler.invoke(prompt)
    
    def generate_function(self,
                         name: str,
                         description: str = "",
                         parameters: List[Dict[str, str]] = None,
                         return_type: str = None,
                         is_async: bool = False) -> str:
        """Générer une fonction complète"""
        
        if not self.llm_handler.is_available():
            return self.template_generator.generate_function_template(name)
        
        prompt = self._build_function_prompt(name, description, parameters, return_type, is_async)
        return self.llm_handler.invoke(prompt)
    
    def generate_service(self,
                        name: str,
                        description: str = "",
                        operations: List[str] = None) -> str:
        """Générer une classe de service"""
        
        service_prompt = f"""
Génère une classe de service {name} en {self.language} pour le framework {self.framework}.

Description: {description}

Opérations requises: {', '.join(operations or [])}

Requirements:
- Injection de dépendances si applicable
- Gestion d'erreurs appropriée
- Logging si pertinent
- Documentation complète
- Tests unitaires si demandé

Adapte-toi aux conventions du framework {self.framework}.
"""
        
        if self.llm_handler.is_available():
            return self.llm_handler.invoke(service_prompt)
        else:
            return self._generate_service_template(name, description, operations)
    
    def generate_controller(self,
                          name: str,
                          resource: str = "",
                          endpoints: List[str] = None) -> str:
        """Générer un contrôleur/handler"""
        
        controller_prompt = f"""
Génère un contrôleur {name} en {self.language} pour le framework {self.framework}.

Ressource: {resource}
Endpoints: {', '.join(endpoints or ['GET', 'POST', 'PUT', 'DELETE'])}

Requirements:
- Validation des entrées
- Gestion d'erreurs HTTP appropriée
- Serialization/désérialisation
- Documentation API
- Middleware si applicable

Adapte-toi aux conventions du framework {self.framework}.
"""
        
        if self.llm_handler.is_available():
            return self.llm_handler.invoke(controller_prompt)
        else:
            return self._generate_controller_template(name, resource, endpoints)
    
    def generate_repository(self,
                          name: str,
                          entity: str = "",
                          operations: List[str] = None) -> str:
        """Générer un repository/DAO"""
        
        repository_prompt = f"""
Génère un repository {name} en {self.language}.

Entité: {entity}
Opérations: {', '.join(operations or ['create', 'read', 'update', 'delete', 'list'])}

Requirements:
- Pattern Repository
- Abstraction de la base de données
- Gestion d'erreurs
- Transactions si applicable
- Interface et implémentation

Adapte-toi aux conventions du projet.
"""
        
        if self.llm_handler.is_available():
            return self.llm_handler.invoke(repository_prompt)
        else:
            return self._generate_repository_template(name, entity, operations)
    
    def generate_model(self,
                      name: str,
                      fields: List[Dict[str, str]] = None,
                      validations: List[str] = None) -> str:
        """Générer un modèle/entité"""
        
        model_prompt = f"""
Génère un modèle {name} en {self.language}.

Champs: {fields or []}
Validations: {', '.join(validations or [])}

Requirements:
- Encapsulation appropriée
- Validation des données
- Sérialisation si nécessaire
- Méthodes utilitaires
- Documentation

Adapte-toi aux conventions du projet.
"""
        
        if self.llm_handler.is_available():
            return self.llm_handler.invoke(model_prompt)
        else:
            return self._generate_model_template(name, fields, validations)
    
    def _build_class_prompt(self, name: str, description: str, attributes: List[str] = None,
                           methods: List[str] = None, inheritance: str = None,
                           interfaces: List[str] = None) -> str:
        """Construire le prompt pour une classe"""
        
        prompt = f"""
Génère une classe {name} complète en {self.language}.

Description: {description}

Spécifications:
- Langage: {self.language}
- Framework: {self.framework}
"""
        
        if attributes:
            prompt += f"- Attributs: {', '.join(attributes)}\n"
        
        if methods:
            prompt += f"- Méthodes: {', '.join(methods)}\n"
        
        if inheritance:
            prompt += f"- Hérite de: {inheritance}\n"
        
        if interfaces:
            prompt += f"- Implémente: {', '.join(interfaces)}\n"
        
        prompt += f"""
Requirements:
- Code complet et fonctionnel
- Documentation appropriée
- Gestion d'erreurs
- Encapsulation
- Validation des données
- Tests unitaires de base

Adapte-toi aux conventions du {self.language} et du framework {self.framework}.
"""
        
        return prompt
    
    def _build_function_prompt(self, name: str, description: str, 
                              parameters: List[Dict[str, str]] = None,
                              return_type: str = None, is_async: bool = False) -> str:
        """Construire le prompt pour une fonction"""
        
        prompt = f"""
Génère une fonction {name} complète en {self.language}.

Description: {description}

Spécifications:
- Langage: {self.language}
- Asynchrone: {is_async}
"""
        
        if parameters:
            param_str = ", ".join([f"{p.get('name', '')}: {p.get('type', 'Any')}" for p in parameters])
            prompt += f"- Paramètres: {param_str}\n"
        
        if return_type:
            prompt += f"- Type de retour: {return_type}\n"
        
        prompt += f"""
Requirements:
- Documentation complète
- Validation des paramètres
- Gestion d'erreurs appropriée
- Optimisation si nécessaire
- Tests unitaires

Adapte-toi aux conventions du {self.language}.
"""
        
        return prompt
    
    def _generate_service_template(self, name: str, description: str, operations: List[str] = None) -> str:
        """Template de service de base"""
        if self.language == 'python':
            return f'''```python
class {name}:
    """Service {description}"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def execute_operation(self, data):
        """Opération principale"""
        try:
            # Logique métier ici
            self.logger.info(f"Executing operation with data: {{data}}")
            return {{"status": "success", "data": data}}
        except Exception as e:
            self.logger.error(f"Error in operation: {{e}}")
            raise
    
    def validate_data(self, data):
        """Validation des données"""
        if not data:
            raise ValueError("Data cannot be empty")
        return True
```'''
        else:
            return f"Template de service pour {self.language} non disponible."
    
    def _generate_controller_template(self, name: str, resource: str, endpoints: List[str] = None) -> str:
        """Template de contrôleur de base"""
        if self.language == 'python' and self.framework == 'flask':
            return f'''```python
from flask import Blueprint, request, jsonify

{name.lower()}_bp = Blueprint('{name.lower()}', __name__)

@{name.lower()}_bp.route('/{resource}', methods=['GET'])
def get_{resource}():
    """Récupérer {resource}"""
    try:
        # Logique de récupération
        return jsonify({{"status": "success", "data": []}})
    except Exception as e:
        return jsonify({{"error": str(e)}}), 500

@{name.lower()}_bp.route('/{resource}', methods=['POST'])
def create_{resource}():
    """Créer {resource}"""
    try:
        data = request.get_json()
        # Logique de création
        return jsonify({{"status": "created", "data": data}}), 201
    except Exception as e:
        return jsonify({{"error": str(e)}}), 400
```'''
        else:
            return f"Template de contrôleur pour {self.language}/{self.framework} non disponible."
    
    def _generate_repository_template(self, name: str, entity: str, operations: List[str] = None) -> str:
        """Template de repository de base"""
        if self.language == 'python':
            return f'''```python
from abc import ABC, abstractmethod
from typing import List, Optional

class {name}Interface(ABC):
    """Interface du repository {name}"""
    
    @abstractmethod
    def create(self, entity: {entity}) -> {entity}:
        pass
    
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[{entity}]:
        pass
    
    @abstractmethod
    def get_all(self) -> List[{entity}]:
        pass
    
    @abstractmethod
    def update(self, entity: {entity}) -> {entity}:
        pass
    
    @abstractmethod
    def delete(self, id: int) -> bool:
        pass

class {name}({name}Interface):
    """Implémentation du repository {name}"""
    
    def __init__(self, db_session):
        self.db = db_session
    
    def create(self, entity: {entity}) -> {entity}:
        """Créer une entité"""
        try:
            self.db.add(entity)
            self.db.commit()
            return entity
        except Exception as e:
            self.db.rollback()
            raise
    
    def get_by_id(self, id: int) -> Optional[{entity}]:
        """Récupérer par ID"""
        return self.db.query({entity}).filter({entity}.id == id).first()
    
    def get_all(self) -> List[{entity}]:
        """Récupérer toutes les entités"""
        return self.db.query({entity}).all()
    
    def update(self, entity: {entity}) -> {entity}:
        """Mettre à jour une entité"""
        try:
            self.db.merge(entity)
            self.db.commit()
            return entity
        except Exception as e:
            self.db.rollback()
            raise
    
    def delete(self, id: int) -> bool:
        """Supprimer une entité"""
        try:
            entity = self.get_by_id(id)
            if entity:
                self.db.delete(entity)
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            raise
```'''
        else:
            return f"Template de repository pour {self.language} non disponible."
    
    def _generate_model_template(self, name: str, fields: List[Dict[str, str]] = None, validations: List[str] = None) -> str:
        """Template de modèle de base"""
        if self.language == 'python':
            return f'''```python
from dataclasses import dataclass
from typing import Optional
import datetime

@dataclass
class {name}:
    """Modèle {name}"""
    
    id: Optional[int] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    
    def __post_init__(self):
        """Validation post-initialisation"""
        if self.created_at is None:
            self.created_at = datetime.datetime.now()
        
        self.validate()
    
    def validate(self):
        """Validation des données"""
        # Ajouter les validations spécifiques
        pass
    
    def to_dict(self) -> dict:
        """Conversion en dictionnaire"""
        return {{
            'id': self.id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }}
    
    @classmethod
    def from_dict(cls, data: dict) -> '{name}':
        """Création depuis un dictionnaire"""
        return cls(**data)
```'''
        else:
            return f"Template de modèle pour {self.language} non disponible."
    
    def generate_custom(self, prompt: str, code_type: str = "general") -> str:
        """Génération personnalisée avec prompt libre"""
        
        enhanced_prompt = f"""
Contexte du projet:
- Langage: {self.language}
- Framework: {self.framework}
- Type de code: {code_type}

Demande: {prompt}

Requirements:
- Code complet et fonctionnel
- Adapté au langage et framework
- Bonnes pratiques respectées
- Documentation appropriée

Code généré:
"""
        
        if self.llm_handler.is_available():
            return self.llm_handler.invoke(enhanced_prompt)
        else:
            return f"Génération personnalisée non disponible sans LLM. Prompt: {prompt}"