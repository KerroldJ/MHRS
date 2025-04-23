import numpy as np
import soundfile as sf
from lameenc import Encoder

def generate_harmony(pitches, key_index, instrument_type):
    harmony = []
    interval = 4 if instrument_type in ["guitar", "ukulele"] else 7
    for pitch in pitches:
        if pitch > 0:
            harmony.append(pitch + interval)
    return harmony

def mix_audio_with_harmony(original_wav_path, harmony_pitches, output_mp3_path):
    # Read original WAV
    audio, sr = sf.read(original_wav_path)
    
    # Simple harmony generator: sine wave overlay
    harmony_wave = np.zeros_like(audio)
    t = np.arange(len(audio)) / sr
    for i, pitch in enumerate(harmony_pitches):
        harmony_wave += 0.1 * np.sin(2 * np.pi * pitch * t)

    # Mix the original audio and harmony (normalize)
    mixed_audio = audio + harmony_wave
    mixed_audio = np.clip(mixed_audio, -1.0, 1.0)

    # Convert to 16-bit PCM
    pcm_audio = (mixed_audio * 32767).astype(np.int16)

    # Encode to MP3 using lameenc
    encoder = Encoder()
    encoder.set_bit_rate(128)
    encoder.set_in_sample_rate(sr)
    encoder.set_channels(1 if pcm_audio.ndim == 1 else pcm_audio.shape[1])
    encoder.set_quality(2)

    mp3_data = encoder.encode(pcm_audio.tobytes())
    mp3_data += encoder.flush()

    # Save MP3
    with open(output_mp3_path, "wb") as f:
        f.write(mp3_data)

    return output_mp3_path

def save_to_mp3(audio_data, sr, output_path):
    # Save as WAV first
    temp_wav_path = output_path.replace('.mp3', '.wav')
    sf.write(temp_wav_path, audio_data, sr)

    # Then convert to MP3 using pydub
    from pydub import AudioSegment
    sound = AudioSegment.from_wav(temp_wav_path)
    sound.export(output_path, format="mp3")
