from flask import Flask, request, jsonify, render_template, send_file, send_from_directory
from flask_cors import CORS
from io import BytesIO
import numpy as np
import librosa
import lameenc
import uuid
import logging
import tempfile
import os
import soundfile as sf
import time

from audio_analysis import analyze_tones
from recommender import recommend_harmony

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'flac', 'ogg'}

# Directory to store audio files
AUDIO_DIR = os.path.join(app.root_path, 'static', 'audio')
os.makedirs(AUDIO_DIR, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_audio_to_mp3(audio_data, sample_rate, filename):
    try:
        audio_data = audio_data / (np.max(np.abs(audio_data)) + 1e-6)
        audio_data = (audio_data * 32767).astype(np.int16)

        encoder = lameenc.Encoder()
        encoder.set_bit_rate(192)
        encoder.set_in_sample_rate(sample_rate)
        encoder.set_channels(1)
        encoder.set_quality(5)
        mp3_data = encoder.encode(audio_data.tobytes()) + encoder.flush()

        output_path = os.path.join(AUDIO_DIR, filename)
        with open(output_path, 'wb') as f:
            f.write(mp3_data)

        return output_path
    except Exception as e:
        logger.error(f"Failed to encode MP3: {str(e)}")
        raise

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    instrument = request.form.get('instrument')
    audio_file = request.files.get('audio')

    if not instrument or not audio_file or not allowed_file(audio_file.filename):
        return jsonify({'error': 'Missing instrument or invalid audio file'}), 400

    try:
        audio_data = audio_file.read()
        audio_io = BytesIO(audio_data)

        sample_rate = 44100
        audio_array, sr = librosa.load(audio_io, sr=sample_rate, mono=True)

        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
            sf.write(temp_audio.name, audio_array, sample_rate, format='WAV')
            tonal_features = analyze_tones(temp_audio.name)

        os.unlink(temp_audio.name)

        if 'error' in tonal_features:
            return jsonify({'error': tonal_features['error']}), 500

        tonal_features['duration_sec'] = librosa.get_duration(y=audio_array, sr=sample_rate)

        # Save uploaded audio
        uploaded_audio_id = f"{uuid.uuid4()}.mp3"
        uploaded_audio_path = save_audio_to_mp3(audio_array, sample_rate, uploaded_audio_id)

        harmony_data = recommend_harmony(tonal_features, instrument)
        if not harmony_data or 'preview_path' not in harmony_data:
            return jsonify({'error': 'Harmony recommendation failed'}), 500

        harmony_audio, _ = librosa.load(harmony_data['preview_path'], sr=sample_rate, mono=True)
        os.unlink(harmony_data['preview_path'])

        # Save harmony preview
        harmony_audio_id = f"{uuid.uuid4()}.mp3"
        harmony_audio_path = save_audio_to_mp3(harmony_audio, sample_rate, harmony_audio_id)

        # Combine audios
        harmony_audio = harmony_audio * 0.5
        min_length = min(len(audio_array), len(harmony_audio))
        combined_audio = audio_array[:min_length] + harmony_audio[:min_length]

        combined_audio_id = f"{uuid.uuid4()}.mp3"
        combined_audio_path = save_audio_to_mp3(combined_audio, sample_rate, combined_audio_id)

        return jsonify({
            'tonal_features': tonal_features,
            'recommended_chords': harmony_data['chords'],
            'chord_progression': harmony_data['progression'],
            'harmony_preview_url': f"/static/audio/{harmony_audio_id}",
            'uploaded_audio_url': f"/static/audio/{uploaded_audio_id}",
            'combined_audio_url': f"/static/audio/{combined_audio_id}"
        })

    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

@app.route('/regenerate-harmony', methods=['POST'])
def regenerate_harmony():
    data = request.json
    features = data.get('features')
    instrument = data.get('instrument')

    if not features or not instrument or 'duration_sec' not in features:
        return jsonify({'error': 'Missing features, instrument, or duration'}), 400

    try:
        harmony = recommend_harmony(features, instrument)
        if not harmony or 'preview_path' not in harmony:
            return jsonify({'error': 'Harmony regeneration failed'}), 500

        sample_rate = 44100
        harmony_audio, _ = librosa.load(harmony['preview_path'], sr=sample_rate, mono=True)
        os.unlink(harmony['preview_path'])

        harmony_audio_id = f"{uuid.uuid4()}.mp3"
        save_audio_to_mp3(harmony_audio, sample_rate, harmony_audio_id)

        return jsonify({
            'recommended_chords': harmony['chords'],
            'chord_progression': harmony['progression'],
            'harmony_preview_url': f"/static/audio/{harmony_audio_id}"
        })

    except Exception as e:
        logger.error(f"Harmony regeneration failed: {str(e)}")
        return jsonify({'error': f'Harmony regeneration failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
