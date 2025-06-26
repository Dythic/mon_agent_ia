# 🧠 Agent IA Expert - Architecture Hexagonale

Agent IA spécialisé sur l'analyse et la génération de code pour projets Node.js avec architecture hexagonale.

## 🚀 Fonctionnalités

- 💬 Chat expert sur l'architecture
- 📊 Analyse complète du code
- 💻 Génération de code (entités, services, repositories, tests)
- 🔍 Détection de patterns et violations
- 🧪 Tests Given-When-Then automatisés

## 📁 Structure du Projet
mon-agent-ia/
├── agent.py                          # Agent de base
├── master_agent.py                   # Agent expert complet
├── expert_app.py                     # Interface Streamlit
├── indexer_manual.py                 # Indexation manuelle
├── create_enhanced_indexer.py        # Indexation avancée
├── create_training_data.py           # Génération données d'entraînement
├── build_expert_system.py            # Système expert
├── hexagonal_training_data.json      # Données d'entraînement
├── hexagonal_expert_report.json      # Rapport d'analyse
├── knowledge_graph.pkl               # Graphe de connaissances
└── architecture_graph.png            # Visualisation

## 🛠️ Installation

```bash
# Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Installer les dépendances
pip install -r requirements.txt

# Installer Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull deepseek-coder:6.7b
🚀 Utilisation
bash# 1. Indexer votre projet
python create_enhanced_indexer.py

# 2. Construire le système expert
python build_expert_system.py

# 3. Utiliser l'agent
python master_agent.py

# 4. Interface web
streamlit run expert_app.py

## 📦 Créer un `requirements.txt`

```bash
pip freeze > requirements.txt
Ou créez manuellement requirements.txt :
txtlangchain==0.1.0
langchain-chroma==0.1.0
langchain-huggingface==0.0.1
langchain-ollama==0.1.0
langchain-community==0.0.1
streamlit==1.29.0
torch>=2.0.0
transformers>=4.35.0
datasets>=2.14.0
peft>=0.6.0
chromadb>=0.4.0
sentence-transformers>=2.2.0
plotly>=5.17.0
pandas>=2.0.0
networkx>=3.2.0
matplotlib>=3.7.0
numpy>=1.24.0
🚀 Commandes Git pour push
bash# Initialiser le repo (si pas encore fait)
git init

# Créer le .gitignore
touch .gitignore
# (copiez le contenu ci-dessus)

# Ajouter tous les fichiers (sauf ceux dans .gitignore)
git add .

# Premier commit
git commit -m "🚀 Initial commit: Agent IA Expert Hexagonal

- Agent expert spécialisé architecture hexagonale
- Génération de code automatisée
- Interface Streamlit complète
- Système d'analyse et recommandations
- Tests Given-When-Then automatiques"

# Ajouter l'origine (remplacez par votre repo)
git remote add origin https://github.com/votre-username/agent-ia-hexagonal.git

# Push
git push -u origin main
💡 Conseils

Gardez : Scripts Python, rapport JSON, graphe PKL, documentation
Excluez : Base vectorielle (trop lourde), modèles fine-tunés, cache
Documentez : README.md avec instructions d'installation
Versionnez : Les données d'entraînement (utiles pour reproduire)

Votre dépôt sera propre et les autres pourront facilement reproduire votre setup ! 🎯