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