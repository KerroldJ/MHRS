import numpy as np
import soundfile as sf
import librosa

def synthesize_harmony(y, sr, pitches, instrument, output_path):
    interval_map = {
        "piano": 7,
        "guitar": 4,
        "ukulele": 3,
        "bass": -12,
        "electric_guitar": 5,
        "acoustic_guitar": 4
    }

    interval = interval_map.get(instrument.lower(), 7)

    # Apply pitch shifting to synthesize harmony
    harmony = librosa.effects.pitch_shift(y=y, sr=sr, n_steps=interval)

    # Match lengths before mixing
    min_len = min(len(y), len(harmony))
    mixed = (y[:min_len] + harmony[:min_len]) / 2.0

    # Normalize and save to file
    mixed = np.int16(mixed / np.max(np.abs(mixed)) * 32767)
    sf.write(output_path, mixed, sr)
