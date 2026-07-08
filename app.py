import streamlit as st
import cv2
import numpy as np
import kociemba

st.set_page_config(page_title="Real Rubik's Cube Solver", page_icon="🎲", layout="centered")

st.title("🎲 Custom Rubik's Cube Solver")
st.write("Fill out the grids using your exact layout: 1-3 (Top row), 4-6 (Middle row), 7-9 (Bottom row).")

# Initialize state tracker with 9 entries per face
if "cube_faces" not in st.session_state:
    st.session_state.cube_faces = {
        "Top (White center)": ["W"] * 9,
        "Bottom (Yellow center)": ["Y"] * 9,
        "Front (Blue center)": ["B"] * 9,
        "Back (Green center)": ["G"] * 9,
        "Left (Red center)": ["R"] * 9,
        "Right (Orange center)": ["O"] * 9
    }

face_centers = {
    "Top (White center)": "W",
    "Bottom (Yellow center)": "Y",
    "Front (Blue center)": "B",
    "Back (Green center)": "G",
    "Left (Red center)": "R",
    "Right (Orange center)": "O"
}

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

st.write(f"### 🛠️ Verify & Correct the **{current_face}** Grid Layout:")
st.caption("1-3 = Top Row | 4-6 = Middle Row | 7-9 = Bottom Row")

face_grid = st.session_state.cube_faces[current_face]

idx = 0
for row in range(3):
    cols = st.columns(3)
    for col in range(3):
        with cols[col]:
            if row == 1 and col == 1:
                st.write(f"**Pos 5 (Center)**\n\n{color_styles[face_centers[current_face]]}")
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
# STEP 2: MATHEMATICAL SOLVER WITH USER POSITION MAPPING
# ------------------------------------------------------------------
st.write("---")
st.subheader("🔮 Step 2: Calculate Your Solution")

if st.button("🚀 Calculate Moves to Solve", type="primary"):
    with st.spinner("Translating your 1-9 grid configurations into standard solution arrays..."):
        try:
            # Map user's colors to Kociemba standard symbols
            # Target layout mapping for custom colors:
            # W -> U (Up), O -> R (Right), B -> F (Front), Y -> D (Down), R -> L (Left), G -> B (Back)
            mapping = {"W": "U", "O": "R", "B": "F", "Y": "D", "R": "L", "G": "B"}
            
            # Extract lists directly matching your 1-9 input assignments
            U_face = st.session_state.cube_faces["Top (White center)"]
            R_face = st.session_state.cube_faces["Right (Orange center)"]
            f_face = st.session_state.cube_faces["Front (Blue center)"]
            D_face = st.session_state.cube_faces["Bottom (Yellow center)"]
            L_face = st.session_state.cube_faces["Left (Red center)"]
            B_face = st.session_state.cube_faces["Back (Green center)"]
            
            # Build the continuous string in strict Kociemba sequence ordering: U1-U9, R1-R9, F1-F9, D1-D9, L1-L9, B1-B9
            raw_str = "".join(U_face) + "".join(R_face) + "".join(f_face) + "".join(D_face) + "".join(L_face) + "".join(B_face)
            kociemba_string = "".join([mapping[char] for char in raw_str])
            
            # Execute search parameters
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
            st.info("💡 **Quick Fix:** Double-check every face selection to make sure no colors got switched up!")

if st.button("🔄 Clear Camera Memory & Start Over"):
    st.session_state.cube_faces = {k: ["W" if face_centers[k]=="W" else "Y" if face_centers[k]=="Y" else "B" if face_centers[k]=="B" else "G" if face_centers[k]=="G" else "R" if face_centers[k]=="R" else "O" for _ in range(9)] for k in st.session_state.cube_faces}
    st.rerun()
