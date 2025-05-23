from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import numpy as np
import librosa
import lameenc
import uuid
import logging
from audio_analysis import analyze_tones
from recommender import recommend_harmony



app = Flask(__name__)
CORS(app) 
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'Uploads')
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'flac', 'ogg'}

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    """Process uploaded audio and recommend harmony."""
    instrument = request.form.get('instrument')
    audio_file = request.files.get('audio')

    # Validate inputs
    if not instrument or not audio_file or not allowed_file(audio_file.filename):
        logger.error("Invalid input: missing instrument or invalid audio file")
        return jsonify({'error': 'Missing instrument or invalid audio file'}), 400

    # Generate unique filename to avoid overwrites
    filename = f"{uuid.uuid4().hex}_{secure_filename(audio_file.filename)}"
    saved_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    try:
        # Save uploaded file
        audio_file.save(saved_path)
        logger.info(f"Saved uploaded file: {saved_path}")

        # Analyze audio using analyze_tones
        tonal_features = analyze_tones(saved_path)
        if 'error' in tonal_features:
            logger.error(f"Audio analysis failed: {tonal_features['error']}")
            return jsonify({'error': tonal_features['error']}), 500

        # Add uploaded audio path to tonal_features
        tonal_features['uploaded_audio_path'] = saved_path

        # Recommend harmony
        harmony_data = recommend_harmony(tonal_features, instrument)
        if not harmony_data or 'preview_path' not in harmony_data:
            logger.error("Harmony recommendation failed: no preview path returned")
            return jsonify({'error': 'Harmony recommendation failed'}), 500

        # Combine uploaded audio with synthesized harmony
        sample_rate = 44100  # Consistent with analyze_tones
        combined_audio_path = combine_audio(saved_path, harmony_data['preview_path'], instrument, sample_rate)

        # Prepare response
        response = {
            'tonal_features': tonal_features,
            'recommended_chords': harmony_data['chords'],
            'chord_progression': harmony_data['progression'],
            'harmony_preview_url': f"/Uploads/{os.path.basename(harmony_data['preview_path'])}",
            'uploaded_audio_url': f"/Uploads/{filename}",
            'combined_audio_url': f"/Uploads/{os.path.basename(combined_audio_path)}"
        }
        logger.info(f"Recommendation successful for {filename}")
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Processing failed for {filename}: {str(e)}")
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500
    finally:
        # Optionally clean up uploaded file to save space
        if os.path.exists(saved_path):
            try:
                os.remove(saved_path)
                logger.info(f"Cleaned up uploaded file: {saved_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up {saved_path}: {str(e)}")

def combine_audio(uploaded_path, harmony_path, instrument, sample_rate=44100):
    """Combine uploaded audio with synthesized harmony and save as MP3."""
    output_filename = f"combined_{uuid.uuid4().hex}_{instrument}.mp3"
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
    
    try:
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
        encoder.set_channels(1)
        encoder.set_quality(5)   # Medium quality
        mp3_data = encoder.encode(combined.tobytes())
        mp3_data += encoder.flush()
        
        with open(output_path, 'wb') as f:
            f.write(mp3_data)
        
        logger.info(f"Combined audio saved: {output_path}")
        return output_path
    
    except Exception as e:
        logger.error(f"Failed to combine audio: {str(e)}")
        raise

@app.route('/Uploads/<path:filename>')
def serve_uploaded_file(filename):
    """Serve files from the upload folder."""
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except Exception as e:
        logger.error(f"Failed to serve file {filename}: {str(e)}")
        return jsonify({'error': 'File not found'}), 404

@app.route('/regenerate-harmony', methods=['POST'])
def regenerate_harmony():
    """Regenerate harmony based on provided tonal features and instrument."""
    data = request.json
    features = data.get('features')
    instrument = data.get('instrument')

    if not features or not instrument:
        logger.error("Invalid input: missing features or instrument")
        return jsonify({'error': 'Missing features or instrument'}), 400

    try:
        if 'uploaded_audio_path' not in features and 'duration_sec' in features:
            logger.warning("No uploaded_audio_path for regeneration, using duration_sec")
            features['uploaded_audio_path'] = None 
        harmony = recommend_harmony(features, instrument)
        if not harmony or 'preview_path' not in harmony:
            logger.error("Harmony regeneration failed: no preview path returned")
            return jsonify({'error': 'Harmony regeneration failed'}), 500

        response = {
            'recommended_chords': harmony['chords'],
            'chord_progression': harmony['progression'],
            'harmony_preview_url': f"/Uploads/{os.path.basename(harmony['preview_path'])}"
        }
        logger.info("Harmony regeneration successful")
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Harmony regeneration failed: {str(e)}")
        return jsonify({'error': f'Harmony regeneration failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)