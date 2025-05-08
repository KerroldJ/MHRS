import audioread
import lameenc

def convert_audio(input_path, output_path):
    encoder = lameenc.Encoder()
    encoder.set_bit_rate(128)
    encoder.set_in_sample_rate(44100)
    encoder.set_channels(2)
    encoder.set_quality(2)

    with audioread.audio_open(input_path) as f:
        with open(output_path, 'wb') as mp3_file:
            for buf in f:
                mp3_data = encoder.encode(buf)
                if mp3_data:
                    mp3_file.write(mp3_data)
            mp3_file.write(encoder.flush())
