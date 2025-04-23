import librosa

def analyze_tones(file_path):
    y, sr = librosa.load(file_path)
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
    rms = librosa.feature.rms(y=y)

    return {
        'chroma_mean': chroma.mean(axis=1).tolist(),
        'spectral_centroid_mean': float(spectral_centroid.mean()),
        'rms_energy': float(rms.mean())
    }