import soundfile as sf
import numpy as np
from scipy.io import wavfile

def convert_to_wav(input_path, output_path):
    try:
        data, samplerate = sf.read(input_path)
        if data.dtype != 'int16':
            data = np.int16(data * 32767)
        wavfile.write(output_path, samplerate, data)
    except Exception as e:
        raise RuntimeError(f"Error converting to WAV: {str(e)}")
