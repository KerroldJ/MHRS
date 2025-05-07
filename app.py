from flask import Flask, request, send_file, render_template, jsonify
from werkzeug.utils import secure_filename
from utils.harmony_generator import HarmonyGenerator
import os
import tempfile
import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
app.config['ALLOWED_EXTENSIONS'] = {'mp3', 'm4a'}

def allowed_file(filename: str) -> bool:
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['audio']
    instrument = request.form.get('instrument')
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'Only MP3 and M4A files are allowed'}), 400
    if not instrument or instrument.lower() not in ['acoustic_guitar', 'electric_guitar', 'keyboard', 'ukulele', 'bass']:
        return jsonify({'error': 'Invalid instrument selected'}), 400
    
    # Save uploaded file temporarily
    filename = secure_filename(file.filename)
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}_{filename}")
    file.save(input_path)
    
    try:
        # Process audio directly (assumes HarmonyGenerator supports MP3/M4A)
        generator = HarmonyGenerator(input_path, instrument)
        key, tempo, chords, progression = generator.analyze_audio()
        output_filename = f"harmonized_{uuid.uuid4()}.mp3"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        generator.combine_audio(output_path)
        
        # Clean up input file
        os.remove(input_path)
        
        return jsonify({
            'chords': chords,
            'progression': progression,
            'harmony_file': output_filename,
            'uploaded_file': filename
        })
    except Exception as e:
        os.remove(input_path) if os.path.exists(input_path) else None
        return jsonify({'error': f'Error processing audio: {str(e)}'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_file(
            file_path,
            as_attachment=True,
            download_name='harmonized_audio.mp3',
            mimetype='audio/mp3'
        )
    return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
