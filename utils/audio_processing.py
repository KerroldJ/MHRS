import librosa
import os
import numpy as np

def convert_to_wav(input_path, output_path, AudioSegment):
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_frame_rate(44100).set_channels(1)
    audio.export(output_path, format="wav")

def preprocess_audio(filepath):
    y, sr = librosa.load(filepath, sr=44100, mono=True)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    harmonic, percussive = librosa.effects.hpss(y)

    return {
        'tempo': tempo,
        'beats': beats.tolist(),
        'harmonic': harmonic,
        'percussive': percussive,
        'raw_audio': y,
        'sample_rate': sr
    }

def analyze_key_and_pitch(y, sr):
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    chroma_mean = chroma.mean(axis=1)
    key_index = chroma_mean.argmax()
    pitches = librosa.yin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))

    return {
        'estimated_key': key_index,
        'pitches': pitches.tolist()
    }
