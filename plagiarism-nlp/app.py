from flask import Flask, request, jsonify
from flask_cors import CORS
from detect import detect_plagiarism
import uuid

app = Flask(__name__)
CORS(app)

@app.route('/api/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file uploaded"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"status": "error", "message": "Empty filename"}), 400

    # Read the text from the file
    text = file.read().decode('utf-8', errors='ignore')
    
    # Run plagiarism detection
    result = detect_plagiarism(text)
    
    # Add extra info to result
    submission_id = str(uuid.uuid4())[:8]
    result['submission_id'] = submission_id
    result['filename'] = file.filename

    return jsonify(result)


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "running"})


if __name__ == '__main__':
    app.run(debug=True, port=5000)