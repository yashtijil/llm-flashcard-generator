import streamlit as st
import pdfplumber
from together_api import generate_flashcards_togetherai
from flashcard_ui import render_flashcard
import pandas as pd
import io
import json


st.set_page_config(page_title="LLM Flashcard Generator", layout="wide")

st.markdown(
    "<h1 style='text-align: center;'>📚 Memory Forge</u></h1>", unsafe_allow_html=True
)
st.markdown(
    "<h4 style='text-align: center;'>Ignite learning with AI-generated Flashcards</h4>",
    unsafe_allow_html=True,
)

flashcards = st.session_state.get("flashcards", [])

# Input method
st.sidebar.markdown("### ✏️ Input Method")
input_method = st.sidebar.radio("Choose input type:", ["Paste Text", "Upload File"])

st.sidebar.markdown("---") 

# Flashcard color
st.sidebar.subheader("🎨 Flashcard Style")
card_color = st.sidebar.color_picker(
    "Pick a card color", st.session_state.get("card_color", "#F7F7F7")
)
if "card_color" not in st.session_state or card_color != st.session_state["card_color"]:
    st.session_state["card_color"] = card_color
    st.rerun()
    
text_input = ""

# File Upload
if input_method == "Upload File":
    uploaded_file = st.file_uploader("Upload a .pdf or .txt file", type=["pdf", "txt"])
    if uploaded_file:
        if uploaded_file.name.endswith(".pdf"):
            with pdfplumber.open(uploaded_file) as pdf:
                text_input = "\n".join(
                    [page.extract_text() for page in pdf.pages if page.extract_text()]
                )
        else:
            text_input = uploaded_file.read().decode("utf-8")

# Paste Text
elif input_method == "Paste Text":
    text_input = st.text_area("Paste your content here:", height=300)


# Number of flashcards
num_cards = st.slider("Number of flashcards", 3, 15, 5)


if "is_generating" not in st.session_state:
    st.session_state["is_generating"] = False

# Generate button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    generate_button = st.button(
        "✨ Generate Flashcards ✨",
        use_container_width=True,
        disabled=st.session_state["is_generating"]
    )

if generate_button:
    text_input_clean = text_input.strip()

    if not text_input_clean:
        st.error("❗ No input provided. Please upload a file or enter text.")
        st.stop()

    if len(text_input_clean) < 30:
        st.warning("⚠️ Input is too short to generate flashcards. Please provide more content.")
        st.stop()

    st.session_state["is_generating"] = True  # Disable button

    with st.spinner("Generating flashcards..."):
        try:
            raw_output = generate_flashcards_togetherai(text_input_clean, num_cards)

            flashcards = []
            current = {}

            for line in raw_output.splitlines():
                line = line.strip()
                if line.startswith("Q:"):
                    current = {"question": line[2:].strip()}
                elif line.startswith("A:") and current.get("question"):
                    current["answer"] = line[2:].strip()
                    flashcards.append(current)
                    current = {}  # Reset current for next Q/A

            if flashcards:
                st.success("✅ Flashcards Generated!")
                st.session_state["flashcards"] = flashcards
            else:
                st.warning("⚠️ No flashcards could be parsed from the output.")
        except Exception as e:
            st.error(f"❌ Error generating flashcards: {e}")

    st.session_state["is_generating"] = False  # Re-enable button

# Editing
for i, card in enumerate(flashcards):
    edit_key = f"editing_{i}"

    # Handle button events
    if st.session_state.pop(f"edit_clicked_{i}", False):
        st.session_state[edit_key] = True
        st.rerun()

    if st.session_state.pop(f"save_clicked_{i}", False):
        q_key, a_key = f"edit_q_{i}", f"edit_a_{i}"
        edited_q = st.session_state.get(q_key, "").strip()
        edited_a = st.session_state.get(a_key, "").strip()

        if not edited_q or not edited_a:
            st.warning("⚠️ Both Question and Answer must be filled to save changes.")
            st.session_state[edit_key] = True  # Stay in edit mode
        else:
            flashcards[i] = {"question": edited_q, "answer": edited_a}
            st.session_state[edit_key] = False
            st.rerun()

    if st.session_state.pop(f"cancel_clicked_{i}", False):
        st.session_state[edit_key] = False
        st.rerun()

    if st.session_state.pop(f"delete_clicked_{i}", False):
        if i < len(flashcards):  # safety check
            del flashcards[i]
            st.rerun()

    # UI rendering
    if st.session_state.get(edit_key, False):
        st.markdown(f"**Editing Flashcard #{i + 1}**")
        st.text_area("Edit Question", value=card["question"], key=f"edit_q_{i}")
        st.text_area("Edit Answer", value=card["answer"], key=f"edit_a_{i}")
        col1, col2, _ = st.columns(3)
        with col1:
            st.button("💾 Save", key=f"save_{i}", on_click=lambda i=i: st.session_state.update({f"save_clicked_{i}": True}))
        with col2:
            st.button("❌ Cancel", key=f"cancel_{i}", on_click=lambda i=i: st.session_state.update({f"cancel_clicked_{i}": True}))
    else:
        col1, col2 = st.columns([5, 1])
        with col1:
            render_flashcard(card["question"], card["answer"], i)
        with col2:
            st.markdown("##")  # spacing
            col_e, col_d = st.columns(2)
            with col_e:
                st.button("✏️ Edit", key=f"edit_{i}", on_click=lambda i=i: st.session_state.update({f"edit_clicked_{i}": True}))
            with col_d:
                st.button("Delete", key=f"delete_{i}", on_click=lambda i=i: st.session_state.update({f"delete_clicked_{i}": True}))

# Clear inputs after adding a card
if st.session_state.get("clear_new_inputs", False):
    st.session_state["new_q"] = ""
    st.session_state["new_a"] = ""
    st.session_state["clear_new_inputs"] = False

if "flashcards" in st.session_state:
    flashcards = st.session_state["flashcards"]
    
    st.subheader("🧠 Flashcards")

    # Add new flashcard
    with st.expander("➕ Add a New Flashcard"):
        new_q = st.text_area("Enter your question", key="new_q")
        new_a = st.text_area("Enter the answer", key="new_a")

        if st.button("➕ Add Flashcard"):
            if new_q.strip() and new_a.strip():
                flashcards.append({"question": new_q.strip(), "answer": new_a.strip()})
                st.session_state["clear_new_inputs"] = True
                st.rerun()
            else:
                st.warning("❗ Both question and answer are required to add a flashcard.")

    # Export
    st.subheader("📤 Export Flashcards")
    export_format = st.selectbox(
        "Choose export format", ["Text (.txt)", "CSV (.csv)", "JSON (.json)"]
    )

    if not flashcards:
        st.warning("⚠️ No flashcards available to export.")
        st.stop()

    if export_format == "Text (.txt)":
        txt_data = ""
        for i, c in enumerate(flashcards, start=1):
            txt_data += f"Q{i}: {c['question']}\nA{i}: {c['answer']}\n---\n"
        st.download_button("⬇️ Download .txt", txt_data, file_name="flashcards.txt")

    elif export_format == "CSV (.csv)":
        df = pd.DataFrame(flashcards)
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        st.download_button(
            "⬇️ Download .csv", csv_buffer.getvalue(), file_name="flashcards.csv"
        )

    elif export_format == "JSON (.json)":
        json_data = json.dumps(flashcards, indent=2)
        st.download_button(
            "⬇️ Download .json",
            json_data,
            file_name="flashcards.json",
            mime="application/json",
        )

    else:
        st.warning("⚠️ No flashcards to export.")

