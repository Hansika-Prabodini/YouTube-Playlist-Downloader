import os
from typing import Any, List, Optional, Tuple

from dotenv import load_dotenv
import openai
from taipy.gui import Gui, State, notify

# Default conversation values
DEFAULT_CONTEXT = (
    "The following is a conversation with an AI assistant. The assistant is "
    "helpful, creative, clever, and very friendly.\n\n"
    "Human: Hello, who are you?\n"
    "AI: I am an AI created by OpenAI. How can I help you today? "
)
DEFAULT_CONVERSATION = {
    "Conversation": [
        "Who are you?",
        "Hi! I am GPT-4. How can I help you today?",
    ]
}

# Global variables
MODEL_NAME = "gpt-4-turbo-preview"
client: Optional[Any] = None
context = DEFAULT_CONTEXT
conversation = DEFAULT_CONVERSATION.copy()
current_user_message = ""
past_conversations: List[Any] = []
selected_conv = None
selected_row = [1]


def on_init(state: State) -> None:
    """Initialize the app and state defaults."""
    state.context = DEFAULT_CONTEXT
    state.conversation = DEFAULT_CONVERSATION.copy()
    state.current_user_message = ""
    state.past_conversations = []
    state.selected_conv = None
    state.selected_row = [1]
    state.client = client


def request(state: State, prompt: str) -> str:
    """Send a prompt to the OpenAI API and return the response text.

    Args:
        state: The current state of the app (provides the OpenAI client).
        prompt: The prompt to send to the API.

    Returns:
        The response message content from the API, or an error string on failure.
    """
    try:
        response = state.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=MODEL_NAME,
        )
        return response.choices[0].message.content
    except Exception as ex:  # noqa: BLE001 - surface errors to the UI in a friendly way
        on_exception(state, "request", ex)
        return "Sorry, I encountered an error processing your request."


def update_context(state: State) -> str:
    """Update the context with the user's message and the AI's response.

    Returns the AI's response text.
    """
    state.context += f"Human: \n {state.current_user_message}\n\n AI:"
    answer = request(state, state.context)
    # Only replace newlines in the context, not in the displayed answer
    state.context += answer.replace("\n", "")
    state.selected_row = [len(state.conversation["Conversation"]) + 1]
    return answer


def send_message(state: State) -> None:
    """Send the user's message, update the conversation, and notify the user."""
    if not state.current_user_message.strip():
        notify(state, "warning", "Please enter a message")
        return

    try:
        notify(state, "info", "Sending message...")
        answer = update_context(state)
        # Avoid relying on private attributes that may not exist on plain dicts
        conv = state.conversation.copy()
        conv["Conversation"] += [state.current_user_message, answer]
        state.current_user_message = ""
        state.conversation = conv
        notify(state, "success", "Response received!")
    except Exception as ex:  # noqa: BLE001
        on_exception(state, "send_message", ex)


def style_conv(state: State, idx: Optional[int], row: int) -> Optional[str]:
    """Return a style for the conversation table depending on the author."""
    if idx is None:
        return None
    return "user_message" if idx % 2 == 0 else "gpt_message"


def on_exception(state: State, function_name: str, ex: Exception) -> None:
    """Catch exceptions and notify the user in the Taipy GUI."""
    notify(state, "error", f"An error occurred in {function_name}: {ex}")


def reset_chat(state: State) -> None:
    """Save the current conversation (if non-empty) and start a new one."""
    if len(state.conversation["Conversation"]) > 2:
        state.past_conversations.append(
            [len(state.past_conversations), state.conversation]
        )

    state.conversation = DEFAULT_CONVERSATION.copy()
    state.context = DEFAULT_CONTEXT
    state.selected_row = [1]


def tree_adapter(item: list) -> Tuple[str, str]:
    """Convert an element of past_conversations to an id and display string."""
    identifier = str(item[0])
    if len(item[1]["Conversation"]) > 3:
        return (identifier, item[1]["Conversation"][2][:50] + "...")
    return (identifier, "Empty conversation")


def select_conv(state: State, var_name: str, value: Any) -> None:
    """Select a conversation from past_conversations based on tree selection."""
    if not value or not value[0] or len(value[0]) < 1:
        return

    # Retrieve the selected conversation
    conv_id = value[0][0]
    state.conversation = state.past_conversations[conv_id][1]

    # Rebuild the context from the conversation history
    state.context = DEFAULT_CONTEXT
    for i in range(2, len(state.conversation["Conversation"]), 2):
        state.context += (
            f"Human: \n {state.conversation['Conversation'][i]}\n\n AI:"
        )
        state.context += state.conversation["Conversation"][i + 1].replace(
            "\n", ""
        )

    state.selected_row = [len(state.conversation["Conversation"]) - 1]


# UI definition
page = """
<|layout|columns=300px 1|
<|part|class_name=sidebar|
# Taipy **Chat**{: .color-primary} # {: .logo-text}
<|New Conversation|button|class_name=fullwidth plain|id=reset_app_button|on_action=reset_chat|>
### Previous activities ### {: .h5 .mt2 .mb-half}
<|{selected_conv}|tree|lov={past_conversations}|class_name=past_prompts_list|multiple|adapter=tree_adapter|on_change=select_conv|>
|>

<|part|class_name=p2 align-item-bottom table|
<|{conversation}|table|style=style_conv|show_all|selected={selected_row}|rebuild|>
<|part|class_name=card mt1|
<|{current_user_message}|input|label=Write your message here...|on_action=send_message|class_name=fullwidth|change_delay=-1|>
<|Send|button|on_action=send_message|class_name=primary|>
|>
|>
|>
"""

if __name__ == "__main__":
    # Load environment variables and initialize OpenAI client
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set.")
        print("Please set your API key in a .env file or environment variables.")
        client = None
    else:
        client = openai.Client(api_key=api_key)

    # Start the GUI
    Gui(page).run(
        dark_mode=True,
        debug=True,
        use_reloader=True,
        title="💬 Taipy Chat",
    )
