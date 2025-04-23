from flask import Flask, request, jsonify, send_file, render_template
from werkzeug.utils import secure_filename
import os

from utils.audio_conversion import convert_to_wav
from utils.audio_analysis import preprocess_audio, analyze_key_and_pitch
from utils.harmony_generation import synthesize_harmony

app = Flask(__name__)

# Directories
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
OUTPUT_FOLDER = 'output'

for folder in [UPLOAD_FOLDER, PROCESSED_FOLDER, OUTPUT_FOLDER]:
    os.makedirs(folder, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload-audio', methods=['POST'])
def upload_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    instrument = request.form.get('instrument')
    file = request.files['audio']
    filename = secure_filename(file.filename)

    if not filename:
        return jsonify({'error': 'Empty filename'}), 400

    input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(input_path)

    wav_path = os.path.join(app.config['PROCESSED_FOLDER'], f"{os.path.splitext(filename)[0]}.wav")
    convert_to_wav(input_path, wav_path)

    try:
        # Step 1: Analyze audio
        audio_info = preprocess_audio(wav_path)
        pitch_data = analyze_key_and_pitch(audio_info['raw_audio'], audio_info['sample_rate'])

        # Step 2: Generate synthetic harmony
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], 'harmonized_output.wav')
        synthesize_harmony(audio_info['raw_audio'], audio_info['sample_rate'], pitch_data['pitches'], instrument, output_path)

        return send_file(output_path, as_attachment=True, download_name='harmonized_audio.wav')

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
