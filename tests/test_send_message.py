import importlib.util
import types
from types import SimpleNamespace
from pathlib import Path


def load_module_from_path(path: str):
    spec = importlib.util.spec_from_file_location("file_v1_main", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_send_message_updates_conversation_and_clears_input(tmp_path):
    # Load the module from the given file path (filename has hyphens)
    module_path = str(Path(__file__).resolve().parents[1] / "file-v1-main.py")
    m = load_module_from_path(module_path)

    # Stub update_context to return a predictable answer
    def stub_update_context(state):
        return "stubbed-answer"

    m.update_context = stub_update_context

    # Create a minimal state object with required attributes
    state = SimpleNamespace()
    state.current_user_message = "Hello GPT"
    state.conversation = {"Conversation": ["Who are you?", "I am GPT-4."]}

    # Call the function under test
    m.send_message(state)

    # After sending, the user message should be cleared
    assert state.current_user_message == ""

    # Conversation should be appended with the previous user message and the stubbed answer
    assert state.conversation["Conversation"] == [
        "Who are you?",
        "I am GPT-4.",
        "Hello GPT",
        "stubbed-answer",
    ]
