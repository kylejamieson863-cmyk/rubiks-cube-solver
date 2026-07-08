import streamlit as st
import cv2
import numpy as np
from PIL import Image
import kociemba

st.set_page_config(page_title="Rubik's Cube Solver", page_icon="🎲", layout="centered")

st.title("🎲 Rubik's Cube Solver AI")
st.write("Take a picture or manually input your cube configuration to get the fastest solution.")

# ------------------------------------------------------------------
# SIDEBAR / CONFIGURATION
# ------------------------------------------------------------------
st.sidebar.header("How to Input Your Cube")
mode = st.sidebar.radio("Choose Input Method:", ["Manual Text Input", "Camera Scan (Single Face Demo)"])

# Standard Rubik's Cube notation mapping mapping:
# Faces must be ordered: U (Up), R (Right), F (Front), D (Down), L (Left), B (Back)
st.sidebar.markdown("""
### Cube Face Order Guide
When entering text, Kociemba expects 54 characters in this order:
1. **U** (Up/White - 9 inputs)
2. **R** (Right/Red - 9 inputs)
3. **F** (Front/Green - 9 inputs)
4. **D** (Down/Yellow - 9 inputs)
5. **L** (Left/Orange - 9 inputs)
6. **B** (Back/Blue - 9 inputs)
""")

# ------------------------------------------------------------------
# HELPER FUNCTION: CV2 COLOR DETECTION
# ------------------------------------------------------------------
def scan_face_colors(image_bytes):
    # Convert PIL image to OpenCV format
    file_bytes = np.asarray(bytearray(image_bytes.read()), dtype=np.uint8)
    opencv_image = cv2.imdecode(file_bytes, 1)
    hsv = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2HSV)
    
    # Get image dimensions
    h, w, _ = opencv_image.shape
    
    # Divide the image into a 3x3 grid grid points
    grid_colors = []
    for row in range(3):
        for col in range(3):
            # Sample the center pixel of each grid square
            cx = int((col + 0.5) * (w / 3))
            cy = int((row + 0.5) * (h / 3))
            
            # Draw a small circle on the image where we sampled
            cv2.circle(opencv_image, (cx, cy), 10, (255, 255, 255), 2)
            
            # Simple Hue-based color approximation
            pixel_hsv = hsv[cy, cx]
            hue = pixel_hsv[0]
            sat = pixel_p_hsv = pixel_hsv[1]
            val = pixel_hsv[2]
            
            # Naive thresholding for demo purposes
            if sat < 40 and val > 200: color = "U" (White)
            elif hue < 10 or hue > 170: color = "R" (Red)
            elif 11 <= hue <= 25: color = "L" (Orange)
            elif 26 <= hue <= 35: color = "D" (Yellow)
            elif 36 <= hue <= 85: color = "F" (Green)
            else: color = "B" (Blue)
            
            grid_colors.append(color)
            
    return opencv_image, grid_colors

# ------------------------------------------------------------------
# MODE 1: MANUAL TEXT INPUT
# ------------------------------------------------------------------
if mode == "Manual Text Input":
    st.subheader("Manual Cube State Entry")
    
    # A standard pre-scrambled example cube state string
    default_scramble = "DUUBULDBFRBFRRULLLBRDFFFBLURDBFDFDRFRULBLUURDLLLBRRFLB"
    
    cube_string = st.text_input(
        "Enter your 54-character cube string (Use U, R, F, D, L, B):", 
        value=default_scramble,
        max_chars=54
    )
    
    st.caption(f"Current String Length: {len(cube_string)} / 54")

# ------------------------------------------------------------------
# MODE 2: CAMERA SCAN (DEMO)
# ------------------------------------------------------------------
else:
    st.subheader("Camera Scan Face")
    st.info("Fit one face of the cube perfectly into the camera frame.")
    
    img_file = st.camera_input("Snap Face")
    
    if img_file:
        processed_img, detected_colors = scan_face_colors(img_file)
        
        # Display the processed frame with sample targets
        st.image(cv2.cvtColor(processed_img, cv2.COLOR_BGR2RGB), caption="Processed Face Grid Map")
        st.write("Detected Matrix:", "".join(detected_colors))
        
        st.warning("To solve a full cube, you need to string all 6 processed faces together in the exact order. Copying scanned values to a full 54-character string below:")
        
        # Fallback to demo solving using the detected face padded with placeholders
        cube_string = "".join(detected_colors) + "R"*9 + "F"*9 + "D"*9 + "L"*9 + "B"*9

# ------------------------------------------------------------------
# SOLVER RUNNER
# ------------------------------------------------------------------
st.write("---")
if st.button("🔮 Calculate Minimum Moves", type="primary"):
    if len(cube_string) != 54:
        st.error(f"Error: The string must be exactly 54 characters long. You supplied {len(cube_string)}.")
    else:
        with st.spinner("Calculating optimal path using Two-Phase Algorithm..."):
            try:
                # Solve the string state using Kociemba engine
                solution = kociemba.solve(cube_string)
                
                st.success("🎉 Solution Found!")
                
                # Split moves out cleanly
                moves = solution.split(" ")
                st.metric(label="Total Moves required", value=f"{len(moves)} Moves")
                
                # Render the move list beautifully
                st.markdown("### 📋 Step-by-Step Directions:")
                cols = st.columns(min(len(moves), 6))
                for i, move in enumerate(moves):
                    with cols[i % 6]:
                        st.info(f"**Step {i+1}** \n\n ## {move}")
                        
            except Exception as e:
                st.error("Invalid Cube State! The layout provided is impossible to solve physically. Check your colors and try again.")
                st.caption(f"Engine Debug Error: {str(e)}")
