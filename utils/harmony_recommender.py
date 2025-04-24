import numpy as np
from scipy.io import wavfile
import lameenc
import os

# Chord definitions (fundamental frequencies in Hz)
CHORD_NOTES = {
    'C': [261.63, 329.63, 392.00],
    'G': [392.00, 493.88, 587.33],
    'F': [349.23, 440.00, 523.25],
    'Am': [261.63, 329.63, 440.00],
    'Em': [329.63, 392.00, 493.88],
    'D': [293.66, 369.99, 440.00]
}

INSTRUMENT_WEIGHTS = {
    'acoustic_guitar': [1.0, 0.8, 0.6],
    'electric_guitar': [1.0, 1.2, 0.9],
    'keyboard': [0.8, 0.8, 0.8],
    'ukulele': [1.0, 0.7, 0.5],
    'bass': [1.2, 0.5, 0.3]
}

PITCH_TO_CHORD = {
    0: 'C', 1: 'C#', 2: 'D', 3: 'D#', 4: 'E', 5: 'F',
    6: 'F#', 7: 'G', 8: 'G#', 9: 'A', 10: 'A#', 11: 'B'
}

DEFAULT_CHORDS = ['C', 'G', 'F']

def get_chords_from_pitches(pitches):
    chord_map = {
        0: 'C', 2: 'D', 4: 'Em', 5: 'F',
        7: 'G', 9: 'Am', 11: 'Em'
    }
    chords = {chord_map.get(p) for p in pitches if chord_map.get(p)}
    return list(chords)

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

def synthesize_chords(chords, instrument, duration_per_chord=2.0, sample_rate=44100):
    output_path = os.path.join('static/uploads', f'chord_preview_{instrument}.mp3')
    total_samples = int(duration_per_chord * sample_rate * len(chords))
    audio = np.zeros(total_samples)
    t = np.linspace(0, duration_per_chord, int(duration_per_chord * sample_rate), False)
    weights = INSTRUMENT_WEIGHTS.get(instrument, [1.0, 0.8, 0.6])

    def envelope(t, duration):
        attack = min(0.1, duration * 0.1)
        decay = min(0.2, duration * 0.2)
        sustain_level = 0.7
        release = min(0.2, duration * 0.2)
        env = np.ones_like(t)
        env[t < attack] = t[t < attack] / attack
        env[(t >= attack) & (t < attack + decay)] = 1 - (1 - sustain_level) * ((t[(t >= attack) & (t < attack + decay)] - attack) / decay)
        env[t >= duration - release] *= (1 - (t[t >= duration - release] - (duration - release)) / release)
        return env

    for i, chord in enumerate(chords):
        chord_wave = sum(
            weight * np.sin(2 * np.pi * freq * t)
            for freq, weight in zip(CHORD_NOTES[chord], weights)
        )
        chord_wave *= envelope(t, duration_per_chord)
        start = i * len(t)
        audio[start:start + len(t)] = chord_wave

    # Normalize
    max_val = np.max(np.abs(audio)) + 1e-6
    audio = (audio / max_val * 32767).astype(np.int16)

    # MP3 encoding
    encoder = lameenc.Encoder()
    encoder.set_bit_rate(192)
    encoder.set_in_sample_rate(sample_rate)
    encoder.set_channels(1)
    encoder.set_quality(5)
    mp3_data = encoder.encode(audio.tobytes()) + encoder.flush()

    with open(output_path, 'wb') as f:
        f.write(mp3_data)

    return output_path
