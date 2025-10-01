from __future__ import annotations


def send_message(state: "State") -> None:
    """
    Send the user's message to the API and update the context.

    This function is designed to work with a Taipy `State` but does not
    require the type to be imported at runtime (annotation is postponed).

    Args:
        state: The current state of the app.
    """
    # Don't process empty messages
    if not getattr(state, "current_user_message", "").strip():
        notify(state, "warning", "Please enter a message")
        return

    try:
        notify(state, "info", "Sending message...")
        answer = update_context(state)

        # Robustly copy the conversation mapping.
        # Some frameworks expose an internal `_dict`; fall back to the mapping itself.
        conv_source = getattr(state.conversation, "_dict", state.conversation)
        try:
            conv = conv_source.copy()  # Prefer Mapping.copy if available
        except AttributeError:
            conv = dict(conv_source)   # Fallback to dict constructor

        conv["Conversation"] += [state.current_user_message, answer]
        state.current_user_message = ""
        state.conversation = conv
        notify(state, "success", "Response received!")
    except Exception as ex:
        on_exception(state, "send_message", ex)
