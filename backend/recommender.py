import numpy as np
import logging
from chord_config import DEFAULT_CHORDS, get_chords_from_pitches
from harmony_generator import synthesize_chords

logger = logging.getLogger(__name__)

def recommend_harmony(features, instrument):
    """Recommend harmony based on tonal features and synthesize a preview."""
    try:
        # Extract chroma and compute dominant pitches
        chroma = np.array(features.get('chroma_mean', []))
        if len(chroma) == 0:
            logger.warning("No chroma_mean in features, using default chords")
            selected_chords = DEFAULT_CHORDS[:3]
        else:
            dominant_pitches = np.argsort(chroma)[-3:]
            selected_chords = get_chords_from_pitches(dominant_pitches)

        # Fallback with default chords
        for chord in DEFAULT_CHORDS:
            if len(selected_chords) >= 3:
                break
            if chord not in selected_chords:
                selected_chords.append(chord)

        # Determine progression style based on brightness
        brightness = features.get('spectral_centroid_mean', 0)
        progression = selected_chords if brightness < 1500 else [selected_chords[0], selected_chords[2], selected_chords[1]]

        # Get duration parameters
        uploaded_audio_path = features.get('uploaded_audio_path')
        duration_sec = features.get('duration_sec')

        # Synthesize chords with matching duration
        preview_path = synthesize_chords(
            chords=progression,
            instrument=instrument,
            uploaded_audio_path=uploaded_audio_path,
            duration_sec=duration_sec
        )

        # Log success
        logger.info(f"Harmony synthesized: {preview_path} for chords {progression} with instrument {instrument}")

        return {
            'chords': selected_chords,
            'progression': ' -> '.join(progression),
            'preview_path': preview_path
        }

    except Exception as e:
        logger.error(f"Failed to recommend harmony: {str(e)}")
        raise RuntimeError(f"Failed to recommend harmony: {str(e)}")