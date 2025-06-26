"""
Gestion des modèles de langage
"""
import requests
import time
from typing import Optional
from utils.imports import OllamaLLM, OLLAMA_AVAILABLE

class SimpleLLM:
    """LLM simple si Ollama n'est pas disponible"""
    
    def __init__(self, model="simulation", temperature=0.2):
        self.model = model
        self.temperature = temperature
        print(f"⚠️ Mode simulation LLM activé")
    
    def invoke(self, prompt: str) -> str:
        """Simulation de réponse"""
        return f"""
🤖 **Mode Simulation**

Pour obtenir de vraies réponses IA :
1. Installez Ollama: curl -fsSL https://ollama.ai/install.sh | sh
2. Téléchargez le modèle: ollama pull deepseek-coder:6.7b
3. Démarrez Ollama: ollama serve

En attendant, des templates basiques sont disponibles.
"""

class LLMHandler:
    """Gestionnaire des modèles de langage"""
    
    def __init__(self, model="deepseek-coder:6.7b", temperature=0.2):
        self.model = model
        self.temperature = temperature
        self.llm = self._setup_llm()
    
    def _setup_llm(self):
        """Configurer le LLM"""
        if not OLLAMA_AVAILABLE:
            return SimpleLLM()
        
        try:
            self._wait_for_ollama()
            llm = OllamaLLM(
                model=self.model,
                temperature=self.temperature
            )
            print("✅ Ollama LLM configuré")
            return llm
        except Exception as e:
            print(f"⚠️ Ollama non disponible: {e}")
            return SimpleLLM()
    
    def _wait_for_ollama(self, max_retries: int = 5):
        """Attendre qu'Ollama soit disponible"""
        for i in range(max_retries):
            try:
                response = requests.get("http://localhost:11434/api/version", timeout=2)
                if response.status_code == 200:
                    return
            except:
                pass
            if i == 0:
                print("⏳ Vérification Ollama...")
            time.sleep(1)
        raise Exception("Ollama non disponible")
    
    def invoke(self, prompt: str) -> str:
        """Invoquer le LLM"""
        try:
            response = self.llm.invoke(prompt)
            if hasattr(response, 'content'):
                return response.content
            return str(response)
        except Exception as e:
            print(f"⚠️ Erreur LLM: {e}")
            return f"Erreur lors de la génération: {e}"
    
    def is_available(self) -> bool:
        """Vérifier si le LLM est disponible"""
        return OLLAMA_AVAILABLE and not isinstance(self.llm, SimpleLLM)