import librosa
import numpy as np

def analyze_tones(file_path):
    try:
        # Load the audio file
        y, sr = librosa.load(file_path, mono=True)
        
        # Extract chroma features
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        
        # Extract spectral features
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
        
        # Extract energy-related features
        rms = librosa.feature.rms(y=y)
        zero_crossing_rate = librosa.feature.zero_crossing_rate(y)
        
        # Estimate tempo
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        
        # Compute duration
        duration = librosa.get_duration(y=y, sr=sr)

        # Return structured analysis
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
        # Return error details if anything goes wrong
        return {'error': str(e)}
