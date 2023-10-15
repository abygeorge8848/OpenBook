import sys
from dotenv import load_dotenv
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.llms import LlamaCpp
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from ctransformers import AutoModelForCausalLM
import os
import chromadb

from constants import CHROMA_SETTINGS

load_dotenv()

PRIMARY_MODEL_PATH = os.environ.get("Llama2_13b_PRIMARY_PATH")  #Path to the best llama 13b model
SECONDARY_MODEL_PATH = os.environ.get("Llama2_13b_SECONDARY_PATH")  #Path to tge 2nd best llama 13b model
MISTRAL_PATH=os.environ.get("MISTRAL_PATH") #Path to the experimental model - Mistral 7b
MISTRAL_ORCA_PATH=os.environ.get("MISTRAL_ORCA_PATH")
embeddings_model_name = os.environ.get("EMBEDDINGS_MODEL_NAME")
persist_directory = os.environ.get('PERSIST_DIRECTORY')


def load_llm(MODEL_PATH) -> LlamaCpp:
    callback_manager : CallbackManager = CallbackManager([StreamingStdOutCallbackHandler()])
    llm : LlamaCpp = LlamaCpp(
        model_path = MODEL_PATH,
        temperature = 0.7,
        max_tokens = 1024,
        top_p = 0.1,
        top_k = 40,
        repeat_penalty = 1.176,
        callback_manager = callback_manager,
        n_batch=512,
        n_gpu_layers = 25,
        #use_mlock = True,
        verbose = False 
    )
    return llm


def call_db():
    embeddings = HuggingFaceEmbeddings(model_name=embeddings_model_name)
    chroma_client = chromadb.PersistentClient(settings=CHROMA_SETTINGS , path=persist_directory)
    db = Chroma(persist_directory=persist_directory, embedding_function=embeddings, client_settings=CHROMA_SETTINGS, client=chroma_client)

    return db


def generate_raw_data():
    
    db = call_db()
    count = db._collection.count() - 1

    chunk_count = count//4
    leftover_chunk_count = count%4
    exercises_found = False
    chapter_found = False
    for chunk_num in chunk_count: 
        docs = db.get(limit=4, offset=0)
        data = ""
        for i in range(4):        
            data += docs['documents'][i]
            last_occurence = data.rfind(".")
        if last_occurence != -1:
            data = data[:last_occurence+1] 
        
        chunk_likeliness = 0
        if 'EXERCISES' in data:
            chunk_likeliness += 0.5
        if 'CHAPTER' in data:
            if exercises_found:
                break
            chunk_likeliness -= 0.3
        chunk_likeliness += 0.1*data.count('?')
        






if __name__ == "__main__":
    sys.exit(generate_raw_data)































