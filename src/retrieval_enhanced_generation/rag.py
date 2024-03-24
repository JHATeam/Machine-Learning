from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOllama
from langchain.embeddings import FastEmbedEmbeddings
from langchain.schema.output_parser import StrOutputParser
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.runnable import RunnablePassthrough
from langchain.prompts import PromptTemplate
from langchain.vectorstores.utils import filter_complex_metadata

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import re
from config.config import Config
from data_io.read_txt import ReadTXT
from models.chatgpt_client import ChatGPTClient
from embedder.text_embedder import TextEmbedder
from vector_storage.vector_store import VectorStore
from job_description_process.job_description_processor import JobDescriptionProcessor

keywords_prompt_template = ReadTXT.read_file("prompt/template/keywords_template_2.txt")
output_format = ReadTXT.read_file("prompt/format/output_format.txt")

user_inquire_template = ReadTXT.read_file("prompt/template/user_inquire_template.txt")
user_inquire_template_2 = ReadTXT.read_file("prompt/template/user_inquire_template_2.txt")
output_format_2 = ReadTXT.read_file("prompt/format/output_format_2.txt")
output_format_3 = ReadTXT.read_file("prompt/format/output_format_3.txt")

folder_path = "data/job_description"
dimension = 384
model_name = "models/all-MiniLM-L12-v2"


class ChatResume:
    vector_store = None
    retriever = None
    chain = None

    def __init__(self):
        self.model = ChatGPTClient(api_key=Config.API_KEY)
        self.embedder = TextEmbedder()
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=100)

        self.vector_store = VectorStore(dimension, model_name) 
        self.processor = JobDescriptionProcessor(Config.API_KEY, folder_path, self.vector_store)
        self.processor.process_files()

        self.context = None
        self.question = None
        self.prompt_text = """
            You are an assistant for question-answering tasks. Use the following pieces of retrieved context 
            to answer the question. If you don't know the answer, just say that you don't know. 
            
            Context: 
            {text}
            
            Question: 
            {format} 
        """

        # Initialize variables to track the conversation state
        self.is_first_inquiry = True  # Whether it's the user's first inquiry
        self.summary_confirmed = False  # Whether the user has confirmed the summary
        self.inquiry_summary = ""  # Store the summary of the inquiry

    def ingest(self, pdf_file_path: str):
        docs = PyPDFLoader(file_path=pdf_file_path).load()
        chunks = self.text_splitter.split_documents(docs) #split the docs according to the resume section in next step.
        chunks = filter_complex_metadata(chunks)

        query_keywords = []
        for chunk in chunks:
            response = self.model.query(keywords_prompt_template, chunk.page_content, output_format)
            response = response.choices[0].message['content'].split(", ")
            query_keywords.extend(response)
        print(query_keywords)

        results = self.processor.search_descriptions(query_keywords, k=2)

        selected_job_description = """
        Here are the selected job descriptions matching with the uploaded resume:

        """
        for text, score in results:
            selected_job_description = selected_job_description + text + "\n"
        self.context = selected_job_description

    def ask(self, user_query: str):
        if not self.context:
            return "Please, add a PDF resume first."
        
        # If it's the user's first inquiry
        if self.is_first_inquiry:
            # Use a prompt to generate a summary of the user's inquiry

            response = self.model.query(user_inquire_template, user_query, output_format_2)
            self.inquiry_summary = [re.sub(r"^[*-,.]|[*-,.]$", "", line.strip()) for line in response.choices[0].message['content'].split("\n")]
            self.is_first_inquiry = False  # Update the flag
            
            summary_str = "\n".join(self.inquiry_summary)
            message = f"We have summarized your inquiry as follows, please confirm or suggest modifications (reply yes or satisfied for confirmation, reply others for modifications):\n{summary_str}"
            return message
        
        # If the user has not confirmed the summary yet
        if not self.summary_confirmed:
            # Check if the user is suggesting modifications
            if "Yes" in user_query or "satisfied" in user_query:
                self.summary_confirmed = True  # User has confirmed the summary
            else:
                # Assuming here we update the summary based on user feedback
             
                previous_summary = "\n".join(self.inquiry_summary)
                user_inquire_template_2_update = user_inquire_template_2.format(text="{text}", previous_summary=previous_summary, format="{format}")
                print(user_inquire_template_2_update)
                response = self.model.query(user_inquire_template_2_update, user_query, output_format_3)
                self.inquiry_summary = [re.sub(r"^[*-,.]|[*-,.]$", "", line.strip()) for line in response.choices[0].message['content'].split("\n")]
                
                summary_str = "\n".join(self.inquiry_summary)
                message = f"According to your feedback, we have summarized your inquiry as follows, please confirm or suggest modifications (reply yes or satisfied for confirmation, reply others for modifications): \n{summary_str}"
                return message
        
        # If the user has confirmed the summary, handle user inquiry from summary
        if self.summary_confirmed:
            # Here, handle the user's inquiry based on the confirmed summary
            summary_str = "\n".join(self.inquiry_summary)
            message = f"According to your feedback, these are the final summary of your inquiry: \n{summary_str}"
            return message


        """
        self.question = user_query
        response = self.model.query(self.prompt_text, self.context, self.question)
        response = response.choices[0].message['content'].split(", ")
        response = ". ".join(response)
        print("*" * 100)
        print(response) 
        
        return response
        """

    def clear(self):
        self.vector_store = None
        self.retriever = None
        self.chain = None
