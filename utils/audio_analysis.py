import librosa
import numpy as np

def analyze_tones(file_path):
    try:
        y, sr = librosa.load(file_path, mono=True)
        
        # Chroma features
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        
        # Spectral features
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
        
        # Energy
        rms = librosa.feature.rms(y=y)
        zero_crossing_rate = librosa.feature.zero_crossing_rate(y)
        
        # Tempo
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        
        # Duration
        duration = librosa.get_duration(y=y, sr=sr)

        return {
            'chroma_mean': chroma.mean(axis=1).tolist(),
            'spectral_centroid_mean': float(spectral_centroid.mean()),
            'spectral_bandwidth_mean': float(spectral_bandwidth.mean()),
            'rms_energy': float(rms.mean()),
            'zero_crossing_rate': float(zero_crossing_rate.mean()),
            'tempo_bpm': float(tempo),
            'duration_sec': float(duration)
        }
    
    except Exception as e:
        return {'error': str(e)}
