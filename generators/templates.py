"""
Templates de code fallback
"""
from typing import Dict, Optional

class CodeTemplateGenerator:
    """Générateur de templates de code basiques"""
    
    def __init__(self, project_info: Dict = None):
        self.project_info = project_info or {}
        self.language = self.project_info.get('language', 'python')
    
    def generate_class_template(self, name: str = "ExampleClass") -> str:
        """Génère un template de classe"""
        if self.language == 'python':
            return f'''```python
class {name}:
    """Description de la classe {name}"""
    
    def __init__(self, name: str):
        self.name = name
    
    def example_method(self) -> str:
        """Méthode d'exemple"""
        return f"Hello, {{self.name}}!"
    
    def __str__(self) -> str:
        return f"{name}(name={{self.name}})"
```'''
        
        elif self.language == 'javascript':
            return f'''```javascript
class {name} {{
    constructor(name) {{
        this.name = name;
    }}
    
    exampleMethod() {{
        return `Hello, ${{this.name}}!`;
    }}
    
    toString() {{
        return `{name}(name=${{this.name}})`;
    }}
}}
```'''
        
        elif self.language == 'java':
            return f'''```java
public class {name} {{
    private String name;
    
    public {name}(String name) {{
        this.name = name;
    }}
    
    public String exampleMethod() {{
        return "Hello, " + this.name + "!";
    }}
    
    @Override
    public String toString() {{
        return "{name}(name=" + name + ")";
    }}
}}
```'''
        
        else:
            return f"Template de classe pour {self.language} non disponible."
    
    def generate_function_template(self, name: str = "exampleFunction") -> str:
        """Génère un template de fonction"""
        if self.language == 'python':
            return f'''```python
def {name}(param1: str, param2: int = 0) -> str:
    """
    Description de la fonction {name}
    
    Args:
        param1: Description du paramètre 1
        param2: Description du paramètre 2
    
    Returns:
        Description du retour
    """
    if not param1:
        raise ValueError("param1 ne peut pas être vide")
    
    result = f"{{param1}} - {{param2}}"
    return result
```'''
        
        elif self.language == 'javascript':
            return f'''```javascript
/**
 * Description de la fonction {name}
 * @param {{string}} param1 - Description du paramètre 1
 * @param {{number}} param2 - Description du paramètre 2
 * @returns {{string}} Description du retour
 */
function {name}(param1, param2 = 0) {{
    if (!param1) {{
        throw new Error("param1 ne peut pas être vide");
    }}
    
    const result = `${{param1}} - ${{param2}}`;
    return result;
}}
```'''
        
        else:
            return f"Template de fonction pour {self.language} non disponible."
    
    def generate_test_template(self, class_name: str = "ExampleClass") -> str:
        """Génère un template de test"""
        test_framework = self.project_info.get('test_framework', 'pytest')
        
        if self.language == 'python' and 'pytest' in test_framework:
            return f'''```python
import pytest
from your_module import {class_name}

class Test{class_name}:
    """Tests pour {class_name}"""
    
    def test_init(self):
        """Test du constructeur"""
        obj = {class_name}("test")
        assert obj.name == "test"
    
    def test_method_success(self):
        """Test de méthode - cas de succès"""
        obj = {class_name}("test")
        result = obj.example_method()
        assert result == "Hello, test!"
    
    def test_method_edge_case(self):
        """Test de méthode - cas limite"""
        obj = {class_name}("")
        with pytest.raises(ValueError):
            obj.example_method()
    
    @pytest.fixture
    def sample_object(self):
        """Fixture pour les tests"""
        return {class_name}("sample")
```'''
        
        elif self.language == 'javascript':
            return f'''```javascript
import {{ {class_name} }} from './your_module';

describe('{class_name}', () => {{
    test('should create instance', () => {{
        const obj = new {class_name}('test');
        expect(obj.name).toBe('test');
    }});
    
    test('should return greeting', () => {{
        const obj = new {class_name}('test');
        const result = obj.exampleMethod();
        expect(result).toBe('Hello, test!');
    }});
    
    test('should handle edge cases', () => {{
        expect(() => new {class_name}('')).toThrow();
    }});
}});
```'''
        
        else:
            return f"Template de test pour {self.language} non disponible."
    
    def generate_by_type(self, code_type: str, name: str = None) -> str:
        """Génère un template selon le type"""
        generators = {
            'classe': self.generate_class_template,
            'class': self.generate_class_template,
            'fonction': self.generate_function_template,
            'function': self.generate_function_template,
            'test': self.generate_test_template
        }
        
        generator = generators.get(code_type.lower())
        if generator:
            if name:
                return generator(name)
            else:
                return generator()
        
        return f"Template {code_type} non disponible pour {self.language}"