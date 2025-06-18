from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime

app = Flask(__name__)
# Enable CORS for all routes to solve the CORS issue
CORS(app, resources={r"/*": {"origins": "*"}})

# Create upload directory if it doesn't exist
UPLOAD_FOLDER = 'audio_uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/upload', methods=['POST', 'OPTIONS'])
def upload_audio():
    # Handle preflight CORS requests
    if request.method == 'OPTIONS':
        return '', 204
    
    # Check if the post request has the file part
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file in request'}), 400
    
    audio_file = request.files['audio']
    
    # If the user does not select a file, the browser submits an empty file
    if audio_file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        # Generate a unique filename using timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recording_{timestamp}.wav"
        
        # Save the file
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        audio_file.save(file_path)
        
        return jsonify({
            'message': 'File uploaded successfully',
            'filename': filename,
            'path': file_path
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error saving file: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Add a test endpoint to verify the server is running
@app.route('/', methods=['GET'])
def test():
    return jsonify({'status': 'Server is running'}), 200

if __name__ == '__main__':
    # Running the app on port 5000
    app.run(debug=True, port=5000, host='0.0.0.0')