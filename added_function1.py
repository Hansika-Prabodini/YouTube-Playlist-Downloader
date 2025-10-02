from __future__ import annotations

def send_message(state: State) -> None:
    """
    Send the user's message to the API and update the context.

    Args:
        state: The current state of the app.
    """
    # Don't process empty messages
    if not state.current_user_message.strip():
        notify(state, "warning", "Please enter a message")
        return
        
    try:
        notify(state, "info", "Sending message...")
        answer = update_context(state)
        conv = state.conversation._dict.copy()
        conv["Conversation"] += [state.current_user_message, answer]
        state.current_user_message = ""
        state.conversation = conv
        notify(state, "success", "Response received!")
    except Exception as ex:
        on_exception(state, "send_message", ex)