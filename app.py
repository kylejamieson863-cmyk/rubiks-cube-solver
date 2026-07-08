import streamlit as st
import cv2
import numpy as np
import kociemba

st.set_page_config(page_title="Real Rubik's Cube Solver", page_icon="🎲", layout="centered")

st.title("🎲 Custom Rubik's Cube Solver")
st.write("Hold the cube with **BLUE facing you** and **WHITE on top** for all scans.")

# Initialize memory storage mapping directly to your cube layout description
if "cube_faces" not in st.session_state:
    st.session_state.cube_faces = {
        "Front (Blue center)": None,
        "Top (White center)": None,
        "Bottom (Yellow center)": None,
        "Right (Orange center)": None,
        "Left (Red center)": None,
        "Back (Green center)": None
    }

# ------------------------------------------------------------------
# COLOR DETECTOR
# ------------------------------------------------------------------
def scan_face_colors(image_bytes, center_color):
    file_bytes = np.asarray(bytearray(image_bytes.read()), dtype=np.uint8)
    opencv_image = cv2.imdecode(file_bytes, 1)
    hsv = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2HSV)
    
    h, w, _ = opencv_image.shape
    grid_colors = []
    
    for row in range(3):
        for col in range(3):
            if row == 1 and col == 1:
                grid_colors.append(center_color)
                continue
                
            cx = int((col + 0.5) * (w / 3))
            cy = int((row + 0.5) * (h / 3))
            
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
# SCANNING INTERFACE
# ------------------------------------------------------------------
st.subheader("📸 Step 1: Scan All 6 Sides")

face_centers = {
    "Front (Blue center)": "B",
    "Top (White center)": "W",
    "Bottom (Yellow center)": "Y",
    "Right (Orange center)": "O",
    "Left (Red center)": "R",
    "Back (Green center)": "G"
}

current_face = st.selectbox("Which side are you scanning right now?", list(st.session_state.cube_faces.keys()))
img_file = st.camera_input(f"Take picture of {current_face}")

if img_file:
    processed_img, detected_colors = scan_face_colors(img_file, face_centers[current_face])
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
# THE SOLVER ACTION
# ------------------------------------------------------------------
st.write("---")
st.subheader("🔮 Step 2: Get Solutions")

if not all_scanned:
    st.info("Please capture all 6 sides using the camera layout above before processing solver steps.")
else:
    if st.button("🚀 Calculate Moves to Solve", type="primary"):
        with st.spinner("Calculating exact mechanical rotation path..."):
            try:
                # Map your custom color structure directly to Kociemba's spatial definitions
                # Kociemba expects: Up, Right, Front, Down, Left, Back
                mapping = {
                    "W": "U", "O": "R", "B": "F", "Y": "D", "R": "L", "G": "B"
                }
                
                raw_str = (
                    st.session_state.cube_faces["Top (White center)"] +
                    st.session_state.cube_faces["Right (Orange center)"] +
                    st.session_state.cube_faces["Front (Blue center)"] +
                    st.session_state.cube_faces["Bottom (Yellow center)"] +
                    st.session_state.cube_faces["Left (Red center)"] +
                    st.session_state.cube_faces["Back (Green center)"]
                )
                
                kociemba_string = "".join([mapping[char] for char in raw_str])
                
                # Run the math solver engine
                sol_raw = kociemba.solve(kociemba_string)
                moves = sol_raw.split()
                
                st.success("🎉 Solution Calculated! Keep BLUE facing you and WHITE on top while turning:")
                st.write("---")
                
                for i, move in enumerate(moves):
                    base_move = move[0]
                    modifier = move[1] if len(move) > 1 else ""
                    
                    # Convert internal Kociemba tokens to human text matching your exact colors
                    face_names = {
                        "U": "TOP (White center)", 
                        "D": "BOTTOM (Yellow center)", 
                        "F": "FRONT (Blue center)", 
                        "B": "BACK (Green center)", 
                        "L": "LEFT (Red center)", 
                        "R": "RIGHT (Orange center)"
                    }
                    target = face_names[base_move]
                    
                    if modifier == "'":
                        explanation = f"Turn the {target} side counter-clockwise 90 degrees."
                    elif modifier == "2":
                        explanation = f"Turn the {target} side completely around twice (180 degrees)."
                    else:
                        explanation = f"Turn the {target} side clockwise 90 degrees."
                    
                    st.markdown(f"### Move {i+1}: &nbsp;&nbsp; `{move}`")
                    st.caption(explanation)
                    st.write("---")
                    
            except Exception as e:
                st.error("Invalid Scanned Configuration Layout! The math says this combination of pieces is physically impossible.")
                st.info("💡 **Troubleshooting Tip:** Ensure that room lighting isn't causing the camera to mistake White squares for Yellow, or Red squares for Orange!")

if st.button("🔄 Clear Camera Memory & Start Over"):
    st.session_state.cube_faces = {k: None for k in st.session_state.cube_faces}
    st.rerun()
