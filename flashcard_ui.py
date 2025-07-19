import streamlit as st
import html

def render_flashcard(question, answer, index):
    bg_color = st.session_state.get("card_color", "#F7F7F7")
    question = html.escape(question)
    answer = html.escape(answer)

    st.markdown(
        f"""
        <style>
        .flip-card {{
            background-color: transparent;
            width: 70%;
            perspective: 1000px;
            margin: 20px auto;
        }}
        .flip-card-inner {{
            position: relative;
            width: 100%;
            height: 150px;
            text-align: center;
            transition: transform 0.8s;
            transform-style: preserve-3d;
            box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
            cursor: pointer;
        }}
        .flip-card:hover .flip-card-inner {{
            transform: rotateY(180deg);
        }}
        .flip-card-front, .flip-card-back {{
            position: absolute;
            width: 100%;
            height: 100%;
            backface-visibility: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 15px;
            border-radius: 10px;
            font-weight: bold;
            color: black;
        }}
        .flip-card-front {{
            background-color: {bg_color};
        }}
        .flip-card-back {{
            background-color: {bg_color};
            transform: rotateY(180deg);
        }}
        </style>

        <div class="flip-card">
            <div class="flip-card-inner">
                <div class="flip-card-front">
                    Q{index+1}: {question}
                </div>
                <div class="flip-card-back">
                    A: {answer}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
