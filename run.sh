#!/bin/bash
echo "🤖 Installation Agent IA Universel"

# Vérifications préalables
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 requis. Installez Python 3.9+"
    exit 1
fi

# Environnement virtuel
if [ ! -d "venv" ]; then
    echo "📦 Création environnement virtuel..."
    python3 -m venv venv
fi

echo "🔄 Activation environnement..."
source venv/bin/activate

echo "⬆️ Mise à jour pip..."
pip install --upgrade pip

echo "📚 Installation LangChain..."
pip install langchain==0.1.0
pip install langchain-chroma==0.1.4  
pip install langchain-huggingface==0.0.3
pip install langchain-ollama==0.1.3
pip install langchain-community==0.0.38

echo "🧠 Installation ChromaDB et embeddings..."
pip install chromadb==0.4.24
pip install sentence-transformers==2.2.2

echo "🌐 Installation interface..."
pip install streamlit==1.29.0
pip install plotly==5.17.0
pip install pandas==2.0.3

echo "🔧 Installation utilitaires..."
pip install pyyaml==6.0.1
pip install requests==2.31.0
pip install numpy==1.24.4

echo "🤖 Installation PyTorch (CPU)..."
pip install torch==2.0.1 --index-url https://download.pytorch.org/whl/cpu

echo "🦙 Vérification Ollama..."
if ! command -v ollama &> /dev/null; then
    echo "📥 Installation Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
fi

echo "🧠 Téléchargement modèle..."
ollama pull deepseek-coder:6.7b

echo "✅ Installation terminée!"
echo "🚀 Testez avec: python universal_agent.py --project /path/to/project"