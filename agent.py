from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import requests
import time
import torch

class CodeAgent:
    def __init__(self, db_path="./chroma_db", model_name="deepseek-coder:6.7b"):
        print("🤖 Initialisation de l'agent...")
        
        # Vérifier CUDA
        if torch.cuda.is_available():
            print(f"🔥 GPU détecté: {torch.cuda.get_device_name(0)}")
        
        # Vérifier qu'Ollama fonctionne
        self._wait_for_ollama()
        
        # Charger la base vectorielle
        print("📚 Chargement de la base vectorielle...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}  # CPU pour économiser VRAM
        )
        
        self.vectorstore = Chroma(
            persist_directory=db_path,
            embedding_function=self.embeddings
        )
        
        # Vérifier que la base contient des données
        collection = self.vectorstore._collection
        count = collection.count()
        print(f"📊 Base vectorielle chargée: {count} documents")
        
        if count == 0:
            raise Exception("❌ La base vectorielle est vide ! Lancez d'abord l'indexation.")
        
        # Initialiser le modèle Ollama
        print("🦙 Connexion à Ollama...")
        self.llm = OllamaLLM(model=model_name, temperature=0.1)
        
        # Template de prompt spécialisé pour l'architecture hexagonale
        template = """Tu es un assistant IA expert en architecture hexagonale et Node.js, spécialisé sur ce projet.

Contexte du projet (architecture hexagonale Node.js):
{context}

Question: {question}

Instructions:
- Utilise le contexte fourni pour donner une réponse précise et technique
- Si tu parles de code, mentionne les fichiers spécifiques
- Explique les concepts d'architecture hexagonale si nécessaire
- Donne des exemples concrets du code du projet

Réponse détaillée:"""
        
        self.prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
        
        # Créer la chaîne RAG
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 5}),
            chain_type_kwargs={"prompt": self.prompt}
        )
        
        print("✅ Agent prêt !")
    
    def _wait_for_ollama(self, max_retries=30):
        print("⏳ Vérification d'Ollama...")
        for i in range(max_retries):
            try:
                response = requests.get("http://localhost:11434/api/version", timeout=2)
                if response.status_code == 200:
                    print("✅ Ollama connecté")
                    return
            except:
                pass
            
            if i == 0:
                print("⏳ Attente de la connexion à Ollama...")
            time.sleep(1)
        
        raise Exception("❌ Impossible de se connecter à Ollama. Lancez 'ollama serve' d'abord.")
    
    def ask(self, question):
        """Poser une question à l'agent"""
        try:
            response = self.qa_chain.invoke({"query": question})
            return response["result"]
        except Exception as e:
            return f"❌ Erreur: {e}"
    
    def search_relevant_files(self, query):
        """Rechercher les fichiers les plus pertinents"""
        docs = self.vectorstore.similarity_search(query, k=5)
        files = []
        for doc in docs:
            source = doc.metadata.get('source', 'Unknown')
            files.append({
                'file': source.split('/')[-1],
                'path': source,
                'content_preview': doc.page_content[:200] + "..."
            })
        return files

if __name__ == "__main__":
    try:
        agent = CodeAgent()
        
        print("\n" + "="*50)
        print("🤖 Agent IA - Architecture Hexagonale Node.js")
        print("="*50)
        
        while True:
            question = input("\n💬 Votre question (ou 'quit' pour quitter): ")
            if question.lower() in ['quit', 'exit', 'q']:
                break
            
            print("\n🔍 Recherche et analyse...")
            answer = agent.ask(question)
            print(f"\n🤖 Réponse:\n{answer}")
            
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation: {e}")