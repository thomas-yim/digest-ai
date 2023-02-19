import cv2
from pytesseract import pytesseract
from nltk.corpus import words
import re
import os
from google.cloud import speech
from audio_recognition import audio_split, transcribe, extract_audio

# Assume minimum of 3 seconds between each slide transition
TIME_BETWEEN = 3

def getTextAndTimes(filename):
    # Load the video
    video = cv2.VideoCapture(filename)

    # Get the total number of frames
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    # Get the frame rate
    fps = video.get(cv2.CAP_PROP_FPS)

    # Set the initial frame
    _, prev_frame = video.read()
    prev_frame = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)

    print(f"The number of frames per second is: {fps}")

    # This array keeps track of the first frame of the slide
    transition_starts = [0]
    allText = [pytesseract.image_to_string(prev_frame)]

    num_seconds = int(total_frames//int(fps))

    height = video.get(cv2.CAP_PROP_FRAME_HEIGHT)
    width = video.get(cv2.CAP_PROP_FRAME_WIDTH)

    for i in range(num_seconds-TIME_BETWEEN):
        # Advance the video by a second.
        for j in range(int(fps)-1):
            video.read()

        # Read the current frame
        ret, curr_frame = video.read()

        # Convert the frame from Color to grayscale
        curr_frame = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)

        # Calculate the absolute difference between the current frame and the previous frame
        diff = cv2.absdiff(prev_frame, curr_frame)

        # Threshold the difference to create a binary image
        _, diff = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

        # Calculate the number of white pixels in the binary image
        white_pixels = cv2.countNonZero(diff)

        # Check if the number of white pixels exceeds a certain threshold
        if white_pixels > height*width/100:
            # Assume at least three seconds between each slide
            if i-transition_starts[-1] > TIME_BETWEEN:
                slide_text = pytesseract.image_to_string(curr_frame)
                
                if len(allText) == 1 or allText[-1] == "" or not re.sub('[\n ]+', '', slide_text).startswith(re.sub('[\n ]+', '', allText[-1])):
                    transition_starts.append(i)
                    video.set(cv2.CAP_PROP_POS_FRAMES, video.get(cv2.CAP_PROP_POS_FRAMES)-int(fps*1.5))
                    _, second_ago_frame = video.read()
                    video.set(cv2.CAP_PROP_POS_FRAMES, video.get(cv2.CAP_PROP_POS_FRAMES)+int(fps*1.5)-1)
                    cur_text = pytesseract.image_to_string(second_ago_frame)
                    allText.append(re.sub('\n+', '\n', cur_text))
                    print(f"Slide changed at {i+1} seconds")

        # Set the current frame as the previous frame for the next iteration
        prev_frame = curr_frame
        
    video.release()
    
    return allText, transition_starts

# File must be an mp4
def processSlides(filename):
    name = filename.split('.')[0]
    text, transition_starts = getTextAndTimes(filename)

    print(transition_starts)
    print(text)
    
    extract_audio(filename)

    audio_file = f"{name}.wav"
    audio_split(transition_starts, audio_file)

    output = []
    client = speech.SpeechClient()
    for i in range(len(text)):
        print(f"Part {i}")
        segment = 0
        audio_transcription = ""
        while True:
            if os.path.exists(f"{name}_audio/part_{i}_{segment}.wav"):
                audio_transcription += transcribe(f"{name}_audio/part_{i}_{segment}.wav", client)
                segment += 1
            else:
                break
        output.append((text[i], audio_transcription))
    
    return output

if __name__ == "__main__":

    filename = "history.mp4"

    output = processSlides(filename)
    
    for slide_text, audio_text in output:
        print("Slide Text:")
        print(slide_text)
        print("Audio Text:")
        print(audio_text)


    

