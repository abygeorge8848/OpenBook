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

    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if block['type'] == 0:
                lines = block["lines"]
                for line in lines:
                    span = line["spans"][0]
                    fontsize = span["size"]
                    font_sizes[fontsize] += 1

    common_font_size = max(font_sizes, key=font_sizes.get)

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

    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        pending_fragments = []

        for block in blocks:
            if block['type'] == 0:
                lines = block["lines"]
                for index, line in enumerate(lines):
                    span = line["spans"][0]
                    text = span["text"].strip()
                    fontsize = span["size"]

                    # Check for individual character fragments
                    if len(text) == 1 and not text.isdigit() and fontsize > common_font_size:
                        pending_fragments.append(text)
                        continue
                    elif pending_fragments and is_valid_word_or_phrase(merge_fragments(pending_fragments + [text])):
                        text = merge_fragments(pending_fragments + [text])
                        pending_fragments.clear()
                    elif pending_fragments:
                        pending_fragments.clear()

                    if index < len(lines) - 1:
                        next_text = lines[index + 1]["spans"][0]["text"]

                        # Check if current line makes sense with the next one
                        if is_continuous(text, next_text):
                            text += " " + next_text

                    if fontsize > common_font_size * 1.2:
                        # Check for short lines that might be the start of a paragraph
                        if len(text) < 10 and index < len(lines) - 1:
                            next_text = lines[index + 1]["spans"][0]["text"]
                            if is_continuous(text, next_text):
                                text += " " + next_text
                                content_structure["content"].setdefault(current_sub_heading or current_heading, []).append(text)
                                continue

                        if current_heading:
                            current_sub_heading = text
                            content_structure["sub_headings"].setdefault(current_heading, []).append(current_sub_heading)
                            content_structure["content"][current_sub_heading] = []
                        else:
                            current_heading = text
                            content_structure["headings"].append(current_heading)
                            current_sub_heading = None
                    elif fontsize < common_font_size * 0.8:
                        if text.isdigit():
                            content_structure["page_numbers"].append(text)
                        else:
                            content_structure["references"].setdefault(current_sub_heading or current_heading, []).append(text)
                    else:
                        if current_sub_heading:
                            content_structure["content"].setdefault(current_sub_heading, []).append(text)
                        elif current_heading:
                            content_structure["content"].setdefault(current_heading, []).append(text)

                        if block["bbox"][2] - block["bbox"][0] < page.rect.width * 0.6:
                            content_structure["boxed_content"].setdefault(current_sub_heading or current_heading, []).append(text)

    return content_structure

pdf_path = "source_documents/trial_2.pdf"
result = extract_text_from_pdf(pdf_path)

with open('raw_data/extracted_content2.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=4)
    
    
    