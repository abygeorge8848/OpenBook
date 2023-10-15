def QA(llm, data):
    
    prompt = f"""<s>[INST] <<SYS>>\nYou are an AI assistant converting raw data into question-answer pairs. Return nothing else but 3 question-answer pairs with the questions and answers labelled.\n<</SYS>>\n\n{data} [/INST]
"""
    
    response : str = llm(prompt)
    return response


def points(llm, data):

    prompt = f"""<s>[INST] <<SYS>>\nYou are an AI assistant making bullet points of the most important facts from the given data. Return nothing else but 3 bullet points\n<</SYS>>\n\n{data} [/INST]
    """
    response : str = llm(prompt)
    return response


def FillInTheBlanks(llm, data):
    
    prompt = f"""<s>[INST] <<SYS>>\nYou are an AI assistant converting a sentence into a 'Fill in the blank' question and answer pair by replacing the key word in the sentence with a '______' and returning the response. The response should be in a ```Question : question \\n Answer : answer``` where the 'question' is the sentence with the blank and the 'answer' is the key word which was replaced by the '______'.\n<</SYS>>\n\n{data} [/INST]
    """
    
    response : str = llm(prompt)
    return response


def OnlyCheckChapter(llm, data):
    
    prompt = f"""<|im_start|>system
    You are an AI assistant who will give only True or False responses to the questions asked.
    <|im_end|>
    <|im_start|>user
    From the below data, check whether the word 'CHAPTER' or 'Chapter' is present or not.
    DATA : {data}
    <|im_end|> 
    <|im_start|>assistant  
    """

    response : str = llm(prompt)
    return response 


def CheckChapter(llm, data):
    
    prompt = f"""<s>[INST]Check in the DATA given below, whether there is a Chapter name. If there is no chapter name, only return 'NONE' as the response. If there is a Chapter name, return ONLY the chapter name.
           DATA - {data}[/INST]        
        """  
    
    response : str = llm(prompt)
    return response 

def extractChapter(llm, data):
    
    prompt = f"""<s>[INST]The SENTENCE given below has the name of a chapter in it. Extract the name of the chapter and only return that.
    
    SENTENCE :{data}[/INST]
    """
    
    response : str = llm(prompt)
    return response 

