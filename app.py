import gradio as gr
from src.graph import build_graph
from src.interview_logic import EXCEL_QUESTIONS
from src.local_llm_handler import load_llm_pipeline
from src.perplexity_detector import load_detector_model

# Initialize the graph
graph = build_graph()

def run_graph_logic(history: list[dict[str, str]]):
    """
    This helper function contains the core logic for running the LangGraph chain.
    """
    # --- THIS BLOCK CONTAINS THE CRITICAL FIX ---
    # 1. Correctly convert Gradio's history (list of dicts) into our graph's internal format.
    internal_history = []
    for turn in history:
        if turn["role"] == "user":
            internal_history.append(("user", turn["content"]))
        elif turn["role"] == "assistant":
            # Split combined bot messages back into their original parts.
            # This is the key to correctly calculating question_count.
            parts = turn["content"].split("\n\n")
            for part in parts:
                if part.strip(): # Ensure we don't add empty parts
                    internal_history.append(("ai", part)) # Use "ai" as expected by the graph

    len_before = len(internal_history)

    # 2. Build the state dictionary. This logic is now correct because internal_history is correct.
    question_count = sum(1 for role, content in internal_history if content in EXCEL_QUESTIONS)
    current_question_index = question_count - 1 if question_count > 0 else 0
    
    current_state = {
        "interview_status": 0 if len(history) <= 1 else 1,
        "interview_history": internal_history,
        "questions": EXCEL_QUESTIONS,
        "question_index": current_question_index,
        "evaluations": [], 
    }

    print(f"Invoking graph. Question count: {question_count}. Using index: {current_question_index}.")
    new_state = graph.invoke(current_state)
    
    new_messages = new_state["interview_history"][len_before:]
    bot_responses = [content for role, content in new_messages if role in ["ai", "assistant"]]
    
    return "\n\n".join(bot_responses)


def user_sends_message(user_message: str, history: list[dict[str, str]]):
    """
    This function correctly receives the new user_message and the history.
    """
    history.append({"role": "user", "content": user_message})
    bot_response = run_graph_logic(history)
    history.append({"role": "assistant", "content": bot_response})
    return history, ""


def clear_chat():
    """Returns an empty list for the chatbot and an empty string for the textbox."""
    return [], ""


# --- UI CODE (No changes needed here) ---
with gr.Blocks(theme="soft", css=".gradio-container {max-width: 1200px; margin: 0 auto;}") as demo:
    gr.Markdown(
        """
        # 🤖 AI-Powered Excel Interviewer (Phi-3 Mini)
        An AI-powered interview system that asks Excel-related questions and provides feedback. 
        Click one of the examples or type a message like 'start' to begin.
        """
    )

    chatbot = gr.Chatbot(
        label="Interview Conversation",
        type="messages",
        height=600,
        show_copy_button=True,
        placeholder="The interview will begin after you send your first message.",
        avatar_images=(None, "https://upload.wikimedia.org/wikipedia/commons/1/1d/Microsoft_Excel_2013-2019_logo.svg")
    )

    with gr.Row():
        user_input = gr.Textbox(
            show_label=False,
            placeholder="Type your answer here and press Enter...",
            scale=5
        )
        submit_btn = gr.Button("Submit", variant="primary", scale=1)

    with gr.Row():
        clear_btn = gr.Button("Clear and Restart Interview", variant="stop")
        gr.Examples(
            examples=["I'm ready to start the interview", "Let's begin", "Start the assessment"],
            inputs=user_input
        )

    submit_btn.click(
        fn=user_sends_message,
        inputs=[user_input, chatbot],
        outputs=[chatbot, user_input]
    )
    user_input.submit(
        fn=user_sends_message,
        inputs=[user_input, chatbot],
        outputs=[chatbot, user_input]
    )
    clear_btn.click(
        fn=clear_chat,
        inputs=None,
        outputs=[chatbot, user_input],
        queue=False
    )

if __name__ == "__main__":
    print("--- Pre-loading models on application startup... ---")
    try:
        load_llm_pipeline()
        load_detector_model()
        print("--- All models pre-loaded successfully. Starting Gradio server. ---")
    except Exception as e:
        print(f"--- FATAL ERROR: Could not pre-load models: {e} ---")

    demo.launch(debug=True, show_error=True)
