from .perplexity_detector import is_ai_generated
from .local_llm_handler import get_llm_response

EXCEL_QUESTIONS = [
    "What is the difference between the VLOOKUP and HLOOKUP functions in Excel?",
    "Explain how to use the INDEX and MATCH functions together, and why you might prefer them over VLOOKUP.",
    "Describe what a Pivot Table is and give an example of a scenario where it would be useful.",
    "What is Conditional Formatting in Excel? Can you provide an example?",
]

def start_interview(state: dict) -> dict:
    """
    Appends a welcome message to the history, preserving the user's first message.
    """
    intro_message = "Welcome to the automated Excel skills assessment! I will ask you a series of questions to gauge your knowledge. Let's start with the first one."
    history = state.get("interview_history", [])
    history.append(("ai", intro_message))
    return {
        **state,
        "interview_status": 1,
        "interview_history": history,
        "questions": EXCEL_QUESTIONS,
        "question_index": 0,
        "evaluations": [],
    }

def ask_question(state: dict) -> dict:
    """Asks the current question based on the question_index."""
    question_index = state["question_index"]
    current_question = state["questions"][question_index]
    history = state.get("interview_history", [])
    history.append(("ai", current_question))
    return {**state, "interview_history": history}

def process_user_response(state: dict) -> dict:
    """Evaluates the user's response and appends the evaluation to history."""
    history = state.get("interview_history", [])
    user_response = history[-1][1]

    if is_ai_generated(user_response, threshold=35.0):
        termination_message = "This interview will now be terminated due to the detection of AI-generated content."
        history.append(("ai", termination_message))
        return {**state, "interview_history": history, "interview_status": 2}
    
    current_question = state["questions"][state["question_index"]]

    evaluation_prompt = (
        "You are an expert evaluator. Concisely evaluate the following answer to an Excel interview question "
        "based on its technical accuracy and clarity. Start the evaluation directly without conversational filler.\n\n"
        f"Question: {current_question}\n"
        f"Answer: {user_response}"
    )
    
    evaluation = get_llm_response(evaluation_prompt)
    
 
    history.append(("ai", f"**Evaluation:**\n{evaluation}"))
    
    evaluations = state.get("evaluations", [])
    evaluations.append(evaluation)

    return {
        **state, 
        "interview_history": history,
        "evaluations": evaluations, 
        "question_index": state["question_index"] + 1
    }

def generate_final_report(state: dict) -> dict:
    """Generates and appends the final performance summary."""
    interview_transcript = "\n".join([f"{speaker.capitalize()}: {text}" for speaker, text in state['interview_history']])
    evaluations_summary = "\n\n".join(f"Evaluation for Q{i+1}:\n{e}" for i, e in enumerate(state['evaluations']))

    report_prompt = (
        "You are a career coach. Based on the interview transcript and evaluations below, write a brief, constructive performance summary. "
        "Use Markdown for a 'Strengths' section and an 'Areas for Improvement' section.\n\n"
        f"---TRANSCRIPT---\n{interview_transcript}\n\n---EVALUATIONS---\n{evaluations_summary}"
    )
    
    final_feedback = get_llm_response(report_prompt)
    history = state.get("interview_history", [])

    history.append(("ai", f"**Final Performance Summary:**\n{final_feedback}"))

    return {**state, "final_feedback": final_feedback, "interview_history": history, "interview_status": 2}


def route_after_evaluation(state: dict):
    """Routes to the next step after a user's response has been processed."""
    if state.get("interview_status") == 2:
        return "terminate"
    elif state["question_index"] >= len(state["questions"]):
        return "generate_final_report"
    else:
        return "ask_question"

def route_start_of_interview(state: dict):
    """
    CORRECTED: This is the critical fix.
    Checks if it's the very first user message to start the interview.
    Otherwise, it processes the message as an answer.
    """

    if len(state["interview_history"]) == 1:
        return "start_interview"

    else:
        return "process_user_response"