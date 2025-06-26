"""
Interface en ligne de commande simplifiée
"""
import argparse
from core.agent import UniversalCodeAgent
from utils.imports import print_status

def main():
    """Interface CLI principale"""
    parser = argparse.ArgumentParser(description='Agent IA Universel')
    parser.add_argument('--project', '-p', help='Chemin vers le projet')
    parser.add_argument('--demo', action='store_true', help='Mode démonstration')
    args = parser.parse_args()
   
   try:
       # Initialiser l'agent
       agent = UniversalCodeAgent(args.project)
       
       print("\n" + "="*60)
       print("🤖 AGENT IA UNIVERSEL - VERSION MODULAIRE")
       print("="*60)
       
       # Afficher le statut des composants
       print_status()
       
       # Afficher le résumé du projet
       print(agent.get_project_summary())
       
       if args.demo:
           run_demo(agent)
           return
       
       # Boucle interactive
       run_interactive_mode(agent)
       
   except Exception as e:
       print(f"❌ Erreur fatale: {e}")
       print("🆘 Pour toutes les fonctionnalités, installez les dépendances complètes.")

def run_demo(agent):
   """Mode démonstration"""
   demo_questions = [
       "Génère une classe User avec validation email",
       "Crée des tests pour une fonction de calcul",
       "Explique les principes SOLID",
       "Refactorise ce code: def calc(a,b): return a+b+a*b"
   ]
   
   print("\n🎬 MODE DÉMONSTRATION:")
   for i, question in enumerate(demo_questions, 1):
       print(f"\n{i}. Question: {question}")
       query_type = agent.detect_query_type(question)
       print(f"   Type détecté: {query_type}")
       answer = agent.ask(question, query_type)
       print(f"   Réponse: {answer[:200]}...")

def run_interactive_mode(agent):
   """Mode interactif"""
   print("\n💡 EXEMPLES D'UTILISATION:")
   print("- 'Génère une classe User avec validation'")
   print("- 'Crée des tests pour cette fonction'")
   print("- 'Refactorise ce code selon SOLID'")
   print("- 'help' pour voir toutes les commandes")
   
   while True:
       try:
           question = input("\n🎯 Votre demande (ou 'quit'): ").strip()
           
           if question.lower() in ['quit', 'exit', 'q']:
               print("👋 Au revoir!")
               break
           
           if question.lower() in ['help', 'aide', '?']:
               show_help()
               continue
           
           if not question:
               continue
           
           query_type = agent.detect_query_type(question)
           print(f"🔍 Type détecté: {query_type}")
           print("💭 Traitement...")
           
           answer = agent.ask(question, query_type)
           print(f"\n🤖 Agent ({query_type}):\n{answer}")
           
       except KeyboardInterrupt:
           print("\n👋 Interruption utilisateur. Au revoir!")
           break
       except Exception as e:
           print(f"❌ Erreur: {e}")
           continue

def show_help():
   """Afficher l'aide"""
   print("""
🤖 COMMANDES DISPONIBLES:

📝 GÉNÉRATION:
- "Génère une classe User" - Crée une classe
- "Génère une fonction de calcul" - Crée une fonction
- "Génère des tests pour X" - Crée des tests

🔍 ANALYSE:
- "Analyse ce code: [code]" - Analyse la qualité
- "Explique ce code: [code]" - Explique le fonctionnement
- "Refactorise ce code: [code]" - Améliore le code

📊 PROJET:
- "Résumé du projet" - Affi