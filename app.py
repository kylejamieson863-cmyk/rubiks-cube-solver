import streamlit as st
import kociemba

st.set_page_config(page_title="Kid-Friendly Cube Solver", page_icon="🎲", layout="wide")

st.title("🎈 Rubik's Cube Solver")
st.write("Match the colors on the screen to your cube, then follow the arrows to solve it!")

# ------------------------------------------------------------------
# INITIALIZATION
# ------------------------------------------------------------------
# Fixed kid-friendly center arrangement
face_order = ["Top (White)", "Left (Red)", "Front (Blue)", "Right (Orange)", "Back (Green)", "Bottom (Yellow)"]
face_centers = {"Top (White)": "W", "Left (Red)": "R", "Front (Blue)": "B", "Right (Orange)": "O", "Back (Green)": "G", "Bottom (Yellow)": "Y"}

color_emojis = {"W": "⬜", "Y": "🟨", "G": "🟩", "B": "🟦", "R": "🟥", "O": "🟧"}
color_names = {"W": "White", "Y": "Yellow", "G": "Green", "B": "Blue", "R": "Red", "O": "Orange"}

if "cube_state" not in st.session_state:
    st.session_state.cube_state = {f: [face_centers[f]] * 9 for f in face_order}

if "brush" not in st.session_state:
    st.session_state.brush = "W"

# ------------------------------------------------------------------
# PALETTE SELECTION
# ------------------------------------------------------------------
st.subheader("🎨 1. Pick a Color")
palette_cols = st.columns(6)
for i, code in enumerate(["W", "Y", "G", "B", "R", "O"]):
    with palette_cols[i]:
        active = "⭐ " if st.session_state.brush == code else ""
        if st.button(f"{active}{color_emojis[code]}\n\n{color_names[code]}", key=f"p_{code}"):
            st.session_state.brush = code
            st.rerun()

# ------------------------------------------------------------------
# THE FLATTENED CUBE MAP LAYOUT
# ------------------------------------------------------------------
st.write("---")
st.subheader("🧩 2. Paint Your Cube")
st.caption("Tap the squares to change their colors until they look exactly like your real cube!")

def draw_kid_grid(face_name):
    st.markdown(f"**{face_name}**")
    grid = st.session_state.cube_state[face_name]
    idx = 0
    for r in range(3):
        cols = st.columns(3)
        for c in range(3):
            with cols[c]:
                if r == 1 and c == 1:
                    st.button(color_emojis[face_centers[face_name]], disabled=True, key=f"c_{face_name}")
                else:
                    current_color = grid[idx]
                    if st.button(color_emojis[current_color], key=f"b_{face_name}_{idx}"):
                        st.session_state.cube_state[face_name][idx] = st.session_state.brush
                        st.rerun()
            idx += 1

# Displaying faces in a clean, open 2D cross layout
row1_cols = st.columns([1, 1, 1])
with row1_cols[1]:
    draw_kid_grid("Top (White)")

st.write("")

row2_cols = st.columns(4)
with row2_cols[0]:
    draw_kid_grid("Left (Red)")
with row2_cols[1]:
    draw_kid_grid("Front (Blue)")
with row2_cols[2]:
    draw_kid_grid("Right (Orange)")
with row2_cols[3]:
    draw_kid_grid("Back (Green)")

st.write("")

row3_cols = st.columns([1, 1, 1])
with row3_cols[1]:
    draw_kid_grid("Bottom (Yellow)")

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
            
            # Map moves to crystal-clear kid instructions
            title = f"Step {i+1}"
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
            
            st.markdown(f"### {title}")
            st.info(direction)
            st.write("---")
            
    except:
        st.error("Oops! The colors don't match up quite right. Check your painting against your cube and try again!")

if st.button("🔄 Reset Entire Cube"):
    st.session_state.cube_state = {f: [face_centers[f]] * 9 for f in face_order}
    st.rerun()
