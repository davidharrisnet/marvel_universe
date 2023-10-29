from langchain.llms import OpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.docstore.document import Document
from langchain.document_loaders import DirectoryLoader
from langchain.chains import RetrievalQA
import os
os.environ['OPENAI_API_KEY']="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"

class MarvelQuestions:
    def __init__(self,
                database_name,
                openai_model_name="text-davinci-002",
                chain_type="stuff"):

        self.chain_type = chain_type
        self.openai_model_name = openai_model_name
        self.chain_type = self.chain_type
        self.database_name = database_name
        self.get_database()

    def get_database(self):
        embeddings_model = OpenAIEmbeddings()

        #Load the database
        self.vectordb = Chroma(persist_directory=self.database_name,
                        embedding_function=embeddings_model)
    def get_qa(self):
        llm = OpenAI(model_name=self.openai_model_name)
        self.qa = RetrievalQA.from_chain_type(llm=llm,
                                              chain_type=self.chain_type,
                                              retriever=self.vectordb.as_retriever(),
                                              return_source_documents=True)

    def ask_question(self, query):
        self.get_qa()
        result = self.qa({"query": query})
        return result
    
import os
drive = "C:\\Users\\584400\\Documents\\Dev\\python\\dhnet\\marvel_universe\\data"
database_directory = os.path.join(drive, "clean_fulltext_xmen")

if __name__ == "__main__":
    mq = MarvelQuestions(database_directory)
    question = ""
    while question != "quit":
        print("Give a question")
        question = input()
        try:
          result = mq.ask_question(question)
          print(f"\nResult: {result['result']}\n")
          print(f"Documents: {result['source_documents']}\n")
        except Exception as e:
            print(e)