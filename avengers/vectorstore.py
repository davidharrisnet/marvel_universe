import psycopg2

#establishing the connection
#conn = psycopg2.connect(
#   database="vectordb", user='marvel_user', password='password#1', host='127.0.0.1', port= '5432'
#)
#conn.autocommit = True

#Creating a cursor object using the cursor() method
#cursor = conn.cursor()

#print(cursor)

#https://python.langchain.com/docs/integrations/vectorstores/pgvector

import os
import getpass

os.environ['OPENAI_API_KEY']="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"
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores.pgvector import PGVector
from langchain.document_loaders import TextLoader
from langchain.docstore.document import Document


from langchain.llms import OpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.docstore.document import Document
from langchain.document_loaders import DirectoryLoader
from langchain.chains import RetrievalQA

"""
print(os.getcwd())

loader = TextLoader("./data/state_of_the_union.txt")
documents = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(documents)

embeddings = OpenAIEmbeddings()

CONNECTION_STRING = PGVector.connection_string_from_db_params(
     driver="psycopg2",
     host="localhost",
     port="5432",
     database="vectordb",
     user="marvel_user",
     password="password#1"
 )


COLLECTION_NAME = "state_of_the_union_test"

db = PGVector.from_documents(
    embedding=embeddings,
    documents=docs,
    collection_name=COLLECTION_NAME,
    connection_string=CONNECTION_STRING,
)

query = "What did the president say about Ketanji Brown Jackson"
docs_with_score = db.similarity_search_with_score(query)
for doc, score in docs_with_score:
    print("-" * 80)
    print("Score: ", score)
    print(doc.page_content)
    print("-" * 80)
"""
class Avengers:

    def __init__(self, document_directory):
        self.document_directory = document_directory
        self.embeddings = OpenAIEmbeddings()
        self.db = None

    def load_docs(self):
        print("load_docs")
        loader = DirectoryLoader(self.document_directory, glob="**/*.txt",
                                show_progress=True)
        self.documents = loader.load()

    def split_docs(self,chunk_size=512, chunk_overlap=128):
        print("split_docs")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self.texts = text_splitter.split_documents(self.documents)

    def vectorize(self):      
            print("vectorize")
            CONNECTION_STRING = PGVector.connection_string_from_db_params(
                driver="psycopg2",
                host="localhost",
                port="5432",
                database="vectordb",
                user="marvel_user",
                password="password#1"
            )
            self.db = PGVector.from_documents(
                embedding=self.embeddings,
                documents=self.documents,
                collection_name="marvel_summaries",
                connection_string=CONNECTION_STRING,
            )        
    def ask_question(self,question):
        
        docs_with_score = self.db.similarity_search_with_score(question)
        for doc, score in docs_with_score:
            print("-" * 80)
            print("Score: ", score)
            print(doc.page_content)
            print("-" * 80) 


if __name__ == "__main__":
    document_directory = "data/clean_fulltext_xmen/"
    summary_directory = os.path.join(document_directory, "100thAnniversarySpecial")
    a = Avengers(summary_directory)
    a.load_docs()
    a.split_docs()   
    a.vectorize()
    a.ask_question("Who is Scott Summers?")