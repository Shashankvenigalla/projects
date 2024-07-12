import streamlit as st
import cv2
import numpy as np
from PIL import Image

def create_background(cap, num_frames=30):
    st.write("Capturing Background. Please move out of frame.")
    backgrounds = []
    for i in range(num_frames):
        ret, frame = cap.read()
        if ret:
            backgrounds.append(frame)
        else:
            st.warning(f"Warning: Could not read frame {i+1}/{num_frames}")
        time.sleep(0.1)
    if backgrounds:
        return np.median(backgrounds, axis=0).astype(np.uint8)
    else:
        raise ValueError("Could not capture any frame for background")

def create_mask(frame, lower_color, upper_color):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_color, upper_color)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8), iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, np.ones((3, 3), np.uint8), iterations=4)
    return mask

def apply_cloak_effect(frame, mask, background):
    mask_inv = cv2.bitwise_not(mask)
    fg = cv2.bitwise_and(frame, frame, mask=mask_inv)
    bg = cv2.bitwise_and(background, background, mask=mask)
    return cv2.add(fg, bg)

def main():
    st.title("Cloak Effect with OpenCV and Streamlit")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        st.error("Error: Could not open camera")
        return

    if st.button("Capture Background"):
        try:
            background = create_background(cap)
            st.session_state['background'] = background
            st.write("Background captured successfully!")
        except ValueError as e:
            st.error(f"Error: {e}")

    lower_blue = np.array([90, 50, 50])
    upper_blue = np.array([130, 255, 255])

    if 'background' in st.session_state:
        st.write("Starting cloak effect. Press 'Stop' to quit")
        run_cloak = st.button("Start Cloak Effect")
        stop_cloak = st.button("Stop")

        if run_cloak:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                mask = create_mask(frame, lower_blue, upper_blue)
                output = apply_cloak_effect(frame, mask, st.session_state['background'])
                st.image(output, channels="BGR")
                if stop_cloak:
                    break
        else:
            st.write("Click 'Start Cloak Effect' to start the effect.")

    cap.release()

if __name__ == "__main__":
    main()
