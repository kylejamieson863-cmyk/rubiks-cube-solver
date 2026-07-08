import streamlit as st
import cv2
import numpy as np
from PIL import Image
import magiccube
from magiccube.solver.basic_solver import BasicSolver

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
A standard configuration uses 54 characters representing the 6 faces.
The solver uses standard colors:
* **W** = White (Up)
* **Y** = Yellow (Down)
* **O** = Orange (Left)
* **R** = Red (Right)
* **G** = Green (Front)
* **B** = Blue (Back)
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
    
    # default_state needs to match exactly magiccube format (54 chars)
    # Order: Y, R, G, O, B, W (9 chars each)
    default_scramble = "YYYYYYYYYRRRRRRRRRGGGGGGGGGOOOOOOOOOBBBBBBBBBWWWWWWWWW"
    cube_string = st.text_input(
        "Enter your 54-character cube string:", 
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
        
        # Build placeholder string matching order requirement
        cube_string = "".join(detected_colors) + "R"*9 + "G"*9 + "O"*9 + "B"*9 + "W"*9

# ------------------------------------------------------------------
# SOLVER RUNNER
# ------------------------------------------------------------------
st.write("---")
if st.button("🔮 Calculate Moves", type="primary"):
    if len(cube_string) != 54:
        st.error(f"Error: String must be exactly 54 characters. You supplied {len(cube_string)}.")
    else:
        with st.spinner("Calculating solution sequence..."):
            try:
                # Initialize the 3x3 cube with the configuration
                cube = magiccube.Cube(3, cube_string)
                
                # Use basic layer solver
                solver = BasicSolver(cube)
                actions = solver.solve()
                
                # Convert the actions list to strings
                moves = [str(action) for action in actions]
                
                if not moves:
                    st.success("🎉 The cube is already solved!")
                else:
                    st.success(f"🎉 Solution Found in {len(moves)} steps!")
                    st.markdown("### 📋 Step-by-Step Directions:")
                    
                    cols = st.columns(min(len(moves), 6))
                    for i, move in enumerate(moves):
                        with cols[i % 6]:
                            st.info(f"**Step {i+1}** \n\n ## {move}")
                            
            except Exception as e:
                st.error("Invalid Cube Layout! Please check your configuration values.")
                st.caption(f"Engine Debug Error: {str(e)}")
