import chromadb
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma 
import os
from dotenv import load_dotenv

if not load_dotenv():
    print("Could not load .env file or it is empty. Please check if it exists and is readable.")
    exit(1)
    
persist_directory = os.environ.get('PERSIST_DIRECTORY')
from constants import CHROMA_SETTINGS

def wipe():
    chroma_client = chromadb.PersistentClient(settings=CHROMA_SETTINGS , path=persist_directory)
    chroma_client.reset()
    print("Contents of your vector store have been wiped")
    

if __name__=="__main__":
    wipe()