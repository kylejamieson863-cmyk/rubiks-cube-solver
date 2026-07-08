import streamlit as st
import kociemba

st.set_page_config(page_title="Lucas' Ultimate Cube Solver", page_icon="🎲", layout="centered")

# Smooth Mobile Styling Pack - Forces grids to stay square on mobile screens
st.markdown("""
    <style>
    [data-testid="column"] {
        width: calc(33.3333% - 4px) !important;
        flex: 1 1 calc(33.3333% - 4px) !important;
        min-width: calc(33.3333% - 4px) !important;
    }
    div[data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important;
        gap: 4px !important;
    }
    .stButton>button {
        width: 100% !important;
        padding: 10px 0px !important;
        font-weight: bold !important;
    }
    select {
        font-size: 14px !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ Lucas' Ultimate Cube Solver")
st.write("Hold your cube with **BLUE facing you** and **WHITE on top**.")
st.write("Pick the colors for all 6 sides below. It will not lag at all while you choose!")

# Fixed center mapping based on your cube
face_keys = [
    "Top (White center)", 
    "Front (Blue center)", 
    "Right (Orange center)", 
    "Left (Red center)", 
    "Back (Green center)", 
    "Bottom (Yellow center)"
]
centers = {
    "Top (White center)": "W", 
    "Front (Blue center)": "B", 
    "Right (Orange center)": "O",
    "Left (Red center)": "R", 
    "Back (Green center)": "G", 
    "Bottom (Yellow center)": "Y"
}
color_emojis = {"W": "⬜", "Y": "🟨", "G": "🟩", "B": "🟦", "R": "🟥", "O": "🟧"}

# --- THE INSTANT NO-LAG FORM ---
with st.form("ultimate_paint_form"):
    final_inputs = {}
    
    # Generate all 6 faces smoothly on one page
    for face in face_keys:
        st.write(f"### 🧱 {face}")
        row_cells = []
        
        idx = 1
        for r in range(3):
            cols = st.columns(3)
            for c in range(3):
                with cols[c]:
                    if r == 1 and c == 1:
                        st.write(f"**Center**\n\n{color_emojis[centers[face]]}")
                        row_cells.append(centers[face])
                    else:
                        choice = st.selectbox(
                            f"{idx}",
                            options=["W", "Y", "G", "B", "R", "O"],
                            format_func=lambda x: color_emojis[x],
                            index=["W", "Y", "G", "B", "R", "O"].index(centers[face]),
                            key=f"all_faces_{face}_{idx}"
                        )
                        row_cells.append(choice)
                idx += 1
        final_inputs[face] = row_cells
        st.write("---")

    # Single Submit Button keeps the page from lagging while clicking options
    submit_solve = st.form_submit_button("✨ Solve My Cube!", type="primary")

# --- CALCULATION LOGIC ---
if submit_solve:
    with st.spinner("Calculating perfect path..."):
        try:
            # Map layout to Kociemba standard tokens
            mapping = {"W": "U", "O": "R", "B": "F", "Y": "D", "R": "L", "G": "B"}
            
            raw_str = (
                "".join([mapping[c] for c in final_inputs["Top (White center)"]]) +
                "".join([mapping[c] for c in final_inputs["Right (Orange center)"]]) +
                "".join([mapping[c] for c in final_inputs["Front (Blue center)"]]) +
                "".join([mapping[c] for c in final_inputs["Bottom (Yellow center)"]]) +
                "".join([mapping[c] for c in final_inputs["Left (Red center)"]]) +
                "".join([mapping[c] for c in final_inputs["Back (Green center)"]])
            )
            
            moves = kociemba.solve(raw_str).split()
            
            st.success(f"🎉 Solved in {len(moves)} steps! Keep BLUE facing you and WHITE on top:")
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
                    direction = "➡️ Turn the Blue FRONT face Clockwise" if mod == "" else "⬅️ Turn the Blue FRONT face Counter-Clockwise"
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
                
        except Exception as e:
            st.error("Invalid Color Layout! One or more colors don't match up right.")
            st.info("💡 **Tip:** Double check that you have exactly 9 squares of each color total across the whole list!")
