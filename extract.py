import fitz
import spacy
import json
from collections import defaultdict

nlp = spacy.load("en_core_web_sm")

def is_continuous(text1, text2):
    """Check if two texts can be part of a continuous sentence using NLP."""
    combined_text = nlp(text1 + " " + text2)
    return len(list(combined_text.sents)) == 1  # Only one sentence

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)

    # To store the frequency of each font size
    font_sizes = defaultdict(int)  

    # Collect font sizes and their frequencies
    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if block['type'] == 0:  # Text block
                lines = block["lines"]
                for line in lines:
                    span = line["spans"][0]
                    fontsize = span["size"]
                    font_sizes[fontsize] += 1

    # Determine the most frequently used font size
    common_font_size = max(font_sizes, key=font_sizes.get)

    # For storing the extracted data
    content_structure = {
        "headings": [],
        "sub_headings": {},
        "content": {},
        "boxed_content": {},
        "references": {},
        "page_numbers": []
    }

    current_heading = None
    current_sub_heading = None

    # Iterate through each page of the PDF
    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        
        for block in blocks:
            if block['type'] == 0:  # Text block
                lines = block["lines"]
                for index, line in enumerate(lines):
                    span = line["spans"][0]
                    text = span["text"]
                    fontsize = span["size"]

                    # Check if this line and the next line form a continuous sentence (assuming they're not the last line)
                    if index < len(lines) - 1:
                        next_text = lines[index + 1]["spans"][0]["text"]
                        if is_continuous(text, next_text):
                            text += " " + next_text

                    # Adjust based on the most common font size
                    if fontsize > common_font_size * 1.2:  # Heading or sub-heading if it's 20% larger than common
                        if current_heading:
                            current_sub_heading = text
                            content_structure["sub_headings"].setdefault(current_heading, []).append(current_sub_heading)
                            content_structure["content"][current_sub_heading] = []
                        else:
                            current_heading = text
                            content_structure["headings"].append(current_heading)
                            current_sub_heading = None
                    elif fontsize < common_font_size * 0.8:  # Reference or footer if it's 20% smaller than common
                        if text.isdigit():
                            content_structure["page_numbers"].append(text)
                        else:
                            content_structure["references"].setdefault(current_sub_heading or current_heading, []).append(text)
                    else:  # Regular content
                        if current_sub_heading:
                            content_structure["content"].setdefault(current_sub_heading, []).append(text)
                        elif current_heading:
                            content_structure["content"].setdefault(current_heading, []).append(text)
                        
                        # Handle boxed content
                        if block["bbox"][2] - block["bbox"][0] < page.rect.width * 0.6:  # If width is less than 60% of the page width
                            content_structure["boxed_content"].setdefault(current_sub_heading or current_heading, []).append(text)

    return content_structure

# Use the function
pdf_path = "source_documents/trial_2.pdf"
result = extract_text_from_pdf(pdf_path)

with open('raw_data/extracted_content.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=4)

