from sentence_transformers import SentenceTransformer

class TextEmbedder:
    def __init__(self, model_name='models/all-MiniLM-L12-v2'):
        """
        Initializes the text embedder with a specific SentenceTransformer model.
        
        Args:
            model_name (str): The name of the SentenceTransformer model to use for generating embeddings.
        """
        self.model = SentenceTransformer(model_name)

    def embed_text(self, text):
        """
        Generates an embedding for the given text.
        
        Args:
            text (str): The text to generate embedding for.
        
        Returns:
            np.array: The embedding vector for the given text.
        """
        return self.model.encode(text, convert_to_numpy=True)
    
if __name__ == "__main__":
    embedder = TextEmbedder()
    text = "The quick brown fox jumps over the lazy dog."
    embedding = embedder.embed_text(text)
    print("Embedding shape:", embedding.shape)
    print("Embedding:", embedding)