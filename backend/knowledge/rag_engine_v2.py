import os
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any

class OracleRAGV2:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.documents = []
        self.knowledge_path = os.path.dirname(os.path.abspath(__file__))
        
    def build_index(self, force_rebuild: bool = False):
        """Loads knowledge from JSON files and builds a FAISS index."""
        index_file = os.path.join(self.knowledge_path, "oracle_faiss.index")
        docs_file = os.path.join(self.knowledge_path, "oracle_docs.json")
        
        if not force_rebuild and os.path.exists(index_file) and os.path.exists(docs_file):
            print("[RAG 2.0] Loading existing index...")
            self.index = faiss.read_index(index_file)
            with open(docs_file, 'r', encoding='utf-8') as f:
                self.documents = json.load(f)
            return

        print("[RAG 2.0] Building new index from knowledge files...")
        chunks = []
        
        # 1. Load Heroes
        heroes_path = os.path.join(self.knowledge_path, "heroes.json")
        if os.path.exists(heroes_path):
            with open(heroes_path, 'r', encoding='utf-8') as f:
                heroes = json.load(f)
                for h_id, h in heroes.items():
                    text = f"Hero: {h['localized_name']}. Roles: {', '.join(h.get('roles', []))}. Type: {h.get('attack_type')}."
                    chunks.append({"text": text, "source": "heroes.json"})

        # 2. Load Items
        items_path = os.path.join(self.knowledge_path, "items.json")
        if os.path.exists(items_path):
            with open(items_path, 'r', encoding='utf-8') as f:
                items = json.load(f)
                for i_key, i in items.items():
                    name = i.get('dname', i_key)
                    desc = i.get('desc', '')
                    notes = i.get('notes', '')
                    text = f"Item: {name}. Description: {desc}. Notes: {notes}."
                    chunks.append({"text": text, "source": "items.json"})

        # 3. Add Meta Knowledge (from meta_737.py or similar)
        # For now, let's just add the core concepts manually or from a dedicated JSON
        # In a real scenario, we'd parse the dicts in meta_737.py
        
        if not chunks:
            print("[RAG 2.0] Warning: No knowledge found to find.")
            return

        self.documents = chunks
        texts = [doc["text"] for doc in chunks]
        embeddings = self.model.encode(texts, show_progress_bar=True)
        
        # Initialize FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(np.array(embeddings).astype('float32'))
        
        # Save
        faiss.write_index(self.index, index_file)
        with open(docs_file, 'w', encoding='utf-8') as f:
            json.dump(self.documents, f, ensure_ascii=False, indent=2)
        print(f"[RAG 2.0] Index built with {len(chunks)} documents.")

    def search(self, query: str, top_k: int = 5) -> str:
        """Performs semantic search and returns a concatenated string of results."""
        if not self.index:
            return ""
            
        query_vector = self.model.encode([query])
        distances, indices = self.index.search(np.array(query_vector).astype('float32'), top_k)
        
        results = []
        for i in indices[0]:
            if i != -1 and i < len(self.documents):
                results.append(self.documents[i]["text"])
                
        return "\n\n".join(results)

# Singleton
rag_v2 = OracleRAGV2()

if __name__ == "__main__":
    # Test building and searching
    rag_v2.build_index()
    res = rag_v2.search("How to counter high regeneration and healing?")
    print("\nSearch results for 'high regeneration':\n", res)
