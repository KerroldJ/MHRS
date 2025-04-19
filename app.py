from flask import Flask, render_template, request, send_file
import librosa
import soundfile as sf
import os
from io import BytesIO
from werkzeug.utils import secure_filename
from pydub import AudioSegment
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_harmony', methods=['POST'])
def generate_harmony():
    if 'audio_file' not in request.files:
        return "No file uploaded", 400

    file = request.files['audio_file']
    interval = int(request.form.get("interval", 4))

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    y, sr = librosa.load(filepath, sr=None)

    # Generate harmony
    harmony = librosa.effects.pitch_shift(y, sr=sr, n_steps=interval)
    combined = y + harmony
    combined = combined / max(abs(combined))  # Normalize

    # Save WAV temporarily
    wav_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}.wav")
    sf.write(wav_path, combined, sr)

    # Convert to MP3 using pydub
    sound = AudioSegment.from_wav(wav_path)
    mp3_io = BytesIO()
    sound.export(mp3_io, format="mp3")
    mp3_io.seek(0)

    os.remove(wav_path)

    return send_file(mp3_io, mimetype='audio/mpeg', as_attachment=True, download_name='harmony.mp3')

if __name__ == '__main__':
    app.run(debug=True)
