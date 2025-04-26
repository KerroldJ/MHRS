from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
import os
import numpy as np
import librosa
import lameenc
from utils.audio_analysis import analyze_tones
from utils.harmony_recommender import recommend_harmony

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'Uploads')
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'flac', 'ogg'}

# Create the uploads directory if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    instrument = request.form.get('instrument')
    audio_file = request.files.get('audio')

    if not instrument or not audio_file or not allowed_file(audio_file.filename):
        return jsonify({'error': 'Invalid input'}), 400

    filename = secure_filename(audio_file.filename)
    saved_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    audio_file.save(saved_path)

    try:
        tonal_features = analyze_tones(saved_path)
        harmony_data = recommend_harmony(tonal_features, instrument)

        # Combine uploaded audio with synthesized harmony
        combined_audio_path = combine_audio(saved_path, harmony_data['preview_path'], instrument)

        return jsonify({
            'recommended_chords': harmony_data['chords'],
            'chord_progression': harmony_data['progression'],
            'harmony_preview_url': f"/Uploads/{os.path.basename(harmony_data['preview_path'])}",
            'uploaded_audio_url': f'/Uploads/{filename}',
            'combined_audio_url': f'/Uploads/{os.path.basename(combined_audio_path)}'
        })
    except Exception as e:
        print("Error:", e)
        return jsonify({'error': 'Processing failed'}), 500

def combine_audio(uploaded_path, harmony_path, instrument, sample_rate=44100):
    """Combine uploaded audio with synthesized harmony and save as MP3."""
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], f'combined_{instrument}.mp3')
    
    # Load audio files with librosa
    uploaded_audio, sr = librosa.load(uploaded_path, sr=sample_rate, mono=True)
    harmony_audio, _ = librosa.load(harmony_path, sr=sample_rate, mono=True)
    
    # Adjust harmony volume to avoid overpowering
    harmony_audio = harmony_audio * 0.5  # Reduce amplitude by 50%
    
    # Ensure both audios are the same length (trim longer one)
    min_length = min(len(uploaded_audio), len(harmony_audio))
    uploaded_audio = uploaded_audio[:min_length]
    harmony_audio = harmony_audio[:min_length]
    
    # Mix the audios
    combined = uploaded_audio + harmony_audio
    
    # Normalize combined audio
    combined = combined / (np.max(np.abs(combined)) + 1e-6)
    combined = (combined * 32767).astype(np.int16)
    
    # Save as MP3 using lameenc
    encoder = lameenc.Encoder()
    encoder.set_bit_rate(192)
    encoder.set_in_sample_rate(sample_rate)
    encoder.set_channels(1)  # Mono
    encoder.set_quality(5)   # Medium quality
    mp3_data = encoder.encode(combined.tobytes())
    mp3_data += encoder.flush()
    
    with open(output_path, 'wb') as f:
        f.write(mp3_data)
    
    return output_path

@app.route('/Uploads/<path:filename>')
def serve_uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/regenerate-harmony', methods=['POST'])
def regenerate_harmony():
    data = request.json
    features = data.get('features')
    instrument = data.get('instrument')
    harmony = recommend_harmony(features, instrument)
    return jsonify(harmony)

if __name__ == '__main__':
    app.run(debug=True)