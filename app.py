from flask import Flask, request, render_template, jsonify, send_file
from werkzeug.utils import secure_filename
from utils.harmony_generator import HarmonyGenerator
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
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit upload size to 16MB

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

    instrument = request.form.get('instrument', 'sine').lower()
    valid_instruments = {'acoustic_guitar', 'electric_guitar', 'keyboard', 'ukulele', 'bass', 'sine'}
    if instrument not in valid_instruments:
        return jsonify({'error': f"Invalid instrument. Choose from: {', '.join(valid_instruments)}"}), 400

    original_filename = secure_filename(file.filename)
    temp_filename = f"{uuid.uuid4()}_{original_filename}"
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], tempfile.template)
    file.save(input_path)

    try:
        # Initialize HarmonyGenerator and analyze audio
        harmony_gen = HarmonyGenerator(input_path, instrument)
        key, tempo, chords, progression = harmony_gen.analyze_audio()

        # Generate and save combined audio as WAV
        output_filename = f"harmony_{uuid.uuid4()}.wav"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        harmony_gen.combine_audio(output_path)

        # Clean up input file
        cleanup_files(input_path)

        return jsonify({
            'processed_file': output_filename,
            'original_file': original_filename,
            'analysis': {
                'key': key,
                'tempo': tempo,
                'chords': chords,
                'progression': progression
            }
        })

    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}")
        cleanup_files(input_path, output_path)
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
                download_name='harmony_audio.wav',
                mimetype='audio/wav'
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