import streamlit as st
import cv2
import numpy as np
from PIL import Image
from rubik.cube import Cube

st.set_page_config(page_title="Rubik's Cube Solver", page_icon="🎲", layout="centered")

st.title("🎲 Rubik's Cube Solver AI")
st.write("Take a picture or manually input your cube configuration to get the fastest solution.")

# ------------------------------------------------------------------
# SIDEBAR / CONFIGURATION
# ------------------------------------------------------------------
st.sidebar.header("How to Input Your Cube")
mode = st.sidebar.radio("Choose Input Method:", ["Manual Text Input", "Camera Scan (Single Face Demo)"])

st.sidebar.markdown("""
### Cube Face Order Guide
A standard cube representation uses 54 characters representing the grid.
Colors map to face letters:
* **O** = Orange
* **Y** = Yellow
* **W** = White
* **G** = Green
* **B** = Blue
* **R** = Red
""")

# ------------------------------------------------------------------
# HELPER FUNCTION: CV2 COLOR DETECTION
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
            
            cv2.circle(opencv_image, (cx, cy), 10, (255, 255, 255), 2)
            
            pixel_hsv = hsv[cy, cx]
            hue = pixel_hsv[0]
            sat = pixel_hsv[1]
            val = pixel_hsv[2]
            
            # Fixed syntax typo by adding the # comments
            if sat < 40 and val > 200: color = "W" # White
            elif hue < 10 or hue > 170: color = "R" # Red
            elif 11 <= hue <= 25: color = "O" # Orange
            elif 26 <= hue <= 35: color = "Y" # Yellow
            elif 36 <= hue <= 85: color = "G" # Green
            else: color = "B" # Blue
            
            grid_colors.append(color)
            
    return opencv_image, grid_colors

# ------------------------------------------------------------------
# INPUT MECHANISMS
# ------------------------------------------------------------------
if mode == "Manual Text Input":
    st.subheader("Manual Cube State Entry")
    
    # Simple example pattern using standard colors
    default_scramble = "OOOOOOOOOYYYWWWGGGBBBYYYWWWGGGBBBYYYWWWGGGBBBRRRRRRRRR"
    cube_string = st.text_input(
        "Enter your 54-character cube string (O, Y, W, G, B, R):", 
        value=default_scramble,
        max_chars=54
    )
    st.caption(f"Current String Length: {len(cube_string)} / 54")

else:
    st.subheader("Camera Scan Face")
    img_file = st.camera_input("Snap Face")
    
    if img_file:
        processed_img, detected_colors = scan_face_colors(img_file)
        st.image(cv2.cvtColor(processed_img, cv2.COLOR_BGR2RGB), caption="Processed Face Grid Map")
        st.write("Detected Matrix:", "".join(detected_colors))
        
        # Build placeholder string
        cube_string = "".join(detected_colors) + "Y"*9 + "W"*9 + "G"*9 + "B"*9 + "R"*9

# ------------------------------------------------------------------
# SOLVER RUNNER
# ------------------------------------------------------------------
st.write("---")
if st.button("🔮 Calculate Moves", type="primary"):
    if len(cube_string) != 54:
        st.error(f"Error: The string must be exactly 54 characters long. You supplied {len(cube_string)}.")
    else:
        with st.spinner("Calculating solution sequence..."):
            try:
                # Initialize the cube with the user's string configuration
                c = Cube(cube_string)
                
                # rubik-cube library has an internal solver state
                from rubik.solver import Solver
                solver = Solver(c)
                solver.solve()
                
                moves = solver.moves
                
                if not moves:
                    st.success("🎉 The cube is already solved!")
                else:
                    st.success(f"🎉 Solution Found in {len(moves)} steps!")
                    st.markdown("### 📋 Step-by-Step Directions:")
                    
                    # Group moves into columns cleanly
                    cols = st.columns(min(len(moves), 6))
                    for i, move in enumerate(moves):
                        with cols[i % 6]:
                            st.info(f"**Step {i+1}** \n\n ## {move}")
                            
            except Exception as e:
                st.error("Invalid Cube State Layout! Please check your colors.")
                st.caption(f"Engine Debug Error: {str(e)}")
