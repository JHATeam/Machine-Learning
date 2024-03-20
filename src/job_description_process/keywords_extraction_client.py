import sys
sys.path.append('src')

from models.chatgpt_client import ChatGPTClient
from data_io.read_txt import ReadTXT

class KeywordsExtractionClient:
    def __init__(self, api_key):
        """
        Initializes the Keywords Extraction client.
        """
        self.chat_client = ChatGPTClient(api_key)

    def extract_keywords(self, text):
        """
        Extracts keywords from the provided text using the ChatGPTClient.
        """
        prompt = f"Please extract keywords from the following text:\n{text}"
        response = self.chat_client.query(prompt)
        return response

if __name__ == "__main__":
    api_key = 'your openai key'
    keywords_client = KeywordsExtractionClient(api_key=api_key)

    keywords_template = ReadTXT.read_file("src/prompt/template/keywords_template.txt")
    target_words = "these are the target words in list: salary, working location, working remote or not"
    job_description = ReadTXT.read_file("src/data/job_description/job_description.txt")

    prompt = "\n".join([keywords_template, target_words, job_description])
    print(prompt)
    
    keywords = keywords_client.extract_keywords(prompt)
    print("Extracted Keywords:", keywords)
