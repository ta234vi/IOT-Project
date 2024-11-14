import torch
import cv2
import serial
import time
import warnings

# Suppress FutureWarning related to torch.cuda.amp.autocast
warnings.filterwarnings("ignore", category=FutureWarning)

# Load the YOLOv5 model (pre-trained)
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')

# Open the laptop camera (or external camera)
cap = cv2.VideoCapture(0)  # Use 0 for laptop camera, or replace with video file

# Open serial communication with Arduino (adjust COM port accordingly)
arduino = serial.Serial('COM5', 9600, timeout=1)  # Adjust COM2 to your system's port
time.sleep(2)  # Give time for Arduino to reset

# Get the frame dimensions
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Define the regions based on the width of the frame (split into 3 regions)
left_region = frame_width // 3  # Left third
right_region = 2 * frame_width // 3  # Right third

# Start capturing the video stream
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    if not ret:
        break

    # Perform detection using the YOLOv5 model
    results = model(frame)

    # Initialize detection flags for the three regions
    left_detected = False
    middle_detected = False
    right_detected = False

    # Loop through detections and determine which region the student is in
    for *xyxy, conf, cls in results.xyxy[0]:
        if int(cls) == 0:  # Class 0 corresponds to 'person' in YOLOv5
            # Calculate the center of the bounding box (midpoint between x1 and x2)
            x_center = (xyxy[0] + xyxy[2]) / 2  # x_center is the horizontal midpoint

            # Determine which region the person is in based on x_center
            if x_center < left_region:  # Person is in the left region
                left_detected = True
            elif left_region <= x_center < right_region:  # Person is in the middle region
                middle_detected = True
            elif x_center >= right_region:  # Person is in the right region
                right_detected = True

    # Send the detected region info to Arduino
    regions = ''
    if left_detected:
        regions += 'L'  # Left region detected
    if middle_detected:
        regions += 'M'  # Middle region detected
    if right_detected:
        regions += 'R'  # Right region detected

    print(regions)

    if regions:
        # Clear any leftover data in the receive buffer before sending
        arduino.flushInput()

        arduino.write(regions.encode())  # Send the combined regions (e.g., "LMR")
    else:
        arduino.write(b'0')  # Send '0' if no person is detected
        print("Sent: 0 (No detection)")

    # Try to read response from Arduino (optional, for debugging)
    # if arduino.in_waiting > 0:
    #     arduino_response = arduino.readline().decode('utf-8').strip()
    #     print(f"Arduino response: {arduino_response}")

    # Draw dividing lines between the regions
    cv2.line(frame, (left_region, 0), (left_region, frame_height), (0, 255, 0), 2)
    cv2.line(frame, (right_region, 0), (right_region, frame_height), (0, 255, 0), 2)

    # Display which region has a student detected
    if left_detected:
        cv2.putText(frame, "Student in Left Region", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    if middle_detected:
        cv2.putText(frame, "Student in Middle Region", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    if right_detected:
        cv2.putText(frame, "Student in Right Region", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    # Render the results on the frame
    frame = results.render()[0]

    # Display the frame with region divisions
    cv2.imshow('Student Detection by Region', frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture when done
cap.release()
cv2.destroyAllWindows()
arduino.close()