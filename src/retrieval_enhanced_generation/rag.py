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

from config.config import Config
from data_io.read_txt import ReadTXT
from models.chatgpt_client import ChatGPTClient
from embedder.text_embedder import TextEmbedder
from vector_storage.vector_store import VectorStore
from job_description_process.job_description_processor import JobDescriptionProcessor

prompt_text = ReadTXT.read_file("prompt/template/keywords_template_2.txt")
output_format = ReadTXT.read_file("prompt/format/output_format.txt")

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

    def ingest(self, pdf_file_path: str):
        docs = PyPDFLoader(file_path=pdf_file_path).load()
        chunks = self.text_splitter.split_documents(docs) #split the docs according to the resume section in next step.
        chunks = filter_complex_metadata(chunks)

        query_keywords = []
        for chunk in chunks:
            response = self.model.query(prompt_text, chunk.page_content, output_format)
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
        
        self.question = user_query
        response = self.model.query(self.prompt_text, self.context, self.question)
        response = ". ".join(response)
        print("*" * 100)
        print(response)
        
        return response

    def clear(self):
        self.vector_store = None
        self.retriever = None
        self.chain = None
