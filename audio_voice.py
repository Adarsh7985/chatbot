from pydub import AudioSegment

def convert_mp3_to_wav(mp3_file, wav_file):
    # Load MP3 file
    audio = AudioSegment.from_mp3(mp3_file)

    # Export as WAV
    audio.export(wav_file, format="wav")

# Example usage
mp3_file = ""
wav_file = "converted-audio-file.wav"
convert_mp3_to_wav(mp3_file, wav_file)