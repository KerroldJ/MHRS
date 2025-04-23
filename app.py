from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from pydub import AudioSegment
import os

# Import custom modules
from utils.audio_processing import convert_to_wav, preprocess_audio, analyze_key_and_pitch
from utils.instrument_classifier import extract_tonal_features, classify_instrument
from utils.harmony_generator import generate_harmony, mix_audio_with_harmony

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
CONVERTED_FOLDER = 'converted'
OUTPUT_FOLDER = 'output'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CONVERTED_FOLDER'] = CONVERTED_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/upload-audio', methods=['POST'])
def upload_audio():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = secure_filename(file.filename)
    original_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(original_path)

    # Convert to WAV
    converted_filename = os.path.splitext(filename)[0] + '.wav'
    converted_path = os.path.join(app.config['CONVERTED_FOLDER'], converted_filename)
    convert_to_wav(original_path, converted_path, AudioSegment)

    try:
        preprocessed = preprocess_audio(converted_path)
        analysis = analyze_key_and_pitch(preprocessed['raw_audio'], preprocessed['sample_rate'])
        tonal_features = extract_tonal_features(preprocessed['raw_audio'], preprocessed['sample_rate'])
        instrument = classify_instrument(tonal_features)

        harmony_path = generate_harmony(analysis['pitches'], instrument)
        mixed_output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"mixed_{converted_filename}")
        mix_audio_with_harmony(converted_path, harmony_path, AudioSegment, mixed_output_path)

        return jsonify({
            'message': 'Audio processed successfully',
            'tempo': preprocessed['tempo'],
            'estimated_key_index': analysis['estimated_key'],
            'instrument': instrument,
            'harmony_output': mixed_output_path
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
