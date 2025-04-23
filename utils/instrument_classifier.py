# instrument_classifier.py
import numpy as np
import librosa

def extract_tonal_features(audio, sr):
    # Basic tonal features: MFCCs, chroma, spectral centroid
    mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
    chroma = librosa.feature.chroma_stft(y=audio, sr=sr)
    spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sr)

    # Aggregate features (mean)
    features = np.concatenate([
        np.mean(mfccs, axis=1),
        np.mean(chroma, axis=1),
        np.mean(spectral_centroid, axis=1)
    ])

    return features

def classify_instrument(features):
    # Dummy rule-based classification
    if features[0] > 0 and features[10] < 0:
        return "acoustic guitar"
    elif features[0] < -50:
        return "bass"
    elif features[5] > 5:
        return "keyboard"
    else:
        return "piano"
