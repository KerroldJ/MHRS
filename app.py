from flask import Flask, request, render_template, jsonify, send_file
from werkzeug.utils import secure_filename
from utils.convert_to_mp3 import convert_audio
from utils.audio_analysis import analyze_tones
import os
import tempfile
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
app.config['ALLOWED_EXTENSIONS'] = {'wav', 'mp3', 'm4a'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 

def allowed_file(filename: str) -> bool:
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def cleanup_files(*file_paths):
    """Remove temporary files if they exist."""
    for path in file_paths:
        try:
            if path and os.path.exists(path):
                os.remove(path)
                logger.info(f"Removed temporary file: {path}")
        except Exception as e:
            logger.error(f"Error removing file {path}: {str(e)}")

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['audio']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Only WAV, MP3, or M4A files are allowed'}), 400

    original_filename = secure_filename(file.filename)
    file_ext = original_filename.rsplit('.', 1)[1].lower()
    temp_filename = f"{uuid.uuid4()}_{original_filename}"
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)

    try:
        file.save(input_path)

        if file_ext in ['wav', 'mp3']:
            processed_file_path = input_path
            converted_filename = temp_filename
        else:
            output_filename = f"converted_{uuid.uuid4()}.mp3"
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
            convert_audio(input_path, output_path)
            cleanup_files(input_path)
            processed_file_path = output_path
            converted_filename = output_filename
            
            
        analysis_result = analyze_tones(processed_file_path)

        response = {
            'processed_file': converted_filename,
            'original_file': original_filename,
            'analysis': analysis_result
        }

        return jsonify(response)

    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}")
        cleanup_files(input_path, processed_file_path)
        return jsonify({'error': f'Error processing audio: {str(e)}'}), 500

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    """Serve the processed audio file for download."""
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        if os.path.exists(file_path):
            response = send_file(
                file_path,
                as_attachment=True,
                download_name='converted_audio.mp3',
                mimetype='audio/mpeg'
            )
            # Schedule cleanup after sending file
            cleanup_files(file_path)
            return response
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        logger.error(f"Error downloading file {filename}: {str(e)}")
        cleanup_files(file_path)
        return jsonify({'error': 'Error downloading file'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)