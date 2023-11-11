import json
import os
import unicodedata

def remove_non_ascii_characters(text):
    # Normalize the Unicode string, then encode to ASCII bytes, ignoring errors
    normalized_text = unicodedata.normalize('NFKD', text)
    ascii_text = normalized_text.encode('ascii', 'ignore')
    return ascii_text.decode('ascii')

def remove_consecutive_duplicates_and_empty_keys(data):
    cleaned_data = {}
    for key, values in data.items():
        # Process the key to remove non-ASCII characters
        key = remove_non_ascii_characters(key) if isinstance(key, str) else key

        if isinstance(values, list):
            unique_values = []
            previous_value = None
            for value in values:
                if isinstance(value, str):
                    value = remove_non_ascii_characters(value)
                if value != previous_value:
                    unique_values.append(value)
                    previous_value = value
            # Add key only if the list is not empty after cleaning
            if unique_values:
                cleaned_data[key] = unique_values
        # For dictionaries, apply the same cleaning process recursively
        elif isinstance(values, dict):
            cleaned_values = remove_consecutive_duplicates_and_empty_keys(values)
            # Add key only if the dict is not empty after cleaning
            if cleaned_values:
                cleaned_data[key] = cleaned_values
        # For strings, remove non-ASCII characters
        elif isinstance(values, str):
            cleaned_data[key] = remove_non_ascii_characters(values)
        # For other non-empty values, just copy them
        elif values:
            cleaned_data[key] = values
    return cleaned_data

def read_and_clean_json():
    input_file_path = "raw_data/extracted_content4.json"
    output_file_path = "cleaned_documents/cleaned_content.json"
    try:
        with open(input_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        cleaned_data = remove_consecutive_duplicates_and_empty_keys(data)

        # Ensure the output directory exists
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

        with open(output_file_path, 'w', encoding='utf-8') as file:
            json.dump(cleaned_data, file, indent=4)

        print(f"Cleaned data written to {output_file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Call the function
read_and_clean_json()
