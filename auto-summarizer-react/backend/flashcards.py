from flask import Flask, request, jsonify
import fitz  # PyMuPDF
from transformers import T5Tokenizer, T5ForConditionalGeneration
import nltk
from nltk.tokenize import sent_tokenize
from flask_cors import CORS
from io import BytesIO

app = Flask(__name__)
CORS(app)

# Load the T5 model and tokenizer
tokenizer = T5Tokenizer.from_pretrained("t5-small")
model = T5ForConditionalGeneration.from_pretrained("t5-small")

# Function to extract text from the first page of a PDF
def extract_text_from_first_page(pdf_file):
    document = fitz.open(stream=pdf_file.read(), filetype="pdf")
    first_page = document.load_page(0)
    text = first_page.get_text("text")
    return text

# Function to summarize text
def summarize(text, max_points=5):
    sentences = sent_tokenize(text)
    num_sentences = len(sentences)
    chunk_size = max(1, num_sentences // max_points)  # Ensure at least one sentence per chunk
    chunks = [' '.join(sentences[i:i + chunk_size]) for i in range(0, num_sentences, chunk_size)]

    points = []
    for chunk in chunks:
        input_text = "summarize: " + chunk
        inputs = tokenizer.encode(input_text, return_tensors="pt", max_length=512, truncation=True)
        summary_ids = model.generate(inputs, max_length=50, min_length=10, length_penalty=2.0, num_beams=4, early_stopping=True)
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        points.append(summary)
    
    return points

# Route to handle PDF upload and summarization
@app.route('/uploads', methods=['POST'])
def upload():
    file = request.files['file']
    if file:
        text = extract_text_from_first_page(file)
        nltk.download('punkt')
        summary_points = summarize(text, max_points=10)  # Generate 5-6 points
        return jsonify({'summary': summary_points})
    return jsonify({'error': 'No file uploaded'}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5001)
