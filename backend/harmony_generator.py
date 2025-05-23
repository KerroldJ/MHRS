import numpy as np
from scipy.io import wavfile
import lameenc
import os
import librosa
import random
import uuid
import logging
from chord_config import CHORD_NOTES, INSTRUMENT_WEIGHTS

logger = logging.getLogger(__name__)

def synthesize_chords(chords, instrument, uploaded_audio_path=None, duration_sec=None, sample_rate=44100):
    """Synthesize chords to match the duration of the uploaded audio or specified duration and save as MP3."""
    # Generate unique output filename
    unique_id = uuid.uuid4().hex[:8]
    output_path = os.path.join('static', 'Uploads', f'chord_preview_{instrument}_{unique_id}.mp3')

    try:
        # Determine total duration
        if uploaded_audio_path:
            uploaded_audio, sr = librosa.load(uploaded_audio_path, sr=sample_rate, mono=True)
            total_duration = librosa.get_duration(y=uploaded_audio, sr=sr)
            logger.info(f"Using duration {total_duration}s from uploaded audio: {uploaded_audio_path}")
        elif duration_sec is not None:
            total_duration = float(duration_sec)
            logger.info(f"Using specified duration: {total_duration}s")
        else:
            raise ValueError("Either uploaded_audio_path or duration_sec must be provided")
        
        # Calculate duration per chord to match total duration
        if not chords:
            raise ValueError("No chords provided")
        duration_per_chord = total_duration / len(chords)
        
        # Calculate total samples based on duration
        total_samples = int(total_duration * sample_rate)
        audio = np.zeros(total_samples)
        
        # Generate time array for each chord
        samples_per_chord = int(duration_per_chord * sample_rate)
        t = np.linspace(0, duration_per_chord, samples_per_chord, False)
        
        # Get instrument weights
        weights = INSTRUMENT_WEIGHTS.get(instrument, [1.0, 0.8, 0.6])

        def envelope(t, duration):
            """Generate ADSR envelope for the given instrument."""
            attack, decay, sustain, release = {
                'acoustic_guitar': (0.02, 0.2, 0.6, 0.2),
                'electric_guitar': (0.01, 0.15, 0.8, 0.1),
                'keyboard': (0.05, 0.1, 0.9, 0.3),
                'ukulele': (0.03, 0.15, 0.7, 0.2),
                'bass': (0.08, 0.2, 0.5, 0.4)
            }.get(instrument, (0.05, 0.1, 0.7, 0.2))

            env = np.ones_like(t)
            env[t < attack] = t[t < attack] / attack
            env[(t >= attack) & (t < attack + decay)] = 1 - (1 - sustain) * (
                (t[(t >= attack) & (t < attack + decay)] - attack) / decay
            )
            env[t >= duration - release] *= (1 - (t[t >= duration - release] - (duration - release)) / release)
            return env

        # Synthesize each chord
        for i, chord in enumerate(chords):
            if chord not in CHORD_NOTES:
                raise ValueError(f"Invalid chord: {chord}")
            chord_wave = sum(
                weight * np.sin(2 * np.pi * (freq + random.uniform(-0.5, 0.5)) * t)
                for freq, weight in zip(CHORD_NOTES[chord], weights)
            )
            chord_wave *= envelope(t, duration_per_chord)
            start = i * samples_per_chord
            end = start + samples_per_chord
            audio[start:end] = chord_wave

        # Normalize audio
        max_val = np.max(np.abs(audio)) + 1e-6
        audio = (audio / max_val * 32767).astype(np.int16)

        # Encode to MP3
        encoder = lameenc.Encoder()
        encoder.set_bit_rate(192)
        encoder.set_in_sample_rate(sample_rate)
        encoder.set_channels(1)  # Mono
        encoder.set_quality(5)  # Medium quality
        mp3_data = encoder.encode(audio.tobytes()) + encoder.flush()

        # Save MP3 file
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(mp3_data)

        logger.info(f"Synthesized chords saved to: {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Failed to synthesize chords: {str(e)}")
        raise RuntimeError(f"Failed to synthesize chords: {str(e)}")