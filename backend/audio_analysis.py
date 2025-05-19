import numpy as np
import librosa
import logging
import os

logger = logging.getLogger(__name__)

class AudioAnalyzer:
    def __init__(self, audio: np.ndarray, sr: int):
        self.audio = audio
        self.sr = sr
        self.key = None
        self.tempo = None
        self.chords = None
        self.progression = None

    def analyze_audio(self) -> tuple[str, float, list[str], str]:
        """Analyze the input audio to detect key, tempo, chords, and progression."""
        try:
            tempo, _ = librosa.beat.beat_track(y=self.audio, sr=self.sr)
            self.tempo = float(tempo)  # Ensure tempo is a float for JSON serialization

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
            
            logger.info(f"Audio analysis completed: key={self.key}, tempo={self.tempo}, chords={self.chords}")
            return self.key, self.tempo, self.chords, self.progression
        except Exception as e:
            logger.error(f"Error analyzing audio: {str(e)}")
            raise RuntimeError(f"Error analyzing audio: {str(e)}")

    def analyze_tones(self) -> dict:
        """Analyze tonal and spectral features of the input audio."""
        try:
            # Extract chroma features
            chroma = librosa.feature.chroma_stft(y=self.audio, sr=self.sr)
            
            # Extract spectral features
            spectral_centroid = librosa.feature.spectral_centroid(y=self.audio, sr=self.sr)
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=self.audio, sr=self.sr)
            
            # Extract energy-related features
            rms = librosa.feature.rms(y=self.audio)
            zero_crossing_rate = librosa.feature.zero_crossing_rate(y=self.audio)
            
            # Estimate tempo (reuse in analyze_audio if needed)
            tempo, _ = librosa.beat.beat_track(y=self.audio, sr=self.sr)
            self.tempo = float(tempo)
            
            # Compute duration
            duration = librosa.get_duration(y=self.audio, sr=self.sr)

            # Return structured analysis
            result = {
                'chroma_mean': chroma.mean(axis=1).tolist(),
                'spectral_centroid_mean': float(spectral_centroid.mean()),
                'spectral_bandwidth_mean': float(spectral_bandwidth.mean()),
                'rms_energy': float(rms.mean()),
                'zero_crossing_rate': float(zero_crossing_rate.mean()),
                'tempo_bpm': float(tempo),
                'duration_sec': float(duration)
            }
            
            logger.info(f"Tone analysis completed: {result}")
            return result
        
        except Exception as e:
            logger.error(f"Error analyzing tones: {str(e)}")
            return {'error': str(e)}

def analyze_tones(file_path: str) -> dict:
    """Analyze tonal and spectral features of an audio file, including key, chords, and progression."""
    try:
        # Validate file existence and extension
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return {'error': f"File not found: {file_path}"}
        if not file_path.lower().endswith(('.wav', '.mp3', '.flac', '.ogg')):
            logger.error(f"Unsupported file format: {file_path}")
            return {'error': f"Unsupported file format: {file_path}"}

        # Load audio
        logger.info(f"Loading audio file: {file_path}")
        y, sr = librosa.load(file_path, mono=True)
        
        # Initialize AudioAnalyzer
        analyzer = AudioAnalyzer(audio=y, sr=sr)
        
        # Perform tonal analysis
        tone_result = analyzer.analyze_tones()
        
        # If tone analysis failed, return early
        if 'error' in tone_result:
            return tone_result
        
        # Perform audio analysis for key, chords, and progression
        try:
            key, tempo, chords, progression = analyzer.analyze_audio()
            tone_result.update({
                'key': key,
                'chords': chords,
                'chord_progression': progression
            })
        except RuntimeError as e:
            logger.warning(f"Skipping key/chord analysis due to error: {str(e)}")
            # Continue with tone results even if key/chord analysis fails
        
        logger.info(f"Analysis completed for {file_path}: {tone_result}")
        return tone_result
    
    except Exception as e:
        logger.error(f"Error processing audio file {file_path}: {str(e)}")
        return {'error': str(e)}