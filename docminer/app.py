from flask import Flask, render_template, request, redirect, url_for, make_response, jsonify
import os
import csv
from io import StringIO
from lib.adapters import AzureOCRAdapter
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# In-memory storage for processed file metadata and OCR keys
file_memory = {}
ocr_keys = []  # Keys to extract
ocr = AzureOCRAdapter()
DATA_DIR = os.path.join(os.getcwd(), "data")  # Directory for storing documents
os.makedirs(DATA_DIR, exist_ok=True)  # Ensure the 'data' folder exists

@app.route('/', methods=['GET'])
def home():
    """Render the homepage with current processed files and keys."""
    return render_template('index.html', file_memory=file_memory, ocr_keys=ocr_keys)

@app.route('/add_key', methods=['POST'])
def add_key():
    """Add a new key to the OCR key list."""
    new_key = request.form.get('new_key')
    if new_key and new_key not in ocr_keys:
        ocr_keys.append(new_key)
        return jsonify({'status': 'success', 'ocr_keys': ocr_keys})
    return jsonify({'status': 'error', 'message': 'Key already exists or invalid'})

@app.route('/delete_key/<key>', methods=['POST'])
def delete_key(key):
    """Remove a key from the OCR key list."""
    if key in ocr_keys:
        ocr_keys.remove(key)
    return jsonify({'status': 'success', 'ocr_keys': ocr_keys})

@app.route('/upload_docs', methods=['POST'])
def upload_docs():
    """Handle file uploads and process them with Azure OCR."""
    uploaded_files = request.files.getlist('file')

    for file in uploaded_files:
        if file.filename:
            file_path = os.path.join(DATA_DIR, file.filename)
            file.save(file_path)  # Save file to the 'data' directory

            file_memory[file.filename] = {}

    return redirect(url_for('home'))

@app.route('/process_docs', methods=['POST'])
def process_docs():
    """Send documents to Azure AI Document Intelligence and return analysis"""
    ocr.set_keys(ocr_keys)
    uploaded_files = request.files.getlist('file')
    
    for filename in file_memory:    
        file_path = os.path.join(DATA_DIR, filename)
        content = ocr.process(file_path)
        file_memory[filename] = content
    print(file_memory)
    return redirect(url_for('home'))

@app.route('/delete_file/<filename>', methods=['POST'])
def delete_file(filename):
    """Delete a specific file from the 'data' directory and in-memory storage."""
    file_path = os.path.join(DATA_DIR, filename)
    if filename in file_memory:
        file_memory.pop(filename, None)  # Remove from in-memory storage
    if os.path.exists(file_path):
        os.remove(file_path)  # Remove file from the data directory
    return redirect(url_for('home'))

@app.route('/delete_all', methods=['POST'])
def delete_all():
    """Delete all files from the 'data' directory and clear in-memory storage."""
    file_memory.clear()  # Clear in-memory storage
    for file in os.listdir(DATA_DIR):
        file_path = os.path.join(DATA_DIR, file)
        if os.path.isfile(file_path):
            os.remove(file_path)  # Remove all files in the data directory
    return redirect(url_for('home'))

@app.route('/combine_all', methods=['GET'])
def combine_all():
    """Generate and serve the CSV file for download."""
    normalized_keys = ocr.required_keys
    si = StringIO()
    csv_writer = csv.writer(si)
    csv_writer.writerow(normalized_keys)  # Header row includes all keys
    print(file_memory)
    for doc_data in file_memory.values():
        for chunk in doc_data: 
            csv_writer.writerow([chunk.get(key, '') for key in normalized_keys])

    # Prepare the CSV response
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=combined.csv"
    output.headers["Content-Type"] = "text/csv"

    return output

if __name__ == '__main__':
    app.run(debug=True)
