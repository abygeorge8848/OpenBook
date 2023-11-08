import fitz
import spacy
import json
from collections import defaultdict


nlp = spacy.load("en_core_web_sm")


def merge_fragments(texts):
    """Merge individual characters into a word or phrase."""
    return ''.join(texts).replace(" ", "")

def is_continuous(text1, text2):
    """Check if two texts can be part of a continuous sentence without forming unintended compound words using NLP."""
    separate_tokens = set([token.text for token in nlp(text1)] + [token.text for token in nlp(text2)])
    combined_tokens = set([token.text for token in nlp(text1 + " " + text2)])
    return combined_tokens == separate_tokens

def is_valid_word_or_phrase(text):
    """Check if a merged sequence of characters forms a valid word or phrase using NLP."""
    tokens = nlp(text)
    return any(token.is_alpha for token in tokens)  # At least one valid word

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    font_sizes = defaultdict(int)

    # Calculate font sizes and get the most common font size
    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if block['type'] == 0:
                for line in block["lines"]:
                    span = line["spans"][0]
                    fontsize = span["size"]
                    font_sizes[fontsize] += 1

    common_font_size = max(font_sizes, key=font_sizes.get)

    content_structure = {
        "chapters": [],
        "headings": [],
        "sub_headings": [],
        "content": [],
        "boxed_content": [],
        "footer_content": [],
        "page_numbers": [],
        "references": [],
        "questions": []
    }

    current_chapter = None
    current_heading = None

    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            if block['type'] == 0:
                lines = block["lines"]

                # Using the utility function to join texts
                for i in range(len(lines) - 1):
                    line1 = lines[i]["spans"][0]["text"].strip()
                    line2 = lines[i+1]["spans"][0]["text"].strip()
                    if is_continuous(line1, line2):
                        lines[i+1]["spans"][0]["text"] = line1 + " " + line2
                        lines[i]["spans"][0]["text"] = ""

                for line in lines:
                    span = line["spans"][0]
                    text = span["text"].strip()
                    fontsize = span["size"]

                    if not text:
                        continue

                    if fontsize > common_font_size * 1.5 or ("Chapter" in text):
                        current_chapter = text
                        content_structure["chapters"].append(current_chapter)
                        current_heading = None
                    elif fontsize > common_font_size * 1.2:
                        current_heading = text
                        content_structure["headings"].append(current_heading)
                    elif fontsize > common_font_size:
                        content_structure["sub_headings"].append(text)
                    elif fontsize < common_font_size * 0.8:
                        if text.isdigit():
                            content_structure["page_numbers"].append(text)
                        else:
                            content_structure["references"].append(text)
                    else:
                        content_structure["content"].append(text)

                    if block["bbox"][2] - block["bbox"][0] < page.rect.width * 0.6:
                        content_structure["boxed_content"].append(text)
                    if block["bbox"][1] > page.rect.height * 0.85:
                        content_structure["footer_content"].append(text)
                    if "Q." in text or "?" in text:
                        content_structure["questions"].append(text)

    return content_structure


pdf_path = "source_documents/trial_2.pdf"
result = extract_text_from_pdf(pdf_path)

with open('raw_data/extracted_content3.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=4)