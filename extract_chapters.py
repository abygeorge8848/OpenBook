import sys
from dotenv import load_dotenv
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.llms import LlamaCpp
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import RetrievalQA
import argparse
import os
import re
import chromadb
import pandas as pd

from constants import CHROMA_SETTINGS
from db_connect import insert_questions, insert_answers, retrieve_answers

load_dotenv()

PRIMARY_MODEL_PATH = os.environ.get("Llama2_13b_PRIMARY_PATH")  #Path to the best llama 13b model
SECONDARY_MODEL_PATH = os.environ.get("Llama2_13b_SECONDARY_PATH")  #Path to tge 2nd best llama 13b model
MISTRAL_PATH=os.environ.get("MISTRAL_PATH") #Path to the experimental model - Mistral 7b
MISTRAL_ORCA_PATH=os.environ.get("MISTRAL_ORCA_PATH")
embeddings_model_name = os.environ.get("EMBEDDINGS_MODEL_NAME")
persist_directory = os.environ.get('PERSIST_DIRECTORY')
target_source_chunks = int(os.environ.get('TARGET_SOURCE_CHUNKS',4))


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


def chapter_confidence_metric(text):
    confidence = 0.0
    if 'chapter' in text.lower():
        confidence += 0.2
    if re.search(r'\bCHAPTER\b', text):
        confidence += 0.4
    if re.search(r'\n\s*CHAPTER', text) or re.search(r'CHAPTER\s*\n', text):
        confidence += 0.2
    if re.search(r'(\d+\s*\bCHAPTER\b|\bCHAPTER\b\s*\d+)', text, re.IGNORECASE):
        confidence += 0.2   
    return confidence


def exercise_confidence_metric(text):
    confidence = 0.0
    if 'exercises' in text.lower():
        confidence += 0.2
    if re.search(r'\bEXERCISES\b', text):
        confidence += 0.4
    if re.search(r'\n\s*EXERCISES', text) or re.search(r'EXERCISES\s*\n', text):
        confidence += 0.2
    if re.search(r'(\d+\s*\bEXERCISES\b|\bEXERCISES\b\s*\d+)', text, re.IGNORECASE):
        confidence += 0.2
    return confidence


def extract_questions(chunk):
    pattern = r'[^.!?]*\?'
    return re.findall(pattern, chunk)



def generate_answer(question):
    
    args = parse_arguments()
    db = call_db()
    llm = load_llm(PRIMARY_MODEL_PATH)
    retriever = db.as_retriever(search_kwargs={"k": target_source_chunks})
    qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever, return_source_documents= not args.hide_source)
    res = qa(question)
    
    return res['result'] 


def parse_arguments():
    parser = argparse.ArgumentParser(description='Stuff, '
                                                 'more stuff.')
    parser.add_argument("--hide-source", "-S", action='store_true',
                        help='Use this flag to disable printing of source documents used for answers.')
    parser.add_argument("--mute-stream", "-M",
                        action='store_true',
                        help='Use this flag to disable the streaming StdOut callback for LLMs.')
    return parser.parse_args()


def generate_raw_data():
    
    raw_data = ""
    db = call_db()
    count = db._collection.count() - 1
    docs = db.get(limit=count, offset=0)['documents']
    questions = []
                                         
    for i in range(count+1):
        chunk = docs[i]
        
        question_mark_count = chunk.count('?')
        chapter_confidence_score = chapter_confidence_metric(chunk)
        exercise_confidence_score = exercise_confidence_metric(chunk)
        
        questions = extract_questions(chunk)
        for question in questions:
            answer = generate_answer(question.strip())
            #answer = cleaned_answer(answer)
            insert_questions(question)
            insert_answers(answer)
            
    
    answers = retrieve_answers()
    for row in answers:
        answer = row[0]
        raw_data += answer

    return raw_data
            



if __name__ == "__main__":
    sys.exit(generate_raw_data())