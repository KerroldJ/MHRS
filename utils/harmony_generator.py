import librosa
import numpy as np
import scipy.signal as signal
import scipy.io.wavfile as wavfile
import ffmpeg
from typing import Tuple, List
import os
import tempfile
import uuid

class HarmonyGenerator:
    def __init__(self, input_audio_path: str, instrument: str, sample_rate: int = 44100):
        """Initialize the Harmony Generator with input audio and instrument choice."""
        self.input_audio_path = input_audio_path
        self.instrument = instrument.lower()
        self.sample_rate = sample_rate
        try:
            self.audio, self.sr = librosa.load(input_audio_path, sr=sample_rate, mono=True)
        except Exception as e:
            raise ValueError(f"Failed to load audio file: {str(e)}")
        self.key = None
        self.tempo = None
        self.harmony = None
        self.chords = []
        self.progression = ""

    def analyze_audio(self) -> Tuple[str, float, List[str], str]:
        """Analyze the input audio to detect key, tempo, chords, and progression."""
        tempo, _ = librosa.beat.beat_track(y=self.audio, sr=self.sr)
        self.tempo = tempo

        chroma = librosa.feature.chroma_cqt(y=self.audio, sr=self.sr)
        chroma_mean = np.mean(chroma, axis=1)
        key_idx = np.argmax(chroma_mean)
        keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        self.key = keys[key_idx]

        # Generate simple I-IV-V-I chord progression
        chord_map = {
            'C': ['C', 'F', 'G', 'C'], 'C#': ['C#', 'F#', 'G#', 'C#'],
            'D': ['D', 'G', 'A', 'D'], 'D#': ['D#', 'G#', 'A#', 'D#'],
            'E': ['E', 'A', 'B', 'E'], 'F': ['F', 'A#', 'C', 'F'],
            'F#': ['F#', 'B', 'C#', 'F#'], 'G': ['G', 'C', 'D', 'G'],
            'G#': ['G#', 'C#', 'D#', 'G#'], 'A': ['A', 'D', 'E', 'A'],
            'A#': ['A#', 'D#', 'F', 'A#'], 'B': ['B', 'E', 'F#', 'B']
        }
        self.chords = chord_map[self.key]
        self.progression = ' -> '.join(self.chords)
        
        return self.key, self.tempo, self.chords, self.progression

    def generate_harmony_notes(self) -> List[Tuple[float, float]]:
        """Generate harmony notes based on the detected key and tempo."""
        note_freqs = {
            'C': 261.63, 'C#': 277.18, 'D': 293.66, 'D#': 311.13, 'E': 329.63,
            'F': 349.23, 'F#': 369.99, 'G': 392.00, 'G#': 415.30, 'A': 440.00,
            'A#': 466.16, 'B': 493.88
        }
        
        key_idx = [k for k, v in enumerate(['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']) if v == self.key][0]
        chord_notes = [
            [self.key],  # I chord
            [list(note_freqs.keys())[(key_idx + 5) % 12]],  # IV chord
            [list(note_freqs.keys())[(key_idx + 7) % 12]],  # V chord
            [self.key]   # I chord
        ]
        
        beat_duration = 60 / self.tempo
        harmony_notes = []
        for i in range(4):
            start_time = i * beat_duration
            note = chord_notes[i % len(chord_notes)][0]
            freq = note_freqs[note]
            harmony_notes.append((freq, start_time))
        
        return harmony_notes

    def synthesize_instrument(self, freq: float, duration: float) -> np.ndarray:
        """Synthesize a note for the chosen instrument."""
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        
        if self.instrument == 'acoustic_guitar':
            wave = signal.sawtooth(2 * np.pi * freq * t)
            envelope = np.exp(-t * 4)
            wave *= envelope
        elif self.instrument == 'electric_guitar':
            wave = signal.square(2 * np.pi * freq * t)
            envelope = np.exp(-t * 2)
            wave *= envelope
        elif self.instrument == 'keyboard':
            wave = 0.7 * np.sin(2 * np.pi * freq * t)
            wave += 0.2 * np.sin(2 * np.pi * 2 * freq * t)
            wave += 0.1 * np.sin(2 * np.pi * 3 * freq * t)
        elif self.instrument == 'ukulele':
            wave = np.sin(2 * np.pi * freq * t)
            envelope = np.exp(-t * 5)
            wave *= envelope
        elif self.instrument == 'bass':
            wave = np.sin(2 * np.pi * freq * t)
            envelope = np.exp(-t * 1.5)
            wave += 0.3 * np.sin(2 * np.pi * 0.5 * freq * t)
            wave *= envelope
        else:
            wave = np.sin(2 * np.pi * freq * t)
        
        attack = 0.1
        decay = 0.2
        sustain = 0.7
        release = 0.1
        envelope = np.ones_like(t)
        attack_samples = int(attack * self.sample_rate)
        decay_samples = int(decay * self.sample_rate)
        release_samples = int(release * self.sample_rate)
        
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        envelope[attack_samples:attack_samples + decay_samples] = np.linspace(1, sustain, decay_samples)
        envelope[-release_samples:] = np.linspace(sustain, 0, release_samples)
        
        return wave * envelope

    def generate_harmony(self) -> np.ndarray:
        """Generate the harmony audio track."""
        harmony_notes = self.generate_harmony_notes()
        harmony_length = len(self.audio) / self.sample_rate
        harmony_audio = np.zeros(int(self.sample_rate * harmony_length))
        
        for freq, start_time in harmony_notes:
            duration = 60 / self.tempo
            if start_time + duration > harmony_length:
                duration = harmony_length - start_time
            note = self.synthesize_instrument(freq, duration)
            start_sample = int(start_time * self.sample_rate)
            end_sample = start_sample + len(note)
            harmony_audio[start_sample:end_sample] += note[:end_sample - start_sample]
        
        harmony_audio /= np.max(np.abs(harmony_audio)) + 1e-10
        return harmony_audio

    def combine_audio(self, output_path: str):
        """Combine the original audio with the generated harmony and save as MP3."""
        self.harmony = self.generate_harmony()
        if len(self.harmony) < len(self.audio):
            self.harmony = np.pad(self.harmony, (0, len(self.audio) - len(self.harmony)))
        elif len(self.harmony) > len(self.audio):
            self.harmony = self.harmony[:len(self.audio)]
        
        mixed_audio = 0.5 * self.audio + 0.5 * self.harmony
        mixed_audio /= np.max(np.abs(mixed_audio)) + 1e-10
        
        # Save as WAV temporarily
        temp_wav = os.path.join(tempfile.gettempdir(), f"temp_{uuid.uuid4()}.wav")
        wavfile.write(temp_wav, self.sample_rate, mixed_audio.astype(np.float32))
        
        # Convert WAV to MP3 using ffmpeg-python
        try:
            stream = ffmpeg.input(temp_wav)
            stream = ffmpeg.output(stream, output_path, format='mp3', acodec='mp3', ar=self.sample_rate)
            ffmpeg.run(stream, overwrite_output=True)
        except ffmpeg.Error as e:
            raise RuntimeError(f"Failed to convert WAV to MP3: {str(e)}")
        finally:
            # Clean up temporary WAV file
            if os.path.exists(temp_wav):
                os.remove(temp_wav)