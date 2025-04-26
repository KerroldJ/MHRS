import numpy as np
from scipy.io import wavfile
import lameenc
import os
from chord_config import CHORD_NOTES, INSTRUMENT_WEIGHTS

def synthesize_chords(chords, instrument, duration_per_chord=2.0, sample_rate=44100):
    import random
    import uuid

    unique_id = uuid.uuid4().hex[:8]
    output_path = os.path.join('static/uploads', f'chord_preview_{instrument}_{unique_id}.mp3')
    total_samples = int(duration_per_chord * sample_rate * len(chords))
    audio = np.zeros(total_samples)
    t = np.linspace(0, duration_per_chord, int(duration_per_chord * sample_rate), False)
    weights = INSTRUMENT_WEIGHTS.get(instrument, [1.0, 0.8, 0.6])

    def envelope(t, duration):
        attack, decay, sustain, release = {
            'acoustic_guitar': (0.02, 0.2, 0.6, 0.2),
            'electric_guitar': (0.01, 0.15, 0.8, 0.1),
            'keyboard': (0.05, 0.1, 0.9, 0.3),
            'ukulele': (0.03, 0.15, 0.7, 0.2),
            'bass': (0.08, 0.2, 0.5, 0.4)
        }.get(instrument, (0.05, 0.1, 0.7, 0.2))

        env = np.ones_like(t)
        env[t < attack] = t[t < attack] / attack
        env[(t >= attack) & (t < attack + decay)] = 1 - (1 - sustain) * ((t[(t >= attack) & (t < attack + decay)] - attack) / decay)
        env[t >= duration - release] *= (1 - (t[t >= duration - release] - (duration - release)) / release)
        return env

    for i, chord in enumerate(chords):
        chord_wave = sum(
            weight * np.sin(2 * np.pi * (freq + random.uniform(-0.5, 0.5)) * t)
            for freq, weight in zip(CHORD_NOTES[chord], weights)
        )
        chord_wave *= envelope(t, duration_per_chord)
        start = i * len(t)
        audio[start:start + len(t)] = chord_wave

    max_val = np.max(np.abs(audio)) + 1e-6
    audio = (audio / max_val * 32767).astype(np.int16)

    encoder = lameenc.Encoder()
    encoder.set_bit_rate(192)
    encoder.set_in_sample_rate(sample_rate)
    encoder.set_channels(1)
    encoder.set_quality(5)
    mp3_data = encoder.encode(audio.tobytes()) + encoder.flush()

    with open(output_path, 'wb') as f:
        f.write(mp3_data)

    return output_path