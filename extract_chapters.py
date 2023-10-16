import sys
from dotenv import load_dotenv
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.llms import LlamaCpp
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from ctransformers import AutoModelForCausalLM
import os
import re
import chromadb

from constants import CHROMA_SETTINGS

load_dotenv()

PRIMARY_MODEL_PATH = os.environ.get("Llama2_13b_PRIMARY_PATH")  #Path to the best llama 13b model
SECONDARY_MODEL_PATH = os.environ.get("Llama2_13b_SECONDARY_PATH")  #Path to tge 2nd best llama 13b model
MISTRAL_PATH=os.environ.get("MISTRAL_PATH") #Path to the experimental model - Mistral 7b
MISTRAL_ORCA_PATH=os.environ.get("MISTRAL_ORCA_PATH")
embeddings_model_name = os.environ.get("EMBEDDINGS_MODEL_NAME")
persist_directory = os.environ.get('PERSIST_DIRECTORY')


def call_db():
    embeddings = HuggingFaceEmbeddings(model_name=embeddings_model_name)
    chroma_client = chromadb.PersistentClient(settings=CHROMA_SETTINGS , path=persist_directory)
    db = Chroma(persist_directory=persist_directory, embedding_function=embeddings, client_settings=CHROMA_SETTINGS, client=chroma_client)

    return db


def generate_raw_data():
    
    db = call_db()
    count = db._collection.count() - 1
    docs = db.get(limit=count, offset=0)['documents']
    
    for i in range(count+1):
        if 'CHAPTER' in docs[i]:
            chunk_likeliness_chapter = 0.3
            fragment = docs[i-1] if i>0 else "" + docs[i] + docs[i+1] if i<count else ""
            
             
            
            
        
    
    
    
    
        






if __name__ == "__main__":
    sys.exit(generate_raw_data())