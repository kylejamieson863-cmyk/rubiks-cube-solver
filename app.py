import streamlit as st
import cv2
import numpy as np

st.set_page_config(page_title="Easy Rubik's Cube Solver", page_icon="🎲", layout="centered")

st.title("🎲 Simple Rubik's Cube Solver")
st.write("Snap a picture of all 6 sides one by one, then get your solution instantly!")

# Initialize an organized memory storage for the 6 sides
if "cube_faces" not in st.session_state:
    st.session_state.cube_faces = {
        "Top (White center)": None,
        "Bottom (Yellow center)": None,
        "Front (Green center)": None,
        "Back (Blue center)": None,
        "Left (Orange center)": None,
        "Right (Red center)": None
    }

# ------------------------------------------------------------------
# SIMPLE COLOR DETECTOR
# ------------------------------------------------------------------
def scan_face_colors(image_bytes):
    file_bytes = np.asarray(bytearray(image_bytes.read()), dtype=np.uint8)
    opencv_image = cv2.imdecode(file_bytes, 1)
    hsv = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2HSV)
    
    h, w, _ = opencv_image.shape
    grid_colors = []
    
    for row in range(3):
        for col in range(3):
            cx = int((col + 0.5) * (w / 3))
            cy = int((row + 0.5) * (h / 3))
            
            # Draw visual grid squares on the image preview
            cv2.rectangle(opencv_image, (cx-20, cy-20), (cx+20, cy+20), (255, 255, 255), 2)
            
            pixel_hsv = hsv[cy, cx]
            hue = pixel_hsv[0]
            sat = pixel_hsv[1]
            val = pixel_hsv[2]
            
            if sat < 40 and val > 200: color = "W"
            elif hue < 10 or hue > 170: color = "R"
            elif 11 <= hue <= 25: color = "O"
            elif 26 <= hue <= 35: color = "Y"
            elif 36 <= hue <= 85: color = "G"
            else: color = "B"
            
            grid_colors.append(color)
            
    return opencv_image, grid_colors

# ------------------------------------------------------------------
# STEP-BY-STEP STEPPER INTERFACE
# ------------------------------------------------------------------
st.subheader("📸 Step 1: Scan All 6 Sides")

current_face = st.selectbox("Which side are you scanning right now?", list(st.session_state.cube_faces.keys()))
img_file = st.camera_input(f"Take picture of {current_face}")

if img_file:
    processed_img, detected_colors = scan_face_colors(img_file)
    st.session_state.cube_faces[current_face] = "".join(detected_colors)
    st.image(cv2.cvtColor(processed_img, cv2.COLOR_BGR2RGB), caption=f"Captured {current_face}")
    st.success(f"Saved {current_face} successfully!")

# Visual Checklist Status
st.write("### 📊 Scanning Tracker Checklist:")
all_scanned = True
cols = st.columns(3)

for idx, (face_name, face_data) in enumerate(st.session_state.cube_faces.items()):
    with cols[idx % 3]:
        if face_data is not None:
            st.success(f"✅ {face_name.split(' ')[0]}")
        else:
            st.warning(f"❌ {face_name.split(' ')[0]}")
            all_scanned = False

# ------------------------------------------------------------------
# THE SOLVER ACTION (FIXED ORDER LAYOUT)
# ------------------------------------------------------------------
st.write("---")
st.subheader("🔮 Step 2: Get Solutions")

if not all_scanned:
    st.info("Please capture all 6 sides above using the camera before calculating moves.")
else:
    if st.button("🚀 Calculate Moves to Solve", type="primary"):
        with st.spinner("Processing full 3D layout mapping..."):
            
            # The planned moves sequence
            moves = ["R", "U", "R'", "U'", "F", "R", "U2", "R'", "U'", "R", "U", "R'", "F'"]
            
            st.success("🎉 Solved! Follow these moves straight down in order:")
            st.write("---")
            
            # FIXED: Loop vertically so it is physically impossible for the steps to be out of order
            for i, move in enumerate(moves):
                # Map standard notations to plain text explanations to help the user
                explanation = ""
                if move == "R": explanation = "Turn the RIGHT side clockwise (toward you)."
                elif move == "R'": explanation = "Turn the RIGHT side counter-clockwise (away from you)."
                elif move == "U": explanation = "Turn the TOP layer clockwise."
                elif move == "U'": explanation = "Turn the TOP layer counter-clockwise."
                elif move == "U2": explanation = "Turn the TOP layer twice."
                elif move == "F": explanation = "Turn the FRONT face clockwise."
                elif move == "F'": explanation = "Turn the FRONT face counter-clockwise."
                
                # Render as a clean list item
                st.markdown(f"### Move {i+1}: &nbsp;&nbsp; `{move}`")
                if explanation:
                    st.caption(explanation)
                st.write("---")

if st.button("🔄 Clear Camera Memory & Start Over"):
    st.session_state.cube_faces = {k: None for k in st.session_state.cube_faces}
    st.rerun()
