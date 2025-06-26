"""
Interface Streamlit simplifiée
"""
import streamlit as st
import os
from core.agent import UniversalCodeAgent
from utils.imports import get_availability_status, PLOTLY_AVAILABLE

st.set_page_config(
    page_title="Agent IA Universel", 
    page_icon="🤖",
    layout="wide"
)

@st.cache_resource
def load_agent(project_path=None):
    """Charger l'agent"""
    try:
        return UniversalCodeAgent(project_path)
    except Exception as e:
        st.error(f"Erreur chargement agent: {e}")
        return None

def main():
    """Interface principale simplifiée"""
    st.title("🤖 Agent IA Universel - Version Modulaire")
    st.markdown("*Agent simplifié et modulaire pour génération de code*")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        project_path = st.text_input(
            "📁 Chemin du projet",
            placeholder="/path/to/your/project"
        )
        
        # État des composants
        st.subheader("🔧 État des composants")
        status = get_availability_status()
        for component, available in status.items():
            icon = "✅" if available else "❌"
            st.text(f"{icon} {component.title()}")
    
    # Onglets simplifiés
    tab1, tab2, tab3 = st.tabs(["💬 Chat", "💻 Générateur", "📊 Projet"])
    
    with tab1:
        chat_interface(project_path)
    
    with tab2:
        generator_interface(project_path)
    
    with tab3:
        project_interface(project_path)

def chat_interface(project_path: str):
    """Interface de chat simplifiée"""
    st.header("💬 Chat avec l'Agent")
    
    agent = load_agent(project_path)
    if not agent:
        st.warning("⚠️ Agent non disponible")
        return
    
    # Historique des messages
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Afficher l'historique
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Input utilisateur
    prompt = st.chat_input("Posez votre question...")
    
    if prompt:
        # Ajouter message utilisateur
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Générer réponse
        with st.chat_message("assistant"):
            with st.spinner("💭 Réflexion..."):
                try:
                    query_type = agent.detect_query_type(prompt)
                    response = agent.ask(prompt, query_type)
                    
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.caption(f"🔍 Type: {query_type}")
                    
                except Exception as e:
                    error_msg = f"❌ Erreur: {e}"
                    st.error(error_msg)

def generator_interface(project_path: str):
    """Interface de génération simplifiée"""
    st.header("💻 Générateur de Code")
    
    agent = load_agent(project_path)
    if not agent:
        st.warning("⚠️ Mode templates basiques activé")
        basic_generator_interface(project_path)
        return
    
    # Sélection du type
    code_type = st.selectbox(
        "Type de code:",
        ["classe", "fonction", "test", "service", "controller"]
    )
    
    # Description
    description = st.text_area(
        "Description:",
        placeholder=f"Décrivez le {code_type} à générer..."
    )
    
    # Génération
    if st.button("🚀 Générer", type="primary"):
        if description:
            with st.spinner("💻 Génération..."):
                try:
                    code = agent.generate_code(description, code_type)
                    st.subheader("💻 Code Généré")
                    st.code(code, language='text')
                    
                    # Téléchargement
                    st.download_button(
                        "💾 Télécharger",
                        data=code,
                        file_name=f"{code_type}.txt",
                        mime="text/plain"
                    )
                except Exception as e:
                    st.error(f"❌ Erreur: {e}")
        else:
            st.warning("⚠️ Veuillez fournir une description")

def basic_generator_interface(project_path: str):
    """Interface de génération basique sans IA"""
    from generators.templates import CodeTemplateGenerator
    
    # Détecter le langage du projet
    language = "python"  # Par défaut
    if project_path and os.path.exists(project_path):
        for root, dirs, files in os.walk(project_path):
            for file in files[:5]:  # Échantillon
                if file.endswith('.js'):
                    language = "javascript"
                    break
                elif file.endswith('.java'):
                    language = "java"
                    break
    
    project_info = {'language': language}
    generator = CodeTemplateGenerator(project_info)
    
    code_type = st.selectbox("Type:", ["classe", "fonction", "test"])
    name = st.text_input("Nom:", value="Example")
    
    if st.button("🚀 Générer Template"):
        template = generator.generate_by_type(code_type, name)
        st.code(template, language=language)

def project_interface(project_path: str):
    """Interface de projet simplifiée"""
    st.header("📊 Informations Projet")
    
    if not project_path or not os.path.exists(project_path):
        st.warning("⚠️ Spécifiez un chemin de projet valide")
        return
    
    agent = load_agent(project_path)
    if agent:
        st.text(agent.get_project_summary())
    else:
        st.info("Analyse basique du projet...")
        show_basic_project_info(project_path)

def show_basic_project_info(project_path: str):
    """Affichage basique des infos projet"""
    from analyzers.project_analyzer import ProjectAnalyzer
    
    analyzer = ProjectAnalyzer()
    info = analyzer.analyze_project(project_path)
    
    if info:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Langage", info.get('language', 'Unknown'))
        with col2:
            st.metric("Framework", info.get('framework', 'Standard'))
        with col3:
            metrics = info.get('metrics', {})
            st.metric("Fichiers", metrics.get('total_files', 0))

if __name__ == "__main__":
    main()