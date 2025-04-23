import numpy as np
from scipy.io import wavfile
import lameenc
import os

# Chord definitions (frequencies in Hz for major and minor chords)
CHORD_NOTES = {
    'C': [261.63, 329.63, 392.00],  # C Major: C4, E4, G4
    'G': [392.00, 493.88, 587.33],  # G Major: G4, B4, D5
    'F': [349.23, 440.00, 523.25],  # F Major: F4, A4, C5
    'Am': [261.63, 329.63, 440.00], # A Minor: A4, C4, E4
    'Em': [329.63, 392.00, 493.88], # E Minor: E4, G4, B4
    'D': [293.66, 369.99, 440.00]   # D Major: D4, F#4, A4
}

# Instrument timbre adjustments (simplified amplitude weights for synthesis)
INSTRUMENT_WEIGHTS = {
    'acoustic_guitar': [1.0, 0.8, 0.6],  # Emphasize fundamental
    'electric_guitar': [1.0, 1.2, 0.9],  # Brighter overtones
    'keyboard': [0.8, 0.8, 0.8],         # Balanced
    'ukulele': [1.0, 0.7, 0.5],          # Softer overtones
    'bass': [1.2, 0.5, 0.3]              # Emphasize lower frequencies
}

def recommend_harmony(features, instrument):
    # Analyze chroma to detect dominant pitch classes
    chroma = np.array(features['chroma_mean'])
    dominant_pitches = np.argsort(chroma)[-3:]  # Top 3 pitch classes

    # Map pitch classes to chords (simplified)
    pitch_to_chord = {
        0: 'C', 1: 'C#', 2: 'D', 3: 'D#', 4: 'E', 5: 'F',
        6: 'F#', 7: 'G', 8: 'G#', 9: 'A', 10: 'A#', 11: 'B'
    }
    
    # Select chords based on dominant pitches and instrument
    selected_chords = []
    for pitch in dominant_pitches:
        if pitch in [0, 5, 7, 9]:  # C, F, G, A
            selected_chords.append('C' if pitch == 0 else 'F' if pitch == 5 else 'G' if pitch == 7 else 'Am')
        elif pitch in [2, 4, 11]:  # D, E, B
            selected_chords.append('D' if pitch == 2 else 'Em')

    # Remove duplicates and ensure at least 3 chords
    selected_chords = list(set(selected_chords))
    default_chords = ['C', 'G', 'F']
    # Extend with default chords if needed
    while len(selected_chords) < 3:
        for chord in default_chords:
            if chord not in selected_chords:
                selected_chords.append(chord)
                break
    
    # Generate a simple chord progression (e.g., I-IV-V or ii-V-I)
    brightness = features['spectral_centroid_mean']
    if brightness < 1500:  # Darker tone, use minor progression
        progression = [selected_chords[0], selected_chords[1], selected_chords[2]]
    else:  # Brighter tone, use major progression
        progression = [selected_chords[0], selected_chords[2], selected_chords[1]]

    # Synthesize chord preview
    preview_path = synthesize_chords(progression, instrument)
    
    return {
        'chords': selected_chords,
        'progression': progression,
        'preview_path': preview_path
    }

def synthesize_chords(chords, instrument, duration_per_chord=2.0, sample_rate=44100):
    """Synthesize a sequence of chords for the given instrument and save as MP3."""
    output_path = os.path.join('Uploads', f'chord_preview_{instrument}.mp3')
    
    # Initialize empty audio
    total_samples = int(duration_per_chord * sample_rate * len(chords))
    audio = np.zeros(total_samples)
    t = np.linspace(0, duration_per_chord, int(duration_per_chord * sample_rate), False)
    
    # Instrument-specific weights
    weights = INSTRUMENT_WEIGHTS.get(instrument, [1.0, 0.8, 0.6])
    
    # Generate each chord
    for i, chord in enumerate(chords):
        chord_samples = np.zeros_like(t)
        for freq, weight in zip(CHORD_NOTES[chord], weights):
            # Simple sine wave synthesis with instrument timbre
            chord_samples += weight * np.sin(2 * np.pi * freq * t)
        # Apply envelope to avoid clicks
        envelope = np.exp(-4 * t / duration_per_chord)
        chord_samples *= envelope
        # Place in output audio
        start = i * len(t)
        audio[start:start + len(t)] = chord_samples
    
    # Normalize audio
    audio = audio / (np.max(np.abs(audio)) + 1e-6)
    audio = (audio * 32767).astype(np.int16)
    
    # Save as MP3 using lameenc
    encoder = lameenc.Encoder()
    encoder.set_bit_rate(192)
    encoder.set_in_sample_rate(sample_rate)
    encoder.set_channels(1)  # Mono for simplicity
    encoder.set_quality(5)   # Medium quality
    mp3_data = encoder.encode(audio.tobytes())
    mp3_data += encoder.flush()
    
    with open(output_path, 'wb') as f:
        f.write(mp3_data)
    
    return output_path