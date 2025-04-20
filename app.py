from flask import Flask, request, render_template, send_file
import os
import librosa
import numpy as np
import soundfile as sf
import lameenc
from tempfile import NamedTemporaryFile

app = Flask(__name__)
UPLOAD_FOLDER = 'Uploads'
OUTPUT_FOLDER = 'output'
SAMPLE_FOLDER = 'samples'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    file = request.files['audio']
    instrument = request.form['instrument']

    # Save uploaded MP3 file
    mp3_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(mp3_path)

    try:
        # Load MP3 directly with librosa (avoids pydub's ffmpeg dependency)
        y, sr = librosa.load(mp3_path, sr=None)

        # Extract beat
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)

        # Harmony chord sequence: C, F, G, repeat
        chord_sequence = ['C', 'F', 'G', 'C'] * ((len(beats) // 4) + 1)

        # Create harmony audio manually (silence array)
        harmony_signal = np.zeros_like(y)

        for i, beat in enumerate(beats[:len(chord_sequence)]):
            beat_sample = librosa.frames_to_samples(beat)
            duration_samples = int(0.5 * sr)  # 0.5 sec chord length
            t = np.linspace(0, 0.5, duration_samples)

            # Generate simple sine tones for harmony chords
            chord = chord_sequence[i]
            if chord == 'C':
                freqs = [261.63, 329.63, 392.00]  # C major: C-E-G
            elif chord == 'F':
                freqs = [349.23, 440.00, 523.25]  # F major: F-A-C
            elif chord == 'G':
                freqs = [392.00, 493.88, 587.33]  # G major: G-B-D
            else:
                freqs = [261.63]

            chord_wave = sum(np.sin(2 * np.pi * f * t) for f in freqs) / len(freqs)

            # Normalize and add to harmony
            chord_wave = chord_wave * 0.3  # lower volume
            start = beat_sample
            end = min(len(harmony_signal), start + len(chord_wave))
            harmony_signal[start:end] += chord_wave[:end - start]

        # Mix harmony with original
        mixed_signal = y + harmony_signal
        mixed_signal = mixed_signal / np.max(np.abs(mixed_signal))  # normalize

        # Save temporary WAV file for MP3 encoding
        with NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
            sf.write(temp_wav.name, mixed_signal, sr)
            temp_wav_path = temp_wav.name

        # Convert WAV to MP3 using lameenc
        try:
            wav_data, _ = sf.read(temp_wav_path)
            if wav_data.ndim > 1:
                wav_data = wav_data[:, 0]  # Convert to mono if stereo

            # Scale to 16-bit PCM
            wav_data = (wav_data * 32767).astype(np.int16)

            # Encode to MP3
            encoder = lameenc.Encoder()
            encoder.set_bit_rate(192)  # 192 kbps
            encoder.set_in_sample_rate(sr)
            encoder.set_channels(1)  # Mono
            encoder.set_quality(5)  # Medium quality

            mp3_data = encoder.encode(wav_data.tobytes())
            mp3_data += encoder.flush()

            # Save MP3 file
            output_mp3_path = os.path.join(OUTPUT_FOLDER, 'final_output.mp3')
            with open(output_mp3_path, 'wb') as f:
                f.write(mp3_data)
        except Exception as e:
            print(f"WAV to MP3 conversion failed: {e}")
            os.remove(temp_wav_path)
            return "Error: Unable to convert WAV to MP3", 500

        os.remove(temp_wav_path)  # Clean up temporary WAV
        return send_file(output_mp3_path, as_attachment=True)

    except Exception as e:
        print(f"Processing failed: {e}")
        return "Error: Audio processing failed", 500

if __name__ == '__main__':
    app.run(debug=True)