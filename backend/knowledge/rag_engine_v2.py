import os
import json
import re
from typing import List, Dict, Any

class OracleRAGLite:
    """
    A lightweight version of the RAG engine that uses keyword matching instead of 
    heavy neural embeddings to save memory on Render (512MB limit).
    """
    def __init__(self):
        self.documents = []
        self.knowledge_path = os.path.dirname(os.path.abspath(__file__))
        
    def build_index(self, force_rebuild: bool = False):
        """Loads knowledge from JSON files into memory."""
        print("[RAG LITE] Loading knowledge files...")
        chunks = []
        
        # 1. Load Heroes
        heroes_path = os.path.join(self.knowledge_path, "heroes.json")
        if os.path.exists(heroes_path):
            with open(heroes_path, 'r', encoding='utf-8') as f:
                heroes = json.load(f)
                for h_id, h in heroes.items():
                    text = f"Hero: {h['localized_name']}. Roles: {', '.join(h.get('roles', []))}. Type: {h.get('attack_type')}."
                    chunks.append({"text": text, "keywords": h['localized_name'].lower().split()})

        # 2. Load Items
        items_path = os.path.join(self.knowledge_path, "items.json")
        if os.path.exists(items_path):
            with open(items_path, 'r', encoding='utf-8') as f:
                items = json.load(f)
                for i_key, i in items.items():
                    name = i.get('dname', i_key)
                    desc = i.get('desc', '')
                    text = f"Item: {name}. Description: {desc}."
                    chunks.append({"text": text, "keywords": name.lower().split()})

        self.documents = chunks
        print(f"[RAG LITE] Loaded {len(chunks)} documents into memory.")

    def search(self, query: str, top_k: int = 3) -> str:
        """Search using a simple keyword overlap scoring."""
        if not self.documents:
            self.build_index()
            
        query_words = set(re.findall(r'\w+', query.lower()))
        if not query_words:
            return ""

        scored_docs = []
        for doc in self.documents:
            # Score based on how many query words appear in the document text
            doc_text_lower = doc['text'].lower()
            score = sum(1 for word in query_words if word in doc_text_lower)
            if score > 0:
                scored_docs.append((score, doc['text']))

        # Sort by score descending
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        
        results = [text for score, text in scored_docs[:top_k]]
        return "\n\n".join(results)

# Singleton for compatibility
rag_v2 = OracleRAGLite()

if __name__ == "__main__":
    rag_v2.build_index()
    res = rag_v2.search("How to counter Phantom Lancer with items?")
    print("\nSearch results:\n", res)
