"""
Gestion centralisée des imports avec fallbacks
"""

# Flags de disponibilité des composants
CHROMA_AVAILABLE = False
HUGGINGFACE_AVAILABLE = False
OLLAMA_AVAILABLE = False
LANGCHAIN_AVAILABLE = False
PLOTLY_AVAILABLE = False

# LangChain Chroma
try:
    from langchain_chroma import Chroma
    CHROMA_AVAILABLE = True
except ImportError:
    try:
        from langchain.vectorstores import Chroma
        CHROMA_AVAILABLE = True
        print("⚠️ Utilisation de l'ancien import Chroma")
    except ImportError:
        Chroma = None
        print("⚠️ ChromaDB non disponible")

# HuggingFace Embeddings
try:
    from langchain_huggingface import HuggingFaceEmbeddings
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    try:
        from langchain.embeddings import HuggingFaceEmbeddings
        HUGGINGFACE_AVAILABLE = True
        print("⚠️ Utilisation de l'ancien import HuggingFaceEmbeddings")
    except ImportError:
        HuggingFaceEmbeddings = None
        print("⚠️ HuggingFaceEmbeddings non disponible")

# Ollama LLM
try:
    from langchain_ollama import OllamaLLM
    OLLAMA_AVAILABLE = True
except ImportError:
    try:
        from langchain.llms import Ollama as OllamaLLM
        OLLAMA_AVAILABLE = True
        print("⚠️ Utilisation de l'ancien import Ollama")
    except ImportError:
        OllamaLLM = None
        print("⚠️ OllamaLLM non disponible")

# LangChain Core
try:
    from langchain.chains import RetrievalQA
    from langchain.prompts import PromptTemplate
    LANGCHAIN_AVAILABLE = True
except ImportError:
    RetrievalQA = None
    PromptTemplate = None
    LANGCHAIN_AVAILABLE = False
    print("⚠️ LangChain core non disponible")

# Plotly
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    px = None
    go = None
    PLOTLY_AVAILABLE = False

def get_availability_status():
    """Retourne le statut de disponibilité des composants"""
    return {
        'chroma': CHROMA_AVAILABLE,
        'huggingface': HUGGINGFACE_AVAILABLE,
        'ollama': OLLAMA_AVAILABLE,
        'langchain': LANGCHAIN_AVAILABLE,
        'plotly': PLOTLY_AVAILABLE
    }

def print_status():
    """Affiche le statut des composants"""
    status = get_availability_status()
    print("\n🔧 ÉTAT DES COMPOSANTS:")
    for component, available in status.items():
        icon = "✅" if available else "❌"
        print(f"{icon} {component.title()}")