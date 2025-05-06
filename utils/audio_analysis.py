import librosa
import numpy as np
import logging
import traceback
import os
import tempfile
from pydub import AudioSegment

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Log to console
        logging.FileHandler('audio_analysis_errors.log')  # Log to file
    ]
)

def convert_m4a_to_wav(input_path):
    """Convert M4A file to WAV using pydub."""
    try:
        # Create a temporary WAV file
        temp_wav = os.path.join(tempfile.gettempdir(), f"temp_{os.path.basename(input_path)}.wav")
        
        # Load M4A and export as WAV
        audio = AudioSegment.from_file(input_path, format="m4a")
        audio.export(temp_wav, format="wav")
        
        logging.info(f"Converted {input_path} to temporary WAV: {temp_wav}")
        return temp_wav
    except Exception as e:
        error_msg = f"Failed to convert {input_path} to WAV: {str(e)}"
        logging.error(error_msg)
        raise ValueError(error_msg)

def analyze_tones(file_path):
    temp_wav = None
    try:
        # Check if file exists and is accessible
        if not os.path.exists(file_path):
            error_msg = f"Audio file not found: {file_path}"
            logging.error(error_msg)
            raise FileNotFoundError(error_msg)

        # Check if file is WAV, MP3, or M4A
        if not file_path.lower().endswith(('.wav', '.mp3', '.m4a')):
            error_msg = "Unsupported file format. Only WAV, MP3, and M4A are supported."
            logging.error(error_msg)
            raise ValueError(error_msg)
        
        # Convert M4A to WAV if necessary
        if file_path.lower().endswith('.m4a'):
            temp_wav = convert_m4a_to_wav(file_path)
            audio_file = temp_wav
        else:
            audio_file = file_path
        
        logging.info(f"Attempting to load audio file: {audio_file}")

        # Load audio file
        try:
            y, sr = librosa.load(audio_file, mono=True)
        except Exception as e:
            error_msg = f"Failed to load {audio_file}: {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)
        
        if len(y) == 0:
            error_msg = "Audio file is empty or could not be loaded"
            logging.error(error_msg)
            raise ValueError(error_msg)
        
        logging.info(f"Successfully loaded audio file: {audio_file}, sample rate: {sr}")

        # Chroma features
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        if chroma.size == 0:
            raise ValueError("Chroma features could not be computed")

        # Spectral features
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
        if spectral_centroid.size == 0:
            raise ValueError("Spectral centroid could not be computed")
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
        if spectral_bandwidth.size == 0:
            raise ValueError("Spectral bandwidth could not be computed")

        # Energy
        rms = librosa.feature.rms(y=y)
        if rms.size == 0:
            raise ValueError("RMS energy could not be computed")
        zero_crossing_rate = librosa.feature.zero_crossing_rate(y)
        if zero_crossing_rate.size == 0:
            raise ValueError("Zero crossing rate could not be computed")

        # Tempo
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        if tempo is None:
            raise ValueError("Tempo could not be estimated")

        # Duration
        duration = librosa.get_duration(y=y, sr=sr)
        if duration <= 0:
            raise ValueError("Invalid duration computed")

        logging.info(f"Successfully analyzed audio file: {audio_file}")

        return {
            'chroma_mean': chroma.mean(axis=1).tolist(),
            'spectral_centroid_mean': float(spectral_centroid.mean()),
            'spectral_bandwidth_mean': float(spectral_bandwidth.mean()),
            'rms_energy': float(rms.mean()),
            'zero_crossing_rate': float(zero_crossing_rate.mean()),
            'tempo_bpm': float(tempo),
            'duration_sec': float(duration)
        }

    except Exception as e:
        # Log the error with full stack trace
        error_msg = f"Failed to analyze audio file {file_path}: {str(e)}\n{traceback.format_exc()}"
        logging.error(error_msg)
        return {
            'error': f"Failed to analyze {file_path}: {str(e)}",
            'stack_trace': traceback.format_exc()
        }
    finally:
        # Clean up temporary WAV file
        if temp_wav and os.path.exists(temp_wav):
            try:
                os.remove(temp_wav)
                logging.info(f"Cleaned up temporary WAV: {temp_wav}")
            except Exception as e:
                logging.error(f"Failed to delete temporary WAV {temp_wav}: {str(e)}")