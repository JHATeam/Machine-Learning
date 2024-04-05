import openai
import os

from pydantic.v1 import BaseModel, Field
from dotenv import load_dotenv, find_dotenv
from langchain_openai import ChatOpenAI
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain.prompts import ChatPromptTemplate
from langchain_core.utils.function_calling import convert_to_openai_function

_ = load_dotenv(find_dotenv()) 
openai.api_key = os.environ['OPENAI_API_KEY']

# OpenAI Chat Completion
def get_summary(job_description):
    chat = ChatOpenAI(temperature=0.0)
    summary = chat.invoke(prompt_summary(job_description)).content
    return summary

def prompt_summary(job_description):
    template_string = """summarize the following sections of the job description:\
        text: ```{job_description}```
        Highlight the key required skills in html mark style using <mark> except job title, company, location, and date.
        """
    prompt_template = ChatPromptTemplate.from_template(template_string)
    prompt = prompt_template.format_messages(job_description = job_description)
    return prompt

def prompt_tagging(content):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Think carefully, and then tag the text as instructed"),
        ("user", "{content}")
    ])
    return prompt

class JobOverviewModel(BaseModel):
    """Overview of a job description."""
    title: str = Field(description="Find a the specific job title provided from the job description.")
    company: str = Field(description="Find the hiring organization or company from the job description.")
    location: str = Field(description="Find the primary location where the job will be based from the job description.")
    summary: str = Field(description="Summarizing detailed overview of the job role, responsibilities, and qualifications required." + 
                         "Highlight the key required skills in html mark style using <mark> except job title, company, location, and date.")
    skills: str = Field(description="Find the key required skills from the job description.")
    
def tagging_job_description(job_description):
    summary_functions = [convert_to_openai_function(JobOverviewModel)]
    model = ChatOpenAI(temperature=0)
    model_with_functions = model.bind(
        functions=summary_functions,
        function_call={"name": "JobOverviewModel"}
    )
    tagging_chain = prompt_tagging | model_with_functions | JsonOutputFunctionsParser()
    return tagging_chain.invoke(job_description)
    

if __name__ == "__main__": 
    r = tagging_job_description("We are looking for a passionate Software Engineer to design, develop and install software solutions. Software Engineer responsibilities include gathering user requirements, defining system functionality and writing code in various languages, like Java, Ruby on Rails or .NET programming languages (e.g. C++ or JScript.NET.) Our ideal candidates are familiar with the software development life cycle (SDLC) from preliminary system analysis to tests and deployment. Ultimately, the role of the Software Engineer is to build high-quality, innovative and fully performing software that complies with coding standards and technical design.")
    print(r)

