import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import faiss
from embedder.text_embedder import TextEmbedder

class VectorStore:
    def __init__(self, dimension, model_name):
        """
        Initializes the vector store with a specific dimension for the vectors and a model for keywords embedding.
        
        Args:
            dimension (int): The dimension of the vectors to be stored.
            model_name (str): The name of the SentenceTransformer model to use for generating embeddings.
        """
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)  # L2 distance for similarity measure
        self.embedder = TextEmbedder(model_name)  # Initialize the text embedder
        self.id_to_keyword = {}  # Maps index ID to keyword
        self.id_to_text = {}  # Maps index ID to original text
        self.current_id = 0  # Current index ID

        # print("Embedding dimension:", self.embedder.model.get_sentence_embedding_dimension())

    def add(self, keywords, text):
        """
        Generates embedding vectors for a list of keywords and stores them, while recording their mapping to the original text.
        
        Args:
            keywords (list of str): A list containing multiple pieces of keyword.
            text (str): The original text mapping with keywords.
        """
        for keyword in keywords:
            embedding = self.embedder.embed_text(keyword).reshape(1, -1)
            self.index.add(embedding)  # Add embedding vector to FAISS index
            self.id_to_keyword[self.current_id] = keyword
            self.id_to_text[self.current_id] = text
            self.current_id += 1

    def search(self, query_keywords, k=3):
        """
        Searches for the original text most similar to a list of query keywords and returns the top k matching texts ranked by relevance.
        
        Args:
            query_keywords (list of str): A list of query keywords.
            k (int): The number of top matching results to return.
            
        Returns:
            list: The top k matching original texts ranked by relevance.
        """
        query_embeddings = np.array([self.embedder.embed_text(keyword) for keyword in query_keywords])
        D, I = self.index.search(query_embeddings, k)
        texts_scores = {}
        for idx_list in I:
            for idx in idx_list:
                original_text = self.id_to_text[idx]
                texts_scores[original_text] = texts_scores.get(original_text, 0) + 1
        sorted_texts_scores = sorted(texts_scores.items(), key=lambda x: x[1], reverse=True)
        top_k_results = sorted_texts_scores[:k]
        return top_k_results

if __name__ == "__main__":
    dimension = 384  
    model_name ='src/models/all-MiniLM-L12-v2'
    store = VectorStore(dimension=dimension, model_name=model_name)
    
    # Adding some keywords to the store
    keywords_list = [
        ["The quick brown fox", "jumps over", "the lazy dog"],
        ["Lorem ipsum dolor sit amet", "consectetur adipiscing elit", "sed do eiusmod tempor"],
        ["To be or not to be", "that is the question"],
        ["Elementary, my dear Watson", "The game is afoot"]
    ]

    texts_list = [
        "doc_1",
        "doc_2",
        "doc_3",
        "doc_4"
    ]
    for keywords, texts in zip(keywords_list, texts_list):
        store.add(keywords, texts)
    
    # Querying the store with a list of keywords
    query_keywords = ["quick fox", "lazy dog", "consectetur elit"]
    top_k_results = store.search(query_keywords, k=2)
    
    print("Top matching texts:")
    for text, score in top_k_results:
        print(f"Texts: {text}, Score: {score}")
