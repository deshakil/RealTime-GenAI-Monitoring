from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os
from RuleEngine import extract_text_from_pdf, preprocess_text, store_rules_mongodb, extract_rules, verify_rules

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'WebUploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
       
        text = extract_text_from_pdf(file_path)
        preprocessed_text = preprocess_text(text)
        rules = extract_rules(preprocessed_text)
        verified_rules = verify_rules(rules)
        store_rules_mongodb(verified_rules)
        
        return jsonify({"message": "File processed and rules stored"}), 200

if __name__ == '__main__':
    app.run(debug=True)

