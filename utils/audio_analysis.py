import librosa

def preprocess_audio(filepath):
    y, sr = librosa.load(filepath, sr=44100, mono=True)
    return {
        'raw_audio': y,
        'sample_rate': sr
    }

def analyze_key_and_pitch(y, sr):
    pitches = librosa.yin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    key_index = chroma.mean(axis=1).argmax()
    return {
        'estimated_key': key_index,
        'pitches': pitches.tolist()
    }
