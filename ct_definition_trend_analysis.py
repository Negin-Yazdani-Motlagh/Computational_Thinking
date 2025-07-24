import openai
import docx
import pandas as pd
import re
from datetime import datetime

# === SET YOUR API KEY ===
openai.api_key = 'sk-your-api-key'

# === LOAD THE WORD DOC (.docx) ===
def extract_ct_definitions(doc_path):
    doc = docx.Document(doc_path)
    definitions = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if re.search(r'\bcomputational thinking\b', text, re.IGNORECASE) and re.search(r'\[\d+\/\s?W\d+\]', text):
            definitions.append(text)
    return definitions

# === LOAD THE EXCEL SHEET IF AVAILABLE ===
def load_source_metadata(excel_path):
    df = pd.read_excel(excel_path)
    return df

# === CLEAN AND MAP DEFINITIONS TO SOURCE INFO ===
def parse_definition_entry(text):
    match = re.search(r'\[(\d+)\/\s?(W\d+)\]', text)
    if match:
        row_number = int(match.group(1))
        paper_id = match.group(2)
        return {
            "raw_text": text,
            "row_number": row_number,
            "paper_id": paper_id
        }
    return None

# === ANALYZE DEFINITIONS USING OPENAI ===
def analyze_definitions(definitions):
    prompt = "You are an education researcher. Below are multiple definitions of Computational Thinking (CT) from academic papers between 2006 and 2024. Your task is to:\n"
    prompt += "- Identify recurring themes (e.g., abstraction, algorithm, modeling, problem solving)\n"
    prompt += "- Highlight how definitions have evolved over time (if dates are provided)\n"
    prompt += "- Give a short summary of what CT generally means across these definitions\n\n"
    for i, d in enumerate(definitions):
        prompt += f"{i+1}. {d['raw_text']}\n"

    messages = [
        {"role": "system", "content": "You are an expert in educational research and natural language analysis."},
        {"role": "user", "content": prompt}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        temperature=0.4,
        max_tokens=1500
    )
    return response['choices'][0]['message']['content']


# === RUN EVERYTHING ===
def main():
    doc_path = 'Survey_V_3.docx'  # Your Word file
    excel_path = '1. What is CT.xlsx'  # Optional: to map source metadata

    print("Extracting definitions...")
    raw_definitions = extract_ct_definitions(doc_path)
    parsed_definitions = [parse_definition_entry(t) for t in raw_definitions if parse_definition_entry(t)]

    print(f"Total extracted: {len(parsed_definitions)} definitions")

    print("Analyzing with OpenAI...")
    summary = analyze_definitions(parsed_definitions)

    print("\n=== CT DEFINITION ANALYSIS ===")
    print(summary)

if __name__ == "__main__":
    main()
