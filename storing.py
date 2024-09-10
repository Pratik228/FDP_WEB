import cv2
import os

# Get the USN of the student from the user
usn = input("Enter the USN of the student: ")
# Create the "photos" folder if it does not exist
if not os.path.exists("Images"):
    os.makedirs("Images")
# Initialize the webcam
cap = cv2.VideoCapture(0)

# Take a single photo
while True:
    # Capture a frame from the webcam
    ret, frame = cap.read()

    # Display the frame
    cv2.imshow("Webcam", frame)

    # Check if the user pressed 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # Check if the user clicked the left mouse button
    if cv2.waitKey(1) & 0xFF == ord(' '):  # Space bar is ASCII 32
        # Save the photo as "USN.jpg" in the "photos" folder
        file_name = f"Images/{usn}.jpg"
        cv2.imwrite(file_name, frame)
        print(f"Saved photo as {file_name}")
        break

# Release the webcam
cap.release()

# Destroy all windows
cv2.destroyAllWindows()


