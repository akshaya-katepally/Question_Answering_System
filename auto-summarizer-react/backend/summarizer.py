from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import pipeline  # Example for summarizer
import pdfplumber  # Enhanced PDF extraction

# Create the Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS

# Initialize the summarizer with a specific BART model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def extract_text_from_pdfs(pdf_files):
    pdf_text = ""
    for pdf_file in pdf_files:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                # Extract text from the page
                pdf_text += page.extract_text()
                
                # Handle tables (if any)
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        pdf_text += " ".join(row) + " "
                
                # Handle images (if needed, for this example, we will skip handling images)
                # You can use page.images to get information about images

    return pdf_text

def chunk_text(text, chunk_size=1000):
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i + chunk_size])
    return chunks

@app.route('/summarizes', methods=['POST'])
def summarize():
    try:
        text_list = request.form.getlist('texts')
        level = request.form.get('summary_level', 'summary')
        
        level_to_percentage = {
            'abstract': 0.10,  # 10% of the input length
            'summary': 0.20,  # 20% of the input length
            'article': 0.30,  # 30% of the input length
        }
        
        percentage = level_to_percentage.get(level, 0.20)
        
        pdf_files = request.files.getlist('pdf_files')
        pdf_text = extract_text_from_pdfs(pdf_files)

        user_text = " ".join(text_list)
        combined_text = user_text + " " + pdf_text

        # Calculate the length of combined text
        input_length = len(combined_text)

        if not combined_text.strip():
            raise ValueError("The combined text is empty. Please provide some text or PDF content.")

        # Determine the min_length and max_length based on the input length and percentage
        target_length = int(input_length * percentage)
        min_length = max(30, target_length // 3)  # Ensure min_length is not too small
        max_length = target_length

        # Chunk the combined text
        chunks = chunk_text(combined_text)
        no_chunks = len(chunks)

        # Summarize each chunk and combine summaries
        summaries = []
        for chunk in chunks:
            # Summarize each chunk individually
            summary = summarizer(chunk, min_length=min_length//no_chunks, max_length=max_length//no_chunks)[0]['summary_text']
            summaries.append(summary)

        # Combine all summaries into final_summary
        final_summary = "\n\n".join(summaries)  # Joining summaries with double newline for paragraph breaks
        print("Final summary:", final_summary)  # Debugging line

        return jsonify({'summary': final_summary, 'no_chunks': no_chunks})

    except Exception as e:
        print(f"Error during summarization: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True,port=5003)
