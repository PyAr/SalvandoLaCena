# Helper script to reverse a song
from pydub import AudioSegment


def reverse_song(original_file, reversed_file):
    """Reverse a song."""
    loop = AudioSegment.from_wav(wavefile_name)
    reversed_loop = loop.reverse()
    reversed_loop.export(wavefile_name_reverse, format='wav')


if __name__ == "__main__":
    wavefile_name = 'music/music.wav'
    wavefile_name_reverse = 'music/music_reversed.wav'
    reverse_song(wavefile_name, wavefile_name_reverse)
