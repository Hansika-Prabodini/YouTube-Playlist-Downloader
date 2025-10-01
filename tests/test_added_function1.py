import types


class FakeState:
    def __init__(self):
        # Simulate Taipy-like state attributes
        self.current_user_message = "Hello"
        # Provide a plain dict (no _dict attribute) to ensure fallback path is used
        self.conversation = {"Conversation": ["Who are you?", "I am an AI."]}


def test_send_message_appends_and_clears_message():
    # Import the module under test
    import added_function1 as mod

    # Inject fakes for external dependencies used in send_message
    # Using simple functions assigned to the module's global namespace
    captured_notifications = []

    def fake_notify(state, level, msg):
        captured_notifications.append((level, msg))

    def fake_update_context(state):
        # Return a deterministic response
        return "Bot reply"

    def fake_on_exception(state, fn, ex):
        # Should not be called in this test
        raise AssertionError(f"on_exception called unexpectedly: {ex}")

    mod.notify = fake_notify
    mod.update_context = fake_update_context
    mod.on_exception = fake_on_exception

    state = FakeState()

    # Execute
    mod.send_message(state)

    # Verify conversation updated correctly (two new entries appended)
    assert state.conversation["Conversation"][-2:] == ["Hello", "Bot reply"]

    # Verify current_user_message cleared
    assert state.current_user_message == ""

    # Verify that notifications were sent (info and success)
    levels = [lvl for (lvl, _) in captured_notifications]
    assert "info" in levels and "success" in levels
