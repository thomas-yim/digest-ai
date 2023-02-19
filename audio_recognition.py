from moviepy.editor import VideoFileClip
from pydub import AudioSegment
import os
from google.cloud import speech
import shutil

MAX_LEN = 50

def onlyAudio(filename):
    client = speech.SpeechClient()

    with open(filename, "rb") as audio_file:
        content = audio_file.read()
        print(type(content))
    audio_file.close()

    audio = AudioSegment.from_wav(filename)
    print(type(audio.raw_data))

    length = int(len(audio)/1000)

    output = ""
    config = speech.RecognitionConfig(
        audio_channel_count=2,
        language_code="en-US",
        enable_automatic_punctuation=True,
    )
        
    for i in range(int(length/MAX_LEN)+1):
        curEnd = min(length, (i+1)*MAX_LEN)
        print(f"{(i*MAX_LEN)} to {curEnd}")
        curSegment = audio[(i*MAX_LEN)*1000:(curEnd)*1000]
        curSegment.export("tmp.wav", format="WAV")
        with open("tmp.wav", "rb") as temp_segment:
            segment_content = temp_segment.read()

        curAudio = speech.RecognitionAudio(content=segment_content)
        response = client.recognize(request={"config": config, "audio": curAudio})
        for res in response.results:
            output += res.alternatives[0].transcript
    
    print(output)
    


def transcribe(filename, client):
    with open(filename, "rb") as audio_file:
        content = audio_file.read()
        audio = speech.RecognitionAudio(content=content)

    config = speech.RecognitionConfig(
        audio_channel_count=2,
        language_code="en-US",
        enable_automatic_punctuation=True,
    )

    response = client.recognize(request={"config": config, "audio": audio})

    output = ""
    for res in response.results:
        output += res.alternatives[0].transcript
    return output



# Assume the first value is 0
def audio_split(start_times, filename):
    filename_split = filename.split(".")
    name = filename_split[0]
    audio = AudioSegment.from_wav(filename)
    if os.path.exists(f"{name}_audio"):
        shutil.rmtree(f"{name}_audio")
    os.mkdir(f"{name}_audio")
    for i in range(len(start_times)-1):
        # Add a half-second buffer on each side
        start = start_times[i]-0.5
        end = start_times[i+1]+0.5
        length = end - start
        for j in range(int(length/MAX_LEN)+1):
            curEnd = min(end, start + (j+1)*MAX_LEN)
            curSegment = audio[(start+(j*MAX_LEN))*1000:(curEnd)*1000]
            curSegment.export(f"{name}_audio/part_{i}_{j}.wav", format="WAV")
    
    curSegment = audio[(start_times[-1]-1)*1000:]
    curSegment.export(f"{name}_audio/part_{len(start_times)-1}.wav", format="WAV")

def extract_audio(video_file):
    filename_split = video_file.split(".")
    file = filename_split[0]
    clip = VideoFileClip(video_file)
    clip.audio.write_audiofile(f"{file}.wav", codec='pcm_s16le')

if __name__ == "__main__":
    audiofile = "semantics.wav"
    onlyAudio(audiofile)
    

