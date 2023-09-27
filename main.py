from dotenv import load_dotenv
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
import os
import chromadb
from langchain.llms import LlamaCpp
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import re
from constants import CHROMA_SETTINGS

load_dotenv()

PRIMARY_MODEL_PATH = os.environ.get("PRIMARY_MODEL_PATH")
SECONDARY_MODEL_PATH = os.environ.get("SECONDARY_MODEL_PATH")
embeddings_model_name = os.environ.get("EMBEDDINGS_MODEL_NAME")
persist_directory = os.environ.get('PERSIST_DIRECTORY')


def load_llm(MODEL_PATH) -> LlamaCpp:
    callback_manager : CallbackManager = CallbackManager([StreamingStdOutCallbackHandler()])
    llm : LlamaCpp = LlamaCpp(
        model_path = MODEL_PATH,
        temperature = 0.9,
        max_tokens = 2048,
        top_p = 0.6,
        callback_manager = callback_manager,
        verbose = True
    )
    
    return llm


def QA(llm, data):
    
    prompt = f"""Use the DATA given below to make and return ONLY three question-answer pairs from the below data and return them in the format:
    ```Question n : question,   Answer n : answer```
            DATA : {data} 
    """
    
    response : str = llm(prompt)
    
    return response


def clean_qa(qa, qa_pairs):
    lines = qa.split('\n')
    current_pair = []
    for line in lines:
        line = line.strip() 
        if line.startswith("Question"):
            current_pair = [line.split(" : ")[1].strip()] 
        elif line.startswith("Answer"):
            current_pair.append(line.split(" : ")[1].strip()) 
        qa_pairs.append(current_pair)

    

def points(llm, data):
    
    prompt = f"""Use the DATA given below to find only ONLY three of the most import facts from the below data and return them as bullet points.
            DATA : {data} 
    """
    
    response : str = llm(prompt)
    
    return response

def clean_bp(bp, bullet_points):
    chunk_bps = re.findall(r'•\s(.*?)(?=\n|$)', bp)
    for bullet_point in chunk_bps:
        bullet_points.append(bullet_point.strip())
        
        
def call_db():
    embeddings = HuggingFaceEmbeddings(model_name=embeddings_model_name)
    chroma_client = chromadb.PersistentClient(settings=CHROMA_SETTINGS , path=persist_directory)
    db = Chroma(persist_directory=persist_directory, embedding_function=embeddings, client_settings=CHROMA_SETTINGS, client=chroma_client)

    return db

def main():   
    
    db = call_db()
    llm = load_llm(SECONDARY_MODEL_PATH)
    
    count = db._collection.count() - 1
    chunk_count = count//2
    
    offset = 0
    question_answers = []
    bullet_points = []
    #for i in range(chunk_count):
    for i in range(1):
        docs = db.get(limit=2, offset=offset)
        data = ""
        for i in range(2):        
            data += docs['documents'][i]
            last_occurence = data.rfind(".")
            if last_occurence != -1:
                data = data[:last_occurence+1] 
            data.replace("\n", " ")

        #qa = QA(llm, data)
        #clean_qa(qa, question_answers)  
      
        bp = points(llm, data)
        clean_bp(bp, bullet_points)
            
        offset += 2
    
    print(f"The bullet points are : {bp}" )
    print(f"The bullet point array is : {bullet_points}" )

   
    
if __name__ == "__main__":
    main()






