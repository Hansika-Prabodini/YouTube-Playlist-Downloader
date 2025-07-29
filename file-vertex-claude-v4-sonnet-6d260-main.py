

def update_context(state: State) -> str:
    """
    Update the context with the user's message and the AI's response.

    Args:
        - state: The current state of the app.
    """
    state.context += f"Human: \n {state.current_user_message}\n\n AI:"
    answer = request(state, state.context).replace("\n", "")
    state.context += answer
    state.selected_row = [len(state.conversation["Conversation"]) + 1]
    return answer