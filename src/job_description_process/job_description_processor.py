import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.config import Config
from data_io.read_txt import ReadTXT 
from models.chatgpt_client import ChatGPTClient
from vector_storage.vector_store import VectorStore 

prompt_text = ReadTXT.read_file("src/prompt/template/keywords_template.txt")
output_format = ReadTXT.read_file("src/prompt/format/output_format.txt")

class JobDescriptionProcessor:
    def __init__(self, api_key, folder_path, vector_store):
        """
        Initializes the JobDescriptionProcessor with an API key, folder path for job descriptions, and a vector store for embeddings.

        Args:
            api_key (str): The API key for OpenAI.
            folder_path (str): The path to the folder containing job description text files.
            vector_store (VectorStore): An instance of VectorStore for storing and querying embeddings.
        """
        self.client = ChatGPTClient(api_key)
        self.folder_path = folder_path
        self.vector_store = vector_store  # Use the provided vector store directly

    def process_files(self):
        """
        Processes each text file in the specified folder, extracts keywords embeddings for job descriptions, and stores them in the vector store.
        """
        for filename in os.listdir(self.folder_path):
            if filename.endswith('.txt'):
                file_path = os.path.join(self.folder_path, filename)
                text_content = ReadTXT.read_file(file_path)
                text_keywords = self.client.query(prompt_text, text_content, output_format)
                self.vector_store.add(text_keywords, text_content)
        print("*" * 100)
        print(self.vector_store.id_to_keyword)
        print("*" * 100)
        print(self.vector_store.id_to_text)

    def search_descriptions(self, query_keywords, k=3):
        """
        Searches for job descriptions that are most similar to the query keywords.
        
        Args:
            query_keywords (list of str): A list of query keywords.
            k (int): The number of top results to return.
            
        Returns:
            list: The top k most similar job descriptions to the query keywords.
        """
        # Search using the query keywords directly
        results = self.vector_store.search(query_keywords, k)
        return results


if __name__ == "__main__":
    api_key = Config.API_KEY 
    folder_path = "src/data/job_description"
    dimension = 384
    model_name = "src/models/all-MiniLM-L12-v2"

    vector_store = VectorStore(dimension, model_name) 
    processor = JobDescriptionProcessor(api_key, folder_path, vector_store)

    # Process files and add them to the vector store
    processor.process_files()

    query_keywords = ["C++", "AI", "Machine Learning"]
    results = processor.search_descriptions(query_keywords, k=2)

    # Print results
    print("Top 2 most similar job descriptions to the query keywords:")
    for text, score in results:
        print(f"Texts: {text}, Score: {score}")
        print("*" * 100)