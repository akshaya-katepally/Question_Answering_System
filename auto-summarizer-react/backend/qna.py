import os
import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import fitz  # PyMuPDF
from transformers import pipeline, T5Tokenizer, T5ForConditionalGeneration
import textwrap
import random
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
CORS(app)

# Suppress the huggingface_hub symlinks warning
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'

# Pre-load models and tokenizers
logging.info("Loading models and tokenizers...")
question_model_name = "valhalla/t5-base-qg-hl"
qa_model_name = "deepset/roberta-large-squad2"

try:
    question_tokenizer = T5Tokenizer.from_pretrained(question_model_name)
    question_model = T5ForConditionalGeneration.from_pretrained(question_model_name)
    qa_pipeline = pipeline("question-answering", model=qa_model_name)
    logging.info("Models and tokenizers loaded successfully.")
except Exception as e:
    logging.error(f"Error loading models: {str(e)}")
    raise

def extract_text_from_pdf(pdf):
    logging.info("Starting PDF text extraction.")
    try:
        doc = fitz.open(stream=pdf.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        logging.info("Completed PDF text extraction.")
        return text
    except Exception as e:
        logging.error(f"Error during PDF text extraction: {str(e)}")
        raise

def clean_text(text):
    # Add any text cleaning steps if necessary
    return text.replace('\n', ' ')

def generate_questions(text, total_questions=16):
    logging.info("Starting question generation.")
    try:
        wrapped_text = textwrap.wrap(text, width=512)
        questions = []
        for i in range(min(total_questions, len(wrapped_text))):
            input_text = f"generate questions: {wrapped_text[i]}"
            input_ids = question_tokenizer.encode(input_text, return_tensors="pt")
            outputs = question_model.generate(input_ids, max_length=64, num_beams=4, do_sample=False)
            question = question_tokenizer.decode(outputs[0], skip_special_tokens=True)
            questions.append(question)
        logging.info("Completed question generation.")
        return questions
    except Exception as e:
        logging.error(f"Error during question generation: {str(e)}")
        raise

def format_answer(answer):
    if not answer.endswith('.'):
        answer += '.'
    return answer.capitalize()

def answer_questions(questions, context):
    logging.info("Starting question answering.")
    try:
        answers = []
        for question in questions:
            result = qa_pipeline(question=question, context=context)
            formatted_answer = format_answer(result['answer'])
            answers.append({"question": question, "answer": formatted_answer})
        logging.info("Completed question answering.")
        return answers
    except Exception as e:
        logging.error(f"Error during question answering: {str(e)}")
        raise

@app.route('/upload', methods=['POST'])
def upload_file():
    logging.info("File upload request received.")
    try:
        if 'file' not in request.files:
            logging.error("No file part in the request.")
            return jsonify({"error": "No file part"}), 400
        file = request.files['file']
        if file.filename == '':
            logging.error("No selected file.")
            return jsonify({"error": "No selected file"}), 400
        if file:
            text = extract_text_from_pdf(file)
            cleaned_text = clean_text(text)
            
            # Generate questions
            all_questions = generate_questions(cleaned_text)
            
            # Select first question and 5 random questions from the rest
            if len(all_questions) > 1:
                selected_questions = [all_questions[0]] + random.sample(all_questions[1:], min(5, len(all_questions) - 1))
            else:
                selected_questions = all_questions
            
            # Answer selected questions
            answers = answer_questions(selected_questions, cleaned_text)

            logging.info("Question generation and answering completed.")
            return jsonify({"questions": selected_questions, "answers": answers})
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)



















# import os
# import datetime
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import fitz  # PyMuPDF
# from transformers import pipeline
# import textwrap
# import random

# app = Flask(__name__)
# CORS(app)

# # Suppress the huggingface_hub symlinks warning
# os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'

# # Print start message when the application starts
# print(f"{datetime.datetime.now()} - Flask app started.")

# def extract_text_from_pdf(pdf):
#     print(f"{datetime.datetime.now()} - Starting PDF text extraction.")
#     try:
#         doc = fitz.open(stream=pdf.read(), filetype="pdf")
#         text = ""
#         for page in doc:
#             text += page.get_text()
#         print(f"{datetime.datetime.now()} - Completed PDF text extraction.")
#         return text
#     except Exception as e:
#         print(f"{datetime.datetime.now()} - Error during PDF text extraction: {str(e)}")
#         raise

# def generate_questions(text, model_name="valhalla/t5-small-qg-prepend", total_questions=16):
#     try:
#         print(f"{datetime.datetime.now()} - Starting question generation.")
#         nlp = pipeline("text2text-generation", model=model_name, tokenizer="t5-base")
#         wrapped_text = textwrap.wrap(text, width=512)
#         questions = []
#         for i in range(min(total_questions, len(wrapped_text))):
#             question = nlp(f"generate questions: {wrapped_text[i]}", max_length=64, do_sample=False)
#             questions.append(question[0]['generated_text'])
#         print(f"{datetime.datetime.now()} - Completed question generation.")
#         return questions
#     except Exception as e:
#         print(f"{datetime.datetime.now()} - Error during question generation: {str(e)}")
#         raise

# def format_answer(answer):
#     if not answer.endswith('.'):
#         answer += '.'
#     return answer.capitalize()

# def answer_questions(questions, context):
#     try:
#         print(f"{datetime.datetime.now()} - Starting question answering.")
#         qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")
#         answers = []
#         for question in questions:
#             result = qa_pipeline(question=question, context=context)
#             formatted_answer = format_answer(result['answer'])
#             answers.append({"question": question, "answer": formatted_answer})
#         print(f"{datetime.datetime.now()} - Completed question answering.")
#         return answers
#     except Exception as e:
#         print(f"{datetime.datetime.now()} - Error during question answering: {str(e)}")
#         raise

# @app.route('/upload', methods=['POST'])
# def upload_file():
#     try:
#         print(f"{datetime.datetime.now()} - File upload request received.")
#         if 'file' not in request.files:
#             print(f"{datetime.datetime.now()} - No file part in the request.")
#             return jsonify({"error": "No file part"}), 400
#         file = request.files['file']
#         if file.filename == '':
#             print(f"{datetime.datetime.now()} - No selected file.")
#             return jsonify({"error": "No selected file"}), 400
#         if file:
#             text = extract_text_from_pdf(file)
            
#             # Generate questions
#             all_questions = generate_questions(text)
            
#             # Select first question and 5 random questions from the rest
#             if len(all_questions) > 1:
#                 selected_questions = [all_questions[0]] + random.sample(all_questions[1:], min(5, len(all_questions) - 1))
#             else:
#                 selected_questions = all_questions
            
#             # Answer selected questions
#             answers = answer_questions(selected_questions, text)

#             # Print end message when questions are generated and answered
#             print(f"{datetime.datetime.now()} - Question generation ended.")

#             return jsonify({"questions": selected_questions, "answers": answers})
#     except Exception as e:
#         print(f"{datetime.datetime.now()} - Error: {str(e)}")
#         return jsonify({"error": str(e)}), 500

# if __name__ == '__main__':
#     app.run(debug=True)

