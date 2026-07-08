import streamlit as st
import cv2
import numpy as np
import kociemba

st.set_page_config(page_title="Real Rubik's Cube Solver", page_icon="🎲", layout="centered")

st.title("🎲 Custom Rubik's Cube Solver")
st.write("Snap each face, verify the colors on the grid, and tweak any errors before solving!")

# Initialize state tracker
if "cube_faces" not in st.session_state:
    st.session_state.cube_faces = {
        "Top (White center)": ["W"] * 9,
        "Bottom (Yellow center)": ["Y"] * 9,
        "Front (Blue center)": ["B"] * 9,
        "Back (Green center)": ["G"] * 9,
        "Left (Red center)": ["R"] * 9,
        "Right (Orange center)": ["O"] * 9
    }

# Map face center labels to internal color codes
face_centers = {
    "Top (White center)": "W",
    "Bottom (Yellow center)": "Y",
    "Front (Blue center)": "B",
    "Back (Green center)": "G",
    "Left (Red center)": "R",
    "Right (Orange center)": "O"
}

# Color palette styling dictionary
color_styles = {
    "W": "⬜ White", "Y": "🟨 Yellow", "G": "🟩 Green", 
    "B": "🟦 Blue", "O": "🟧 Orange", "R": "🟥 Red"
}

# ------------------------------------------------------------------
# STEP 1: SCAN & VERIFY INDIVIDUAL FACES
# ------------------------------------------------------------------
st.subheader("📸 Step 1: Scan and Verify Your Cube Sides")
current_face = st.selectbox("Which side are you scanning right now?", list(st.session_state.cube_faces.keys()))

img_file = st.camera_input(f"Take a picture of the {current_face} face")

# Computer Vision Color Fallback Processing
if img_file:
    file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, w, _ = img.shape
    scanned_colors = []
    
    for row in range(3):
        for col in range(3):
            if row == 1 and col == 1:
                scanned_colors.append(face_centers[current_face])
                continue
            cx = int((col + 0.5) * (w / 3))
            cy = int((row + 0.5) * (h / 3))
            pixel = hsv[cy, cx]
            hue, sat, val = pixel[0], pixel[1], pixel[2]
            
            if sat < 40 and val > 200: color = "W"
            elif hue < 10 or hue > 170: color = "R"
            elif 11 <= hue <= 25: color = "O"
            elif 26 <= hue <= 35: color = "Y"
            elif 36 <= hue <= 85: color = "G"
            else: color = "B"
            scanned_colors.append(color)
            
    st.session_state.cube_faces[current_face] = scanned_colors
    st.toast(f"Captured layout for {current_face}!")

# INTERACTIVE GRID OVERRIDE - Fix any wrong colors right here manually
st.write(f"### 🛠️ Verify & Correct the **{current_face}** Grid Layout:")
st.caption("If the camera guessed a square wrong because of room lighting, change it below:")

face_grid = st.session_state.cube_faces[current_face]

# Draw the 3x3 layout selector block
idx = 0
for row in range(3):
    cols = st.columns(3)
    for col in range(3):
        with cols[col]:
            if row == 1 and col == 1:
                st.write(f"**Center**\n\n{color_styles[face_centers[current_face]]}")
            else:
                current_val = face_grid[idx]
                selected_val = st.selectbox(
                    f"Pos {idx+1}", 
                    options=list(color_styles.keys()), 
                    format_func=lambda x: color_styles[x],
                    index=list(color_styles.keys()).index(current_val),
                    key=f"edit_{current_face}_{idx}"
                )
                st.session_state.cube_faces[current_face][idx] = selected_val
        idx += 1

# ------------------------------------------------------------------
# STEP 2: MATHEMATICAL FULL CUBE SOLVER
# ------------------------------------------------------------------
st.write("---")
st.subheader("🔮 Step 2: Calculate Your Solution")

if st.button("🚀 Calculate Moves to Solve", type="primary"):
    with st.spinner("Analyzing cube arrangement details..."):
        try:
            # Map layout definitions to Kociemba standard notations
            mapping = {"W": "U", "O": "R", "B": "F", "Y": "D", "R": "L", "G": "B"}
            
            # String building using explicit face names matches
            raw_str = (
                "".join(st.session_state.cube_faces["Top (White center)"]) +
                "".join(st.session_state.cube_faces["Right (Orange center)"]) +
                "".join(st.session_state.cube_faces["Front (Blue center)"]) +
                "".join(st.session_state.cube_faces["Bottom (Yellow center)"]) +
                "".join(st.session_state.cube_faces["Left (Red center)"]) +
                "".join(st.session_state.cube_faces["Back (Green center)"])
            )
            
            kociemba_string = "".join([mapping[char] for char in raw_str])
            
            # Run solution search
            sol_raw = kociemba.solve(kociemba_string)
            moves = sol_raw.split()
            
            st.success("🎉 Real Solution Calculated! Keep BLUE facing you and WHITE on top while turning:")
            st.write("---")
            
            for i, move in enumerate(moves):
                base_move = move[0]
                modifier = move[1] if len(move) > 1 else ""
                
                face_names = {
                    "U": "TOP (White center)", "D": "BOTTOM (Yellow center)", 
                    "F": "FRONT (Blue center)", "B": "BACK (Green center)", 
                    "L": "LEFT (Red center)", "R": "RIGHT (Orange center)"
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
            st.error("Invalid Configuration Layout! Check that your color grids completely match your physical cube.")
            st.info("💡 **Quick Fix:** Change the dropdown lists under Step 1 to match any tiles the camera misread!")
