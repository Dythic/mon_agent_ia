"""
Gestion des bases vectorielles
"""
import os
from typing import List, Optional, Any
from utils.imports import Chroma, HuggingFaceEmbeddings, CHROMA_AVAILABLE, HUGGINGFACE_AVAILABLE

class SimpleDocument:
    """Document simple pour le vectorstore de base"""
    def __init__(self, page_content: str, metadata: dict = None):
        self.page_content = page_content
        self.metadata = metadata or {}

class SimpleVectorStore:
    """Vectorstore simple si ChromaDB n'est pas disponible"""
    
    def __init__(self):
        self.documents = []
    
    def add_documents(self, docs: List[SimpleDocument]):
        self.documents.extend(docs)
    
    def similarity_search(self, query: str, k: int = 4) -> List[SimpleDocument]:
        """Recherche simple par mots-clés"""
        results = []
        query_words = query.lower().split()
        
        for doc in self.documents:
            content = doc.page_content.lower()
            score = sum(1 for word in query_words if word in content)
            if score > 0:
                results.append((doc, score))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in results[:k]]
    
    def as_retriever(self, search_kwargs: dict = None):
        return SimpleRetriever(self, search_kwargs or {})

class SimpleRetriever:
    """Retriever simple"""
    
    def __init__(self, vectorstore: SimpleVectorStore, search_kwargs: dict):
        self.vectorstore = vectorstore
        self.search_kwargs = search_kwargs
    
    def get_relevant_documents(self, query: str):
        k = self.search_kwargs.get('k', 4)
        return self.vectorstore.similarity_search(query, k)

class VectorStoreHandler:
    """Gestionnaire de base vectorielle"""
    
    def __init__(self):
        self.vectorstore = None
        self.embeddings = None
        self._setup_vectorstore()
    
    def _setup_vectorstore(self):
        """Configurer la base vectorielle"""
        print("📚 Configuration de la base vectorielle...")
        
        if not CHROMA_AVAILABLE or not HUGGINGFACE_AVAILABLE:
            print("⚠️ Utilisation d'un vectorstore simple")
            self.vectorstore = SimpleVectorStore()
            return
        
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'}
            )
        except Exception as e:
            print(f"⚠️ Erreur embeddings: {e}")
            self.vectorstore = SimpleVectorStore()
            return
        
        # Chercher une base existante
        db_paths = ["./universal_chroma_db", "./enhanced_chroma_db", "./chroma_db", "./vector_db"]
        db_path = self._find_existing_db(db_paths)
        
        if db_path:
            self._load_existing_db(db_path)
        else:
            print("⚠️ Aucune base vectorielle trouvée - mode simple activé")
            self.vectorstore = SimpleVectorStore()
    
    def _find_existing_db(self, paths: List[str]) -> Optional[str]:
        """Trouver une base existante"""
        for path in paths:
            if os.path.exists(path):
                return path
        return None
    
    def _load_existing_db(self, db_path: str):
        """Charger une base existante"""
        try:
            self.vectorstore = Chroma(
                persist_directory=db_path,
                embedding_function=self.embeddings
            )
            print(f"📊 Base vectorielle chargée: {db_path}")
        except Exception as e:
            print(f"⚠️ Erreur chargement base: {e}")
            self.vectorstore = SimpleVectorStore()
    
    def get_retriever(self, search_kwargs: dict = None):
        """Obtenir un retriever"""
        if search_kwargs is None:
            search_kwargs = {"k": 8}
        return self.vectorstore.as_retriever(search_kwargs=search_kwargs)
    
    def is_available(self) -> bool:
        """Vérifier si la base vectorielle est disponible"""
        return CHROMA_AVAILABLE and not isinstance(self.vectorstore, SimpleVectorStore)