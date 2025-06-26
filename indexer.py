import os
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
import torch
print(f"🔥 CUDA disponible: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"🎯 GPU: {torch.cuda.get_device_name(0)}")
    print(f"💾 VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")

def load_files_manually(project_path):
    """Charge les fichiers manuellement"""
    documents = []
    extensions = ['.js', '.ts', '.jsx', '.tsx', '.json', '.md', '.yml', '.yaml']
    excluded_dirs = ['node_modules', '.git', 'dist', 'build', 'coverage', '.next']
    
    print(f"🔍 Recherche manuelle dans : {project_path}")
    
    for root, dirs, files in os.walk(project_path):
        # Filtrer les dossiers exclus
        dirs[:] = [d for d in dirs if d not in excluded_dirs]
        
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if content.strip():  # Ignorer les fichiers vides
                            doc = Document(
                                page_content=content,
                                metadata={
                                    'source': file_path,
                                    'filename': file,
                                    'extension': Path(file).suffix
                                }
                            )
                            documents.append(doc)
                            print(f"✅ {file_path}")
                except Exception as e:
                    print(f"⚠️  Erreur avec {file_path}: {e}")
    
    return documents

def index_codebase_manual(project_path, db_path="./chroma_db"):
    if not os.path.exists(project_path):
        print(f"❌ Le dossier {project_path} n'existe pas !")
        return None
    
    # Charger les fichiers manuellement
    documents = load_files_manually(project_path)
    print(f"\n📄 Total: {len(documents)} fichiers chargés")
    
    if len(documents) == 0:
        print("❌ Aucun fichier valide trouvé !")
        return None
    
    # Découper les documents
    print("✂️  Découpage en chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    
    splits = text_splitter.split_documents(documents)
    print(f"📦 {len(splits)} chunks créés")
    
    if len(splits) == 0:
        print("❌ Aucun chunk créé !")
        return None
    
    # Créer les embeddings
    print("🧠 Création des embeddings...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cuda'}  # Force GPU
    )
    
    # Créer la base vectorielle
    print("💾 Création de la base vectorielle...")
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory=db_path
    )
    
    print(f"🎉 Indexation terminée ! Base créée dans {db_path}")
    return vectorstore

if __name__ == "__main__":
    project_path = "/home/dythic/projet/hexagonal-nodejs-example"
    vectorstore = index_codebase_manual(project_path)
    
    if vectorstore:
        print("✅ Succès ! Vous pouvez maintenant utiliser l'agent.")
        
        # Test rapide
        print("\n🧪 Test de la base vectorielle...")
        retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
        docs = retriever.invoke("UserService")
        print(f"Test recherche 'UserService': {len(docs)} résultats trouvés")
    else:
        print("❌ Échec de l'indexation.")