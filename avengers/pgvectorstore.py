import psycopg2
from pgvector.psycopg2 import register_vector
import pandas as pd
import numpy as np

import os
import getpass

os.environ['OPENAI_API_KEY']="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"
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores.pgvector import PGVector
from langchain.document_loaders import TextLoader
from langchain.docstore.document import Document

import openai


from langchain.llms import OpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.docstore.document import Document
from langchain.document_loaders import DirectoryLoader
from langchain.chains import RetrievalQA
from sentence_transformers import SentenceTransformer

class Avengers:

    def __init__(self, document_directory,chain_type="stuff", openai_model_name="text-davinci-003"):
        self.document_directory = document_directory 
        self.CONNECTION_STRING = PGVector.connection_string_from_db_params(
                driver="psycopg2",
                host="localhost",
                port="5432",
                database="vectordb",
                user="marvel_user",
                password="password#1"
            )
        self.vectordb = None
        self.chain_type = chain_type
        self.openai_model_name=openai_model_name

    def get_connection(self):
        conn = psycopg2.connect(
          database="vectordb", user='marvel_user', password='password#1', host='127.0.0.1', port= '5432'          
        )

        conn.autocommit = True
        register_vector(conn)
        return conn.cursor()
    
    def load_docs(self):
        print("load_docs")
        loader = DirectoryLoader(self.document_directory, glob="**/*.txt",
                                show_progress=True)
        self.documents = loader.load()

    def split_docs(self,chunk_size=512, chunk_overlap=128):
        print("split_docs")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self.texts = text_splitter.split_documents(self.documents)
    """
    def vectorize1(self):      
            print("vectorize")
            embeddings = OpenAIEmbeddings()
            self.vectordb = PGVector.from_documents(
                embedding=embeddings,
                documents=self.documents,
                collection_name="marvel_summaries",
                connection_string=self.CONNECTION_STRING 
            )        
    """
    def vectorize(self):
        print("vectorize")

        #embeddings = OpenAIEmbeddings(show_progress_bar=True,chunk_size=3)
        model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        connection = self.get_connection()
        
        def split_list(input_list, chunk_size):
           for i in range(0, len(input_list), chunk_size):
              yield input_list[i:i + chunk_size]
        
        split_docs_chunked = split_list(self.texts, 41000)

        for split_docs_chunk in split_docs_chunked:
            input = [ chunk.page_content for chunk in split_docs_chunk]
            
            embeddings = model.encode(input)
            for content, embedding in zip(input,embeddings):     
                connection.execute('INSERT INTO documents (content, embedding) VALUES (%s, %s)', (content, embedding))

    def get_qa(self):
        class Page:
            def __init__(self,text):
                self.page_content = text
                self.metadata = {}

        connection = self.get_connection()
        connection.execute('SELECT content from documents')
        text_tuples = connection.fetchall()
        embeddings = OpenAIEmbeddings()
        texts = [ t[0])  for t in text_tuples ]
        
        docsearch = PGVector.from_documents(texts, embeddings)

        llm = OpenAI(model_name=self.openai_model_name)
        self.qa = RetrievalQA.from_chain_type(llm=llm,
                                              chain_type=self.chain_type,
                                              retriever=docsearch.as_retriever(),
                                              return_source_documents=True)



    def ask_question1(self,question):
        
        docs_with_score = self.db.similarity_search_with_score(question)
        for doc, score in docs_with_score:
            print("-" * 80)
            print("Score: ", score)
            print(doc.page_content)
            print("-" * 80) 

    def ask_question(self, question):
        self.get_qa()
        result = self.qa({"query", "Who is Scott Summers?"})
        return result
    
if __name__ == "__main__":
    document_directory = "data/clean_fulltext_xmen/"
    summary_directory = os.path.join(document_directory, "100thAnniversarySpecial")
    a = Avengers(summary_directory)
    #a.load_docs()
    #a.split_docs()   
    #a.vectorize()


    question = "Who is Scott Summers?"
    result = a.ask_question(question)
    print(f"\nResult: {result['result']}\n")
    print(f"Documents: {result['source_documents']}\n")