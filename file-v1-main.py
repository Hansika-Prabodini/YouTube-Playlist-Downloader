import os
from taipy.gui import Gui, State, notify
import openai
from dotenv import load_dotenv

# Configuration constants
# Default model can be overridden via the OPENAI_MODEL environment variable
DEFAULT_MODEL_NAME = "gpt-4o-mini"
MAX_PREVIEW_LENGTH = 50


def get_model_name() -> str:
    """Resolve the OpenAI model name from environment or fallback to default.

    Returns:
        Model name to be used for OpenAI chat completions.
    """
    return os.getenv("OPENAI_MODEL", DEFAULT_MODEL_NAME)

# Default conversation values
# Conversation structure: ["Who are you?", "AI response", "user msg 2", "AI response 2", ...]
# Index 0, 2, 4... are user messages; Index 1, 3, 5... are AI responses
DEFAULT_CONTEXT = "The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly.\n\nHuman: Hello, who are you?\nAI: I am an AI created by OpenAI. How can I help you today? "
DEFAULT_CONVERSATION = {
    "Conversation": ["Who are you?", "Hi! I am GPT-4. How can I help you today?"]
}

# Global variables
client = None
context = DEFAULT_CONTEXT
conversation = DEFAULT_CONVERSATION.copy()
current_user_message = ""
past_conversations = []
selected_conv = None
selected_row = [1]


def on_init(state: State) -> None:
    """Initialize the app.

    Args:
        state: The current state of the app.
    """
    state.context = DEFAULT_CONTEXT
    state.conversation = DEFAULT_CONVERSATION.copy()
    state.current_user_message = ""
    state.past_conversations = []
    state.selected_conv = None
    state.selected_row = [1]
    state.client = client


def request(state: State, prompt: str) -> str:
    """Send a prompt to the GPT-4 API and return the response.

    Args:
        state: The current state of the app.
        prompt: The prompt to send to the API.

    Returns:
        The response from the API.
    """
    try:
        response = state.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=get_model_name(),
        )
        return response.choices[0].message.content
    except Exception as ex:
        on_exception(state, "request", ex)
        return "Sorry, I encountered an error processing your request."


def build_context_from_conversation(conversation_list: list) -> str:
    """Build context string from conversation history.

    Args:
        conversation_list: List of conversation messages (alternating user/AI).

    Returns:
        Formatted context string.
    """
    context = DEFAULT_CONTEXT
    # Start from index 2 (first real user message after initial greeting)
    for i in range(2, len(conversation_list), 2):
        user_msg = conversation_list[i]
        ai_response = conversation_list[i + 1] if i + 1 < len(conversation_list) else ""
        context += f"Human: \n {user_msg}\n\n AI:"
        context += ai_response.replace("\n", "")
    return context


def update_context(state: State) -> str:
    """Update the context with the user's message and the AI's response.

    Args:
        state: The current state of the app.

    Returns:
        The AI's response.
    """
    state.context += f"Human: \n {state.current_user_message}\n\n AI:"
    answer = request(state, state.context)
    # Only replace newlines in the context, not in the displayed answer
    state.context += answer.replace("\n", "")
    state.selected_row = [len(state.conversation["Conversation"]) + 1]
    return answer


def send_message(state: State) -> None:
    """Send the user's message to the API and update the context.

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


def style_conv(state: State, idx: int, row: int) -> str:
    """Apply a style to the conversation table depending on the message's author.

    Args:
        state: The current state of the app.
        idx: The index of the message in the table.
        row: The row of the message in the table.

    Returns:
        The style to apply to the message.
    """
    if idx is None:
        return None
    # Even indices (0, 2, 4...) are user messages
    elif idx % 2 == 0:
        return "user_message"
    # Odd indices (1, 3, 5...) are AI messages
    else:
        return "gpt_message"


def on_exception(state: State, function_name: str, ex: Exception) -> None:
    """Catch exceptions and notify user in Taipy GUI.

    Args:
        state: Taipy GUI state.
        function_name: Name of function where exception occurred.
        ex: The exception that was raised.
    """
    notify(state, "error", f"An error occurred in {function_name}: {ex}")


def reset_chat(state: State) -> None:
    """Reset the chat by saving current conversation and starting a new one.

    Args:
        state: The current state of the app.
    """
    # Only save non-empty conversations (more than the default greeting)
    if len(state.conversation["Conversation"]) > 2:
        state.past_conversations.append([
            len(state.past_conversations), 
            state.conversation
        ])
        
    # Reset to default conversation
    state.conversation = DEFAULT_CONVERSATION.copy()
    state.context = DEFAULT_CONTEXT
    state.selected_row = [1]


def tree_adapter(item: list) -> tuple[str, str]:
    """Convert element of past_conversations to id and displayed string.

    Args:
        item: Element of past_conversations [id, conversation_dict].

    Returns:
        Tuple of (identifier, display_string).
    """
    identifier = item[0]
    conversation_list = item[1]["Conversation"]
    # Index 2 is the first real user message (after initial greeting)
    if len(conversation_list) > 2:
        preview_text = conversation_list[2][:MAX_PREVIEW_LENGTH]
        return (identifier, f"{preview_text}...")
    return (identifier, "Empty conversation")


def select_conv(state: State, var_name: str, value) -> None:
    """Select conversation from past_conversations.

    Args:
        state: The current state of the app.
        var_name: Variable name (should be "selected_conv").
        value: Selected conversation data [[id, conversation]].
    """
    if not value or len(value[0]) < 1:
        return
        
    # Retrieve the selected conversation
    conv_id = value[0][0]
    state.conversation = state.past_conversations[conv_id][1]
    
    # Rebuild the context from the conversation history using helper function
    state.context = build_context_from_conversation(state.conversation["Conversation"])
    
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
        title="💬 Taipy Chat"
    )