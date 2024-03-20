import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import openai

from config.config import Config
from data_io.read_txt import ReadTXT

class ChatGPTClient:
    def __init__(self, api_key):
        """
        Initializes the ChatGPT client with the provided API key.

        Args:
            openai.api_key (str): The API key for authenticating with the OpenAI API.
        """
        openai.api_key = api_key

    def query(self, prompt_text, text_to_analyze, output_format, engine="gpt-3.5-turbo", temperature=0.7, max_tokens=300):
        """
        Sends a query to ChatGPT using the chat-specific endpoint, including a text for analysis and a specified output format, and returns the response.

        Args:
            prompt_text (str): The initial part of the prompt text with placeholders for text and format.
            text_to_analyze (str): The text that ChatGPT needs to analyze.
            output_format (str): The desired format for ChatGPT's response.
            engine (str, optional): The model engine to use. Defaults to "gpt-3.5-turbo".
            temperature (float, optional): Controls the variety of the responses. Defaults to 0.7.
            max_tokens (int, optional): The maximum length of the response. Defaults to 300.

        Returns:
            str: The response text from ChatGPT.
        """
        full_prompt = prompt_text.format(text=text_to_analyze, format=output_format)
        
        try:
            response = openai.ChatCompletion.create(
                model=engine,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": full_prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message['content'].split(", ")
        except Exception as e:
            print(f"Error: {e}")
            return "API request failed"


if __name__ == "__main__":
    client = ChatGPTClient(api_key=Config.API_KEY)
    prompt_text = ReadTXT.read_file("src/prompt/template/keywords_template.txt")
    text_to_analyze = ReadTXT.read_file("src/data/job_description/job_description.txt")
    output_format = ReadTXT.read_file("src/prompt/format/output_format.txt")
    response = client.query(prompt_text, text_to_analyze, output_format)
    print("Response from ChatGPT:", response)


