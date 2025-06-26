import streamlit as st
import os
import json
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from universal_agent import UniversalCodeAgent
from code_indexer import UniversalCodeIndexer
from code_analyzer import UniversalCodeAnalyzer
from config import UniversalConfig

st.set_page_config(
    page_title="Agent IA Universel", 
    page_icon="🤖",
    layout="wide"
)

@st.cache_resource
def load_config():
    """Charger la configuration"""
    return UniversalConfig()

@st.cache_resource
def load_agent(project_path=None):
    """Charger l'agent universel"""
    try:
        return UniversalCodeAgent(project_path)
    except Exception as e:
        st.error(f"Erreur chargement agent: {e}")
        return None

def main():
    """Interface principale"""
    st.title("🤖 Agent IA Universel - Génération de Code")
    st.markdown("*Agent polyvalent pour analyser et générer du code dans n'importe quel projet*")
    
    # Sidebar pour configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Sélection du projet
        project_path = st.text_input(
            "📁 Chemin du projet",
            placeholder="/path/to/your/project",
            help="Chemin vers votre projet à analyser"
        )
        
        # Options d'indexation
        if st.button("🔍 Indexer le projet", type="primary"):
            if project_path and os.path.exists(project_path):
                index_project(project_path)
            else:
                st.error("Chemin de projet invalide")
        
        st.divider()
        
        # Informations sur l'agent
        config = load_config()
        st.subheader("📊 Langages supportés")
        for lang in config.get_supported_languages()[:10]:
            st.text(f"• {lang.title()}")
        
        if len(config.get_supported_languages()) > 10:
            st.text(f"... et {len(config.get_supported_languages()) - 10} autres")
    
    # Onglets principaux
    tabs = st.tabs([
        "💬 Chat Agent", 
        "📊 Analyse Projet", 
        "💻 Générateur Code", 
        "🧪 Générateur Tests",
        "🔧 Refactoring",
        "📈 Métriques"
    ])
    
    # Onglet Chat Agent
    with tabs[0]:
        chat_interface(project_path)
    
    # Onglet Analyse Projet  
    with tabs[1]:
        project_analysis_interface(project_path)
    
    # Onglet Générateur Code
    with tabs[2]:
        code_generator_interface(project_path)
    
    # Onglet Générateur Tests
    with tabs[3]:
        test_generator_interface(project_path)
    
    # Onglet Refactoring
    with tabs[4]:
        refactoring_interface(project_path)
    
    # Onglet Métriques
    with tabs[5]:
        metrics_interface(project_path)

def index_project(project_path: str):
    """Indexer un projet"""
    with st.spinner("🔍 Indexation en cours..."):
        try:
            indexer = UniversalCodeIndexer()
            success = indexer.index_project(project_path, force=True)
            
            if success:
                st.success("✅ Projet indexé avec succès!")
                st.rerun()
            else:
                st.error("❌ Erreur lors de l'indexation")
        except Exception as e:
            st.error(f"❌ Erreur: {e}")

def chat_interface(project_path: str):
    """Interface de chat avec l'agent"""
    st.header("💬 Chat avec l'Agent Universel")
    
    # Charger l'agent
    agent = load_agent(project_path)
    if not agent:
        st.warning("⚠️ Agent non disponible. Vérifiez qu'Ollama fonctionne.")
        return
    
    # Afficher le résumé du projet
    if project_path:
        with st.expander("📊 Résumé du projet", expanded=False):
            st.text(agent.get_project_summary())
    
    # Historique des messages
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Afficher l'historique
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Exemples de questions
    st.subheader("💡 Exemples de questions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🏗️ Analyser l'architecture"):
            example_question = "Analyse l'architecture de ce projet et donne des recommandations"
            st.session_state.example_question = example_question
    
    with col2:
        if st.button("💻 Générer du code"):
            example_question = "Génère une classe User avec validation selon les conventions du projet"
            st.session_state.example_question = example_question
    
    with col3:
        if st.button("🧪 Créer des tests"):
            example_question = "Génère des tests complets pour la classe UserService"
            st.session_state.example_question = example_question
    
    # Input utilisateur
    prompt = st.chat_input("Posez votre question à l'agent universel...")
    
    # Utiliser question d'exemple si cliquée
    if 'example_question' in st.session_state:
        prompt = st.session_state.example_question
        del st.session_state.example_question
    
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
                    
                    # Afficher le type de requête détecté
                    st.caption(f"🔍 Type détecté: {query_type}")
                    
                except Exception as e:
                    error_msg = f"❌ Erreur: {e}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

def project_analysis_interface(project_path: str):
    """Interface d'analyse de projet"""
    st.header("📊 Analyse de Projet Universelle")
    
    if not project_path or not os.path.exists(project_path):
        st.warning("⚠️ Veuillez spécifier un chemin de projet valide dans la sidebar")
        return
    
    # Bouton d'analyse
    if st.button("🔍 Analyser le projet", type="primary"):
        with st.spinner("🔍 Analyse en cours..."):
            try:
                config = load_config()
                analyzer = UniversalCodeAnalyzer(config)
                analysis = analyzer.analyze_project(project_path)
                
                # Sauvegarder l'analyse
                st.session_state.project_analysis = analysis
                
            except Exception as e:
                st.error(f"❌ Erreur analyse: {e}")
                return
    
    # Afficher l'analyse si disponible
    if 'project_analysis' in st.session_state:
        analysis = st.session_state.project_analysis
        
        # Métriques principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🗣️ Langage", analysis.get('language', 'Unknown'))
        with col2:
            st.metric("🏗️ Framework", analysis.get('framework', 'Standard'))
        with col3:
            st.metric("📊 Score Qualité", f"{analysis.get('quality_score', 0)}/10")
        with col4:
            metrics = analysis.get('metrics', {})
            st.metric("📁 Fichiers", metrics.get('total_files', 0))
        
        # Graphiques
        col1, col2 = st.columns(2)
        
        with col1:
            # Répartition des langages
            if analysis.get('language_stats'):
                fig = px.pie(
                    values=list(analysis['language_stats'].values()),
                    names=list(analysis['language_stats'].keys()),
                    title="📊 Répartition des langages"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Patterns détectés
            patterns = analysis.get('patterns', [])
            if patterns:
                fig = go.Figure(data=[
                    go.Bar(x=patterns, y=[1]*len(patterns))
                ])
                fig.update_layout(title="🔧 Patterns détectés")
                st.plotly_chart(fig, use_container_width=True)
        
        # Détails de l'analyse
        with st.expander("📋 Détails de l'analyse", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🏗️ Structure")
                structure = analysis.get('structure', {})
                st.json(structure)
                
                st.subheader("🎯 Conventions")
                conventions = analysis.get('conventions', [])
                for conv in conventions:
                    st.text(f"• {conv}")
            
            with col2:
                st.subheader("📊 Métriques")
                metrics = analysis.get('metrics', {})
                st.json(metrics)
                
                st.subheader("📦 Dépendances")
                deps = analysis.get('dependencies', {})
                st.json(deps)

def code_generator_interface(project_path: str):
    """Interface de génération de code"""
    st.header("💻 Générateur de Code Universel")
    
    agent = load_agent(project_path)
    if not agent:
        st.warning("⚠️ Agent non disponible")
        return
    
    # Types de code prédéfinis
    st.subheader("🚀 Génération Rapide")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🏗️ Architecture**")
        if st.button("📦 Nouvelle Classe", help="Génère une classe"):
            st.session_state.code_type = "classe"
        if st.button("⚙️ Nouveau Service", help="Génère un service"):
            st.session_state.code_type = "service"
    
    with col2:
        st.markdown("**🔌 Infrastructure**")
        if st.button("💾 Repository", help="Génère un repository"):
            st.session_state.code_type = "repository"
        if st.button("🌐 API Controller", help="Génère un controller"):
            st.session_state.code_type = "controller"
    
    with col3:
        st.markdown("**🛠️ Utilitaires**")
        if st.button("🔧 Fonction", help="Génère une fonction"):
            st.session_state.code_type = "fonction"
        if st.button("🛡️ Middleware", help="Génère un middleware"):
            st.session_state.code_type = "middleware"
    
    # Formulaire de spécifications
    st.subheader("📝 Spécifications du code")
    
    # Type de code
    if 'code_type' in st.session_state:
        code_type = st.session_state.code_type
        del st.session_state.code_type
    else:
        code_type = st.selectbox(
            "Type de code:",
            ["classe", "service", "repository", "controller", "fonction", "middleware", "autre"]
        )
    
    # Description
    description = st.text_area(
        f"Description du {code_type} à générer:",
        placeholder=f"Ex: {code_type} User pour gérer les utilisateurs avec validation email",
        height=100
    )
    
    # Options
    col1, col2 = st.columns(2)
    with col1:
        include_tests = st.checkbox("Inclure les tests", value=True)
        include_docs = st.checkbox("Inclure la documentation", value=True)
    
    with col2:
        follow_patterns = st.checkbox("Suivre les patterns du projet", value=True)
        add_validation = st.checkbox("Ajouter la validation", value=True)
    
    # Génération
    if st.button("🚀 Générer le Code", type="primary"):
        if description.strip():
            with st.spinner("💻 Génération en cours..."):
                try:
                    prompt = f"Génère un {code_type} : {description}"
                    
                    if include_tests:
                        prompt += " Inclus les tests complets."
                    if include_docs:
                        prompt += " Inclus la documentation."
                    if add_validation:
                        prompt += " Ajoute la validation appropriée."
                    
                    code = agent.generate_code(prompt, code_type)
                    
                    # Affichage du code
                    st.subheader("💻 Code Généré")
                    
                    # Détecter le langage pour la coloration syntaxique
                    if hasattr(agent, 'project_info') and agent.project_info:
                        lang = agent.project_info.get('language', 'text')
                    else:
                        lang = 'text'
                    
                    st.code(code, language=lang)
                    
                    # Bouton de téléchargement
                    file_extension = {
                        'python': '.py',
                        'javascript': '.js',
                        'typescript': '.ts',
                        'java': '.java',
                        'csharp': '.cs',
                        'go': '.go',
                        'rust': '.rs'
                    }.get(lang, '.txt')
                    
                    st.download_button(
                        label="💾 Télécharger",
                        data=code,
                        file_name=f"{code_type}_{description.split()[0] if description.split() else 'generated'}{file_extension}",
                        mime="text/plain"
                    )
                    
                except Exception as e:
                    st.error(f"❌ Erreur génération: {e}")
        else:
            st.warning("⚠️ Veuillez fournir une description")

def test_generator_interface(project_path: str):
    """Interface de génération de tests"""
    st.header("🧪 Générateur de Tests Universel")
    
    agent = load_agent(project_path)
    if not agent:
        st.warning("⚠️ Agent non disponible")
        return
    
    # Code à tester
    st.subheader("📝 Code à tester")
    
    input_method = st.radio(
        "Méthode d'entrée:",
        ["📋 Coller le code", "📁 Fichier du projet", "✍️ Description"]
    )
    
    code_to_test = ""
    
    if input_method == "📋 Coller le code":
        code_to_test = st.text_area(
            "Code à tester:",
            height=200,
            placeholder="Collez votre code ici..."
        )
    
    elif input_method == "📁 Fichier du projet":
        if project_path and os.path.exists(project_path):
            # Lister les fichiers du projet
            files = []
            for root, dirs, file_list in os.walk(project_path):
                dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__']]
                for file in file_list:
                    if file.endswith(('.py', '.js', '.ts', '.java', '.cs', '.go', '.rs')):
                        rel_path = os.path.relpath(os.path.join(root, file), project_path)
                        files.append(rel_path)
            
            selected_file = st.selectbox("Sélectionner un fichier:", files)
            
            if selected_file:
                file_path = os.path.join(project_path, selected_file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        code_to_test = f.read()
                    st.code(code_to_test[:500] + "..." if len(code_to_test) > 500 else code_to_test)
                except:
                    st.error("Erreur lecture fichier")
        else:
            st.warning("Projet non spécifié")
    
    else:  # Description
        code_to_test = st.text_area(
            "Description du code à tester:",
            height=100,
            placeholder="Décrivez le code pour lequel vous voulez générer des tests..."
        )
    
    # Options de test
    st.subheader("⚙️ Options de test")
    
    col1, col2 = st.columns(2)
    with col1:
        test_type = st.selectbox(
            "Type de tests:",
            ["🧪 Tests unitaires", "🔗 Tests d'intégration", "🚀 Tests complets", "⚡ Tests de performance"]
        )
        coverage_goal = st.slider("Objectif de couverture:", 80, 100, 100, 5)
    
    with col2:
        include_mocks = st.checkbox("Inclure les mocks", value=True)
        include_edge_cases = st.checkbox("Inclure les cas limites", value=True)
        given_when_then = st.checkbox("Format Given-When-Then", value=True)
    
    # Génération des tests
    if st.button("🧪 Générer les Tests", type="primary"):
        if code_to_test.strip():
            with st.spinner("🧪 Génération des tests..."):
                try:
                    prompt = f"Génère {test_type.lower()} pour ce code avec {coverage_goal}% de couverture"
                    
                    if include_mocks:
                        prompt += " Inclus les mocks appropriés."
                    if include_edge_cases:
                        prompt += " Teste tous les cas limites."
                    if given_when_then:
                        prompt += " Utilise le format Given-When-Then."
                    
                    prompt += f" Code: {code_to_test}"
                    
                    tests = agent.generate_tests(prompt)
                    
                    # Affichage des tests
                    st.subheader("🧪 Tests Générés")
                    
                    # Détecter le langage
                    if hasattr(agent, 'project_info') and agent.project_info:
                        lang = agent.project_info.get('language', 'text')
                    else:
                        lang = 'text'
                    
                    st.code(tests, language=lang)
                    
                    # Statistiques des tests
                    test_count = tests.count('test(') + tests.count('def test_') + tests.count('it(')
                    st.success(f"✅ {test_count} tests générés avec objectif {coverage_goal}% de couverture")
                    
                    # Téléchargement
                    test_extension = {
                        'python': '.test.py',
                        'javascript': '.test.js',
                        'typescript': '.test.ts',
                        'java': '.test.java'
                    }.get(lang, '.test.txt')
                    
                    st.download_button(
                        label="💾 Télécharger les tests",
                        data=tests,
                        file_name=f"tests{test_extension}",
                        mime="text/plain"
                    )
                    
                except Exception as e:
                    st.error(f"❌ Erreur génération tests: {e}")
        else:
            st.warning("⚠️ Veuillez fournir du code à tester")

def refactoring_interface(project_path: str):
    """Interface de refactoring"""
    st.header("🔧 Assistant Refactoring Universel")
    
    agent = load_agent(project_path)
    if not agent:
        st.warning("⚠️ Agent non disponible")
        return
    
    # Code à refactoriser
    st.subheader("📝 Code à refactoriser")
    
    code_input = st.text_area(
        "Code actuel:",
        height=300,
        placeholder="Collez le code à refactoriser..."
    )
    
    # Objectifs de refactoring
    st.subheader("🎯 Objectifs de refactoring")
    
    col1, col2 = st.columns(2)
    with col1:
        improvements = st.multiselect(
            "Améliorations souhaitées:",
            [
                "🏗️ Appliquer SOLID",
                "🧹 Réduire la complexité", 
                "🔄 Éliminer la duplication",
                "📚 Améliorer la lisibilité",
                "⚡ Optimiser les performances",
                "🛡️ Renforcer la sécurité",
                "🧪 Améliorer la testabilité",
                "🔧 Simplifier la maintenance"
            ]
        )
    
    with col2:
        keep_compatibility = st.checkbox("Préserver la compatibilité", value=True)
        add_comments = st.checkbox("Ajouter des commentaires", value=True)
        modernize_syntax = st.checkbox("Moderniser la syntaxe", value=True)
    
    # Analyse préliminaire
    if st.button("🔍 Analyser le code"):
        if code_input.strip():
            with st.spinner("🔍 Analyse en cours..."):
                analysis_prompt = f"Analyse ce code et identifie les problèmes de qualité: {code_input}"
                analysis = agent.ask(analysis_prompt, 'general')
                
                st.subheader("📋 Analyse du code")
                st.write(analysis)
    
    # Refactoring
    if st.button("🔧 Refactoriser", type="primary"):
        if code_input.strip():
            with st.spinner("🔧 Refactoring en cours..."):
                try:
                    prompt = f"Refactorise ce code en appliquant ces améliorations: {', '.join(improvements)}"
                    
                    if keep_compatibility:
                        prompt += " Préserve la compatibilité de l'API."
                    if add_comments:
                        prompt += " Ajoute des commentaires explicatifs."
                    if modernize_syntax:
                        prompt += " Utilise la syntaxe moderne du langage."
                    
                    refactored = agent.refactor_code(code_input, prompt)
                    
                    # Affichage côte à côte
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("📝 Code Original")
                        st.code(code_input, language='text')
                    
                    with col2:
                        st.subheader("✨ Code Refactorisé")
                        st.code(refactored, language='text')
                    
                    # Résumé des améliorations
                    st.subheader("📊 Améliorations apportées")
                    
                    # Calcul basique des métriques
                    original_lines = len(code_input.split('\n'))
                    refactored_lines = len(refactored.split('\n'))
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("📏 Lignes", refactored_lines, refactored_lines - original_lines)
                    with col2:
                        complexity_reduction = max(0, original_lines // 10 - refactored_lines // 10)
                        st.metric("🧠 Complexité", "Réduite" if complexity_reduction > 0 else "Stable")
                    with col3:
                        st.metric("🎯 Améliorations", len(improvements))
                    
                    # Téléchargement
                    st.download_button(
                        label="💾 Télécharger le code refactorisé",
                        data=refactored,
                        file_name="refactored_code.txt",
                        mime="text/plain"
                    )
                    
                except Exception as e:
                    st.error(f"❌ Erreur refactoring: {e}")
        else:
            st.warning("⚠️ Veuillez fournir du code à refactoriser")

def metrics_interface(project_path: str):
    """Interface des métriques"""
    st.header("📈 Métriques et Qualité du Code")
    
    if not project_path or not os.path.exists(project_path):
        st.warning("⚠️ Veuillez spécifier un projet dans la sidebar")
        return
    
    # Afficher les métriques si analyse disponible
    if 'project_analysis' in st.session_state:
        analysis = st.session_state.project_analysis
        metrics = analysis.get('metrics', {})
        
        # Métriques principales
        st.subheader("📊 Vue d'ensemble")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📁 Fichiers total", metrics.get('total_files', 0))
        with col2:
            st.metric("🧪 Fichiers de test", metrics.get('test_files', 0))
        with col3:
            test_coverage = metrics.get('test_coverage', 0) * 100
            st.metric("📈 Couverture tests", f"{test_coverage:.1f}%")
        with col4:
            st.metric("🧠 Complexité moy.", f"{metrics.get('avg_complexity', 0):.1f}")
        
        # Graphiques détaillés
        col1, col2 = st.columns(2)
        
        with col1:
            # Score de qualité
            quality_score = analysis.get('quality_score', 0)
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = quality_score,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Score Qualité"},
                gauge = {
                    'axis': {'range': [None, 10]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 5], 'color': "lightgray"},
                        {'range': [5, 8], 'color': "yellow"},
                        {'range': [8, 10], 'color': "green"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 8
                    }
                }
            ))
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Répartition des langages
            if analysis.get('language_stats'):
                df = pd.DataFrame(
                    list(analysis['language_stats'].items()),
                    columns=['Langage', 'Fichiers']
                )
                fig = px.bar(df, x='Langage', y='Fichiers', title="📊 Fichiers par langage")
                st.plotly_chart(fig, use_container_width=True)
        
        # Recommandations
        st.subheader("💡 Recommandations")
        
        # Génération de recommandations basées sur les métriques
        recommendations = []
        
        if test_coverage < 80:
            recommendations.append("🧪 Augmenter la couverture de tests (actuellement {:.1f}%)".format(test_coverage))
        
        if metrics.get('avg_complexity', 0) > 5:
            recommendations.append("🧠 Réduire la complexité du code (moyenne: {:.1f})".format(metrics.get('avg_complexity', 0)))
        
        if quality_score < 7:
            recommendations.append("🏗️ Améliorer la qualité générale du code")
        
        if len(analysis.get('patterns', [])) < 2:
            recommendations.append("🔧 Implémenter plus de patterns de design")
        
        for i, rec in enumerate(recommendations, 1):
            st.write(f"{i}. {rec}")
        
        if not recommendations:
            st.success("✅ Code de bonne qualité! Continuez comme ça.")
    
    else:
        st.info("ℹ️ Analysez d'abord votre projet dans l'onglet 'Analyse Projet'")

if __name__ == "__main__":
    main()