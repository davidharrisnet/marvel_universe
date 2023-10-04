
import os

from langchain.llms import OpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.docstore.document import Document
from langchain.document_loaders import DirectoryLoader
from langchain.chains import RetrievalQA
from openai.error import RateLimitError
import openai
from typing import Iterable,List, Optional
import time
import copy
from tqdm import tqdm

# imports
import random
import time
import pickle

os.environ['OPENAI_API_KEY']="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"

openai.api_key = os.environ['OPENAI_API_KEY']

def delayed_completion(delay_in_seconds: float = 1, **kwargs):
    """Delay a completion by a specified amount of time."""

    # Sleep for the delay
    time.sleep(delay_in_seconds)

    # Call the Completion API and return the result
    return openai.Completion.create(**kwargs)


# Calculate the delay based on your rate limit
rate_limit_per_minute = 100
delay = 60.0 / rate_limit_per_minute
openai_model_name = "text-davinci-002"

delayed_completion(
    delay_in_seconds=delay,
    model=openai_model_name,
    prompt="Once upon a time",
)
class Avengers:
    def __init__(self,document_directory,database_name, chain_type="stuff", openai_model_name="text-davinci-003"):
        self.openai_model_name = openai_model_name

        self.chain_type = chain_type
        self.llm = OpenAI(temperature=0.2,model_name=self.openai_model_name,max_tokens=20)
        self.embeddings_model = OpenAIEmbeddings()
        self.document_directory = document_directory
        self.database_name = database_name
        self.embedding = OpenAIEmbeddings(show_progress_bar=True,chunk_size=3)
        

    def create_database(self):
        dirs = [d for d in os.listdir(self.document_directory)]
        dirs.sort()
        for index, directory in enumerate(dirs):
          
          summary_directory = os.path.join(self.document_directory, directory)
          print(f"{index} {summary_directory}")
          self.load_docs(summary_directory)
          self.split_docs()
          self.update_database()

    def load_docs(self, summary_directory):
        print("load_docs")
      
        loader = DirectoryLoader(summary_directory, glob="*.txt", show_progress=True)
        self.documents = loader.load()
 

    def split_docs(self,chunk_size=512, chunk_overlap=128):
        print("split_docs")

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self.texts = text_splitter.split_documents(self.documents)

    def split_list(self, input_list, chunk_size):
           for i in range(0, len(input_list), chunk_size):
              yield input_list[i:i + chunk_size]
                                 
    def update_database(self):
              
        split_docs_chunked = self.split_list(self.texts, 41000)
        vectordb = None
        for split_docs_chunk in split_docs_chunked:
            vectordb = Chroma.from_documents(
                documents=split_docs_chunk,
                embedding=self.embedding,
                persist_directory=self.database_name)
        if vectordb:
            vectordb.add_documents(self.documents)
            vectordb.persist()

import os
drive = "/home/bilbo/dev/dhnet/marvel_universe"

summary_directory = os.path.join(drive, "data", "clean_fulltext_xmen/")
database_directory = os.path.join(drive, "uncannyxmendb")


a = Avengers(document_directory=summary_directory,database_name=database_directory)
a.create_database()