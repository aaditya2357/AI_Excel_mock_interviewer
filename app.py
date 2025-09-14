import streamlit as st
from src.graph import build_graph
from src.interview_logic import EXCEL_QUESTIONS
from src.local_llm_handler import load_llm_pipeline
from src.perplexity_detector import load_detector_model


graph = build_graph()

def run_graph_logic(history: list[dict[str, str]]):
    """Run the LangGraph chain with proper history conversion."""
    internal_history = []
    for turn in history:
        if turn["role"] == "user":
            internal_history.append(("user", turn["content"]))
        elif turn["role"] == "assistant":
            parts = turn["content"].split("\n\n")
            for part in parts:
                if part.strip():
                    internal_history.append(("ai", part))

    len_before = len(internal_history)

    question_count = sum(1 for role, content in internal_history if content in EXCEL_QUESTIONS)
    current_question_index = question_count - 1 if question_count > 0 else 0
    
    current_state = {
        "interview_status": 0 if len(history) <= 1 else 1,
        "interview_history": internal_history,
        "questions": EXCEL_QUESTIONS,
        "question_index": current_question_index,
        "evaluations": [],
    }

    new_state = graph.invoke(current_state)
    
    new_messages = new_state["interview_history"][len_before:]
    bot_responses = [content for role, content in new_messages if role in ["ai", "assistant"]]
    
    return "\n\n".join(bot_responses)


st.set_page_config(page_title="AI-Powered Excel Interviewer", layout="wide")

st.markdown(
    """
    # 🤖 AI-Powered Excel Interviewer (Phi-3 Mini)
    An AI-powered interview system that asks Excel-related questions and provides feedback.  
    Type a message like **'start'** to begin.
    """
)

if "history" not in st.session_state:
    st.session_state.history = []

for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_input := st.chat_input("Type your answer here..."):

    st.session_state.history.append({"role": "user", "content": user_input})

 
    bot_response = run_graph_logic(st.session_state.history)


    st.session_state.history.append({"role": "assistant", "content": bot_response})

  
    with st.chat_message("assistant", avatar="https://upload.wikimedia.org/wikipedia/commons/7/73/Microsoft_Excel_2013-2019_logo.svg"):
        st.markdown(bot_response)


if st.button("🔄 Clear and Restart Interview"):
    st.session_state.history = []
    st.rerun()


@st.cache_resource
def preload_models():
    load_llm_pipeline()
    load_detector_model()
    return "Models loaded successfully"

try:
    preload_models()
except Exception as e:
    st.error(f"FATAL ERROR: Could not pre-load models: {e}")