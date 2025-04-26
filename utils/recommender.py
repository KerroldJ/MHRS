import numpy as np
from chord_config import DEFAULT_CHORDS, get_chords_from_pitches
from utils.harmony_generator import synthesize_chords

def recommend_harmony(features, instrument):
    chroma = np.array(features['chroma_mean'])
    dominant_pitches = np.argsort(chroma)[-3:]
    selected_chords = get_chords_from_pitches(dominant_pitches)

    # Fallback with default chords
    for chord in DEFAULT_CHORDS:
        if len(selected_chords) >= 3:
            break
        if chord not in selected_chords:
            selected_chords.append(chord)

    # Determine progression style
    brightness = features['spectral_centroid_mean']
    progression = selected_chords if brightness < 1500 else [selected_chords[0], selected_chords[2], selected_chords[1]]

    preview_path = synthesize_chords(progression, instrument)
    return {
        'chords': selected_chords,
        'progression': progression,
        'preview_path': preview_path
    }