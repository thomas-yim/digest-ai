import cv2

# Load the video
video = cv2.VideoCapture("history.mp4")

# Get the total number of frames
total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

# Set the initial frame
_, prev_frame = video.read()
prev_frame = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)

# Set the start time
start_time = 0

# Loop through all the frames
for i in range(1, total_frames):
    # Read the current frame
    _, curr_frame = video.read()
    curr_frame = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)

    # Calculate the absolute difference between the current frame and the previous frame
    diff = cv2.absdiff(prev_frame, curr_frame)

    # Threshold the difference to create a binary image
    _, diff = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

    # Calculate the number of white pixels in the binary image
    white_pixels = cv2.countNonZero(diff)

    # Check if the number of white pixels exceeds a certain threshold
    if white_pixels > 100000:
        # Print the timestamp when the slide changes
        print("Slide changed at", start_time + i / video.get(cv2.CAP_PROP_FPS), "seconds")

    # Set the current frame as the previous frame for the next iteration
    prev_frame = curr_frame

# Release the video
video.release()