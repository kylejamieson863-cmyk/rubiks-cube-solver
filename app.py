import streamlit as st
import kociemba

st.set_page_config(page_title="Lucas' Cube Solver", page_icon="🎲", layout="centered")

# --- MOBILE CSS FORCE PACK ---
# This CSS forces Streamlit columns to stay horizontal on mobile phones instead of stacking vertically.
st.markdown("""
    <style>
    [data-testid="column"] {
        width: calc(33.3333% - 8px) !important;
        flex: 1 1 calc(33.3333% - 8px) !important;
        min-width: calc(33.3333% - 8px) !important;
    }
    div[data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important;
        gap: 4px !important;
    }
    .stButton>button {
        width: 100% !important;
        padding: 4px 0px !important;
        font-size: 16px !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎈 Lucas' Rubik's Cube Solver")
st.write("Match the colors on the screen to your cube, then follow the arrows to solve it!")

# ------------------------------------------------------------------
# INITIALIZATION
# ------------------------------------------------------------------
face_order = ["Top (White)", "Left (Red)", "Front (Blue)", "Right (Orange)", "Back (Green)", "Bottom (Yellow)"]
face_centers = {"Top (White)": "W", "Left (Red)": "R", "Front (Blue)": "B", "Right (Orange)": "O", "Back (Green)": "G", "Bottom (Yellow)": "Y"}

color_emojis = {"W": "⬜", "Y": "🟨", "G": "🟩", "B": "🟦", "R": "🟥", "O": "🟧"}
color_names = {"W": "White", "Y": "Yellow", "G": "Green", "B": "Blue", "R": "Red", "O": "Orange"}

if "cube_state" not in st.session_state:
    st.session_state.cube_state = {f: [face_centers[f]] * 9 for f in face_order}

if "brush" not in st.session_state:
    st.session_state.brush = "W"

# ------------------------------------------------------------------
# PALETTE SELECTION (Forced 3 Columns per Row on Mobile)
# ------------------------------------------------------------------
st.subheader("🎨 1. Pick a Color")
codes = ["W", "Y", "G", "B", "R", "O"]

# Row 1 of Palette
p_cols1 = st.columns(3)
for i in range(3):
    code = codes[i]
    with p_cols1[i]:
        active = "⭐" if st.session_state.brush == code else ""
        if st.button(f"{active}{color_emojis[code]}\n\n{color_names[code]}", key=f"p_{code}"):
            st.session_state.brush = code
            st.rerun()

# Row 2 of Palette
p_cols2 = st.columns(3)
for i in range(3, 6):
    code = codes[i]
    with p_cols2[i-3]:
        active = "⭐" if st.session_state.brush == code else ""
        if st.button(f"{active}{color_emojis[code]}\n\n{color_names[code]}", key=f"p_{code}"):
            st.session_state.brush = code
            st.rerun()

# ------------------------------------------------------------------
# STEP 2: PAINT YOUR CUBE (Displays one clean face layout at a time)
# ------------------------------------------------------------------
st.write("---")
st.subheader("🧩 2. Paint Your Cube")
st.caption("Select a face below, then tap the grid squares to match your real cube colors.")

# Dropdown works best on mobile screens to save vertical space
current_face = st.selectbox("Choose the side you want to paint:", face_order)

st.write(f"### Grid for {current_face}:")
grid = st.session_state.cube_state[current_face]

idx = 0
for r in range(3):
    grid_cols = st.columns(3)
    for c in range(3):
        with grid_cols[c]:
            if r == 1 and c == 1:
                # Locked middle center block
                st.button(f"📍\n\n{color_emojis[face_centers[current_face]]}", disabled=True, key=f"c_{current_face}")
            else:
                current_color = grid[idx]
                if st.button(f"{idx+1}\n\n{color_emojis[current_color]}", key=f"b_{current_face}_{idx}"):
                    st.session_state.cube_state[current_face][idx] = st.session_state.brush
                    st.rerun()
        idx += 1

# ------------------------------------------------------------------
# GENERATE SIMPLIFIED MOVES
# ------------------------------------------------------------------
st.write("---")
st.subheader("🚀 3. Get Your Magic Moves")

if st.button("✨ Show Me How To Solve It!", type="primary"):
    try:
        mapping = {"W": "U", "O": "R", "B": "F", "Y": "D", "R": "L", "G": "B"}
        raw_str = (
            "".join(st.session_state.cube_state["Top (White)"]) +
            "".join(st.session_state.cube_state["Right (Orange)"]) +
            "".join(st.session_state.cube_state["Front (Blue)"]) +
            "".join(st.session_state.cube_state["Bottom (Yellow)"]) +
            "".join(st.session_state.cube_state["Left (Red)"]) +
            "".join(st.session_state.cube_state["Back (Green)"])
        )
        kociemba_string = "".join([mapping[char] for char in raw_str])
        moves = kociemba.solve(kociemba_string).split()
        
        st.success("🎉 Steps ready! Keep BLUE facing you and WHITE on top for every single step!")
        st.write("---")
        
        for i, move in enumerate(moves):
            face = move[0]
            mod = move[1] if len(move) > 1 else ""
            
            direction = ""
            if face == "U":
                direction = "➡️ Turn the White TOP layer to the Right" if mod == "'" else "⬅️ Turn the White TOP layer to the Left"
                if mod == "2": direction = "🔄 Turn the White TOP layer around twice"
            elif face == "D":
                direction = "➡️ PUSH the Yellow BOTTOM layer to the Right" if mod == "" else "⬅️ PUSH the Yellow BOTTOM layer to the Left"
                if mod == "2": direction = "🔄 Turn the Yellow BOTTOM layer around twice"
            elif face == "F":
                direction = "➡️ Turn the Blue FRONT face Clockwise (like a steering wheel to the right)" if mod == "" else "⬅️ Turn the Blue FRONT face Counter-Clockwise (to the left)"
                if mod == "2": direction = "🔄 Turn the Blue FRONT face around twice"
            elif face == "B":
                direction = "➡️ Turn the Green BACK wall to the Right" if mod == "'" else "⬅️ Turn the Green BACK wall to the Left"
                if mod == "2": direction = "🔄 Turn the Green BACK wall around twice"
            elif face == "L":
                direction = "⬇️ Roll the Red LEFT side DOWN toward you" if mod == "" else "⬆️ Push the Red LEFT side UP away from you"
                if mod == "2": direction = "🔄 Spin the Red LEFT side around twice"
            elif face == "R":
                direction = "⬆️ Push the Orange RIGHT side UP away from you" if mod == "" else "⬇️ Roll the Orange RIGHT side DOWN toward you"
                if mod == "2": direction = "🔄 Spin the Orange RIGHT side around twice"
            
            st.markdown(f"### Step {i+1}")
            st.info(direction)
            st.write("---")
            
    except:
        st.error("Oops! The colors don't match up quite right. Check your painting against your cube and try again!")

if st.button("🔄 Reset Entire Cube"):
    st.session_state.cube_state = {f: [face_centers[f]] * 9 for f in face_order}
    st.rerun()
