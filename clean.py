import re

import re

def clean_qa(qa_text):
    pairs = []   
    pattern = re.compile(r'Question(?: \d+)?: (.*?)\nAnswer: (.*?)(?:\n|$)', re.DOTALL)
    matches = re.findall(pattern, qa_text)
    
    try:
        for question, answer in matches:
            pairs.append([question.strip(), answer.strip()]) 
    except Exception as e:  
        print(f"Oops, the cleaning function ain't working again ... Error: {str(e)}")
    finally:
        print(f"\n\nThe question-answer pairs array is : \n{pairs}\n")
        return pairs


    

def clean_bp(bp):
    
    bullet_points = []
    
    chunk_bps = re.findall(r'•\s(.*?)(?=\n|$)', bp)
    if chunk_bps == None:
        chunk_bps = re.findall(r')\s(.*?)(?=\n|$)', bp)
    if chunk_bps == None:
        chunk_bps = re.findall(r'\d+\.\s(.*?)\n', bp)
    if chunk_bps == None:
        chunk_bps = re.findall(r'*\s(.*?)(?=\n|$)', bp)
    if chunk_bps == None:
        chunk_bps = [point.replace('* ', '').strip() for point in bp.split('\n') if point.strip()]    
    for bullet_point in chunk_bps:
        if bullet_point != None:
            bullet_points.append(bullet_point.strip())
     
    print(f"\n\nThe bullet point array is : \n {bullet_points}\n")       
    return bullet_points


import re

def clean_fbqa(text):
    
    pattern_sentence = re.compile(r'(?<=Question : )?\s*([^?!.]*_+[^?!.]*[.?!])', re.DOTALL)
    match_sentence = re.search(pattern_sentence, text)
    
    sentence = None
    if match_sentence:
        sentence = match_sentence.group(1)
        sentence = sentence.split('\n', 1)[-1].strip()
        sentence = re.sub(r'^Question\s?:\s?', '', sentence)
    
    # Extract the answer
    pattern_answer = re.compile(r'Answer\s?:\s?(.+)', re.IGNORECASE)
    match_answer = re.search(pattern_answer, text)
    
    answer = None
    if match_answer:
        answer = match_answer.group(1).strip()
    elif '(' in sentence and ')' in sentence:
        # Extract answer between ( ) if it exists and is not extracted yet
        pattern_parentheses = re.compile(r'\((.+?)\)')
        match_parentheses = re.search(pattern_parentheses, sentence)
        
        if match_parentheses:
            answer = match_parentheses.group(1).strip()
            # Remove the content within ( ) from the sentence
            sentence = re.sub(pattern_parentheses, '', sentence).strip()
    
    print(f"\nThe Fill in the blanks question and answer is : \n{[sentence, answer]}")
    return [sentence, answer]
    

def extract_chapter_1(chapterText):
    match = re.search(r'\[ANSWER\](.*?)\[/ANSWER\]', chapterText)
    chapter_name = None
    if match:
        chapter_name = match.group(1)
        print(f"\nThe first result of chapter extraction is : {chapter_name}\n")
    else:
        print("Chapter not found")
    
    return chapter_name

def extract_chapter_2(chapterText):
    print(f"The extracted text is : {chapterText}")
    pattern = r'\[SOL\](.*?)\[/SOL\]'
    match = re.search(pattern, chapterText, re.DOTALL)
    print(f"\n\n The content within the [SOL] is : {match}")
    extracted_content = match.group(1)
    print(f"Extracted match between [SOL] : {extracted_content}")
    
    pattern = r'"([^"]+)"'
    match = re.search(pattern, extracted_content)
    print(f"The final match is : {match}")
    result = match.group(1)

    return result


    
    
