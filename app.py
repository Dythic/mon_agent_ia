import streamlit as st
import sys
import os

# Ajouter le répertoire courant au path Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from agent import CodeAgent
except ImportError as e:
    st.error(f"Erreur d'import: {e}")
    st.stop()

st.set_page_config(page_title="Agent IA - Mon Projet", page_icon="🤖")

@st.cache_resource
def load_agent():
    try:
        return CodeAgent()
    except Exception as e:
        st.error(f"Erreur lors du chargement de l'agent: {e}")
        return None

st.title("🤖 Agent IA spécialisé sur mon projet")

# Initialiser l'agent
if 'agent' not in st.session_state:
    with st.spinner('Chargement de l\'agent...'):
        st.session_state.agent = load_agent()

if st.session_state.agent is None:
    st.error("❌ Impossible de charger l'agent. Vérifiez que:")
    st.error("- Ollama fonctionne: `ollama serve`")
    st.error("- Un modèle est installé: `ollama pull deepseek-coder:6.7b`")
    st.error("- La base vectorielle existe: `python indexer_manual.py`")
    st.stop()

# Interface de chat
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Afficher l'historique
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input utilisateur
if prompt := st.chat_input("Posez votre question sur le projet..."):
    # Ajouter le message utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Générer la réponse
    with st.chat_message("assistant"):
        with st.spinner("Réflexion..."):
            try:
                response = st.session_state.agent.ask(prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                error_msg = f"❌ Erreur: {e}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})