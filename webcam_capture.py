import streamlit as st
import base64
from io import BytesIO
import cv2
import numpy as np

def webcam_capture():
    st.write("Please allow the browser to access the camera.")
    st.write("When you are ready to take a photo, press the 'Capture' button below.")

    # Create a button to capture the photo
    capture_button = st.button("Capture")

    if capture_button:
        # Load JavaScript code to access the webcam and capture the photo
        js_code = """
            async function getWebcamImage() {
                const video = document.createElement('video');
                video.style.display = 'none';
                document.body.appendChild(video);
                await new Promise((resolve) => video.onloadedmetadata = resolve);
                const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                video.srcObject = stream;
                await video.play();
                const canvas = document.createElement('canvas');
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                canvas.getContext('2d').drawImage(video, 0, 0);
                stream.getVideoTracks()[0].stop();
                video.remove();
                return canvas.toDataURL('image/jpeg', 0.8);
            }
            getWebcamImage();
        """

        # Get the captured image from JavaScript
        image_data_url = st.markdown(js_code, unsafe_allow_html=True)

        # Convert the Data URL to an OpenCV image (BGR format)
        img_data = base64.b64decode(image_data_url.split(',')[1])
        img_np_arr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(img_np_arr, cv2.IMREAD_COLOR)

        return img
