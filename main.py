import gc
import sys
from dotenv import load_dotenv
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.llms import LlamaCpp
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
#from langchain.llms import CTransformers
from ctransformers import AutoModelForCausalLM
import os
import chromadb
import time
import datetime
import winsound

from clean import clean_qa, clean_bp, clean_fbqa, extract_chapter_1, extract_chapter_2
from generate_content import QA, points, FillInTheBlanks, CheckChapter, extractChapter, OnlyCheckChapter
from db_connect import insert_chapter, get_previous_chapter_id, insert_bp, insert_fbqa, insert_qa, insert_book 
from constants import CHROMA_SETTINGS

load_dotenv()

PRIMARY_MODEL_PATH = os.environ.get("Llama2_13b_PRIMARY_PATH")  #Path to the best llama 13b model
SECONDARY_MODEL_PATH = os.environ.get("Llama2_13b_SECONDARY_PATH")  #Path to tge 2nd best llama 13b model
MISTRAL_PATH=os.environ.get("MISTRAL_PATH") #Path to the experimental model - Mistral 7b
WIZARD_PATH=os.environ.get("WIZARD_PATH") #Path to the experimental model - WIZARD 13b
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


def load_llm_2(MODEL_PATH) -> LlamaCpp:
    callback_manager : CallbackManager = CallbackManager([StreamingStdOutCallbackHandler()])
    llm : LlamaCpp = LlamaCpp(
        model_path = MODEL_PATH,
        temperature = 0.5,
        max_tokens = 1024,
        top_p = 0.9,
        top_k = 55,
        repeat_penalty = 1.2,
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


def get_chapter_id(isNew, chapterName):
    chapter_id = 1
    if isNew:
        chapter_id = insert_chapter(chapterName)
    else:
        chapter_id = get_previous_chapter_id()
        
    return chapter_id
        
        
def Generate_Raw_Data():  
          
    complete_start_time = time.time()
    chunk_processing_time = []
     
    db = call_db()
    count = db._collection.count() - 1

    #llm = load_llm(PRIMARY_MODEL_PATH)
    #llm_mistral = load_llm(MISTRAL_PATH)
    #llm_mistral_2 = load_llm_2(MISTRAL_PATH)
    #llm_mistral_orca = load_llm_2(MISTRAL_ORCA_PATH)
                     
    
    #insert_book("")
    offset = 0
    chunk_count = count//2
    chunk_count = 5 #Yeet this line in prod please
    #sys.exit("Terminating here for testing purposes")
    for chunk_num in range(chunk_count):
        start_time = time.time()
        docs = db.get(limit=2, offset=offset)
        data = ""
        for i in range(2):        
            data += docs['documents'][i]
        last_occurence = data.rfind(".")
        if last_occurence != -1:
            data = data[:last_occurence+1] 
        print(f"\n*************************************Chunk {chunk_num + 1} will be processed now**************************************\n")
        print(f"\nThe chunk is : \n{data}\n")
        print("\n***********************************************************************************************************************\n")
        #sys.exit()

        mistral_orca_start_time = time.time()
        print(f"\nThe time at which mistral-orca was loaded is : {datetime.datetime.now()}\n")
        llm_mistral_orca = load_llm_2(MISTRAL_ORCA_PATH)
        
        try:
            isNew = OnlyCheckChapter(llm_mistral_orca, data)
        except Exception as e:
            print(f"This error has occured : {e}")
            winsound.Beep(500, 500)
        finally: 
            del(llm_mistral_orca)
            
        mistral_orca_end_time = time.time()
        print(f"\nMistral Orca took : {mistral_orca_end_time-mistral_orca_start_time} secs time\n")
        # Add a gc.collect() here if necessary
        #sys.exit("I'm terminating the program here for testing purposes")
        
        chapterFound = False
        chapterName = None
        if "True" in isNew:
            mistral_start_time = time.time()
            llm_mistral = load_llm(MISTRAL_PATH)
            
            try:
                checkchapter = CheckChapter(llm_mistral, data)
                chapterText_1 = extract_chapter_1(checkchapter)
                chapterName = chapterText_1 #Delete this line if the below 2 lines are to be uncommented
                #chapterText_2 = extractChapter(llm_mistral, chapterText_1)
                #chapterName = extract_chapter_2(chapterText_2)
            except Exception as e:
                print(f"This error has occured : {e}")
                winsound.Beep(500, 500)
            finally: 
                del(llm_mistral)
            
            if chapterName:
                chapterFound = True
            mistral_end_time = time.time()
            print(f"\nMistral took : {mistral_end_time-mistral_start_time} secs time")
            print(f"\nThe chapter name is : {chapterName}")
        
    
        chapter_id = get_chapter_id(chapterFound, chapterName)
        print("\n##########  Chapter name extracted  ###############\n")
        print("Proceeding to content generation ...\n")
        #sys.exit("I'm terminating the program here for testing purposes")
        
        ##### Get questions answers generated and cleaned ######
        llama2_start_time = time.time()
        llm = load_llm(PRIMARY_MODEL_PATH)
        llama2_load_end_time = time.time()
        print(f"\nLlama 2 13-b took : {llama2_load_end_time-llama2_start_time} secs to load\n")
        print("\n*******************************************************************************************************************\n")
        
        fb_qa_all = []
        try:       
            qa = QA(llm, data)
            question_answers = clean_qa(qa)
            print("\n***************************************************************************************************************\n")
            
            ##### Get bullet points generated and cleaned #######
            bp = points(llm, data)
            bullet_points = clean_bp(bp)
            print("\n******************************************************************************************************************\n")
            
            ##### Get fill in the blanks questions generated and cleaned ######
            bullet_index = 0
            while bullet_index < len(bullet_points):
                entry = bullet_points[bullet_index]
                fb = FillInTheBlanks(llm, entry)
                fb_qa = clean_fbqa(fb)
                if (fb_qa[0] and fb_qa[1]):
                    bullet_index += 1 
                    fb_qa_all.append(fb_qa)
                    print(f"\nThe 'Fill in the blanks' array is : \n{fb_qa_all}\n")
                else:
                    print("\nDid not get a valid Fill in the blanks question\n")
                    print("Skipping iteration and removing corresponding bullet point...\n")
                    bullet_points.remove(entry)
                print("\n")
            print("\n***************************************************************************************************************\n")
                
        except Exception as e:
            print(f"This error has occured : {e}")
            winsound.Beep(500, 1500)
            
        finally: 
            del(llm)
           
        
        llama2_end_time = time.time()
        print(f"\nLlama 2 13-b took : {llama2_load_end_time-llama2_start_time} secs to generate all the responses.\n")
        #sys.exit("I'm terminating the program here for testing purposes")
               
        ####### Storing it all in the db #######
        while question_answers:
            [question, answer] = question_answers.pop(0)
            if question and answer:
                insert_qa(chapter_id, question, answer)
    
        while bullet_points:
            bullet_point = bullet_points.pop(0)
            if bullet_point:
                insert_bp(chapter_id, bullet_point)
            
        while fb_qa_all:
            [fb_question, fb_answer] = fb_qa_all.pop(0)
            if fb_answer and fb_question:
                insert_fbqa(chapter_id, fb_question, fb_answer)
                
                            
        offset += 2
    
        end_time = time.time()
        total_chunk_load_time = end_time-start_time
        chunk_processing_time.append([f"Chunk {chunk_num+1}", total_chunk_load_time])
        print(f"\nThe elapsed time is : {total_chunk_load_time}\n")
        print(f"\n\n************************ Chunk number : {chunk_num+1} has been successfully processed and the data has been stashed in the databse ************************\n\n")
    
    complete_end_time = time.time()
    total_time_elapsed = complete_end_time-complete_start_time
    total_mins = total_time_elapsed//60
    leftover_secs = total_time_elapsed%60
    print("\n\n*********************************************************************************************************\n")
    print(f"The chunk load processing times are : \n{chunk_processing_time}")
    print(f"\nThe total time taken for executing {chunk_count} chunks is : {total_mins} minutes and {leftover_secs} seconds.")
    gc.collect()
    
    
    
if __name__ == "__main__":
    Generate_Raw_Data()



