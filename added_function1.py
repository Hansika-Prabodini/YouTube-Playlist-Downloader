+from typing import Any
+
+
+def send_message(state: Any) -> None:
+    """
+    Send the user's message to the API and update the context.
+
+    Args:
+        state: The current state of the app.
+    """
+    # Don't process empty messages
+    if not getattr(state, "current_user_message", "").strip():
+        notify(state, "warning", "Please enter a message")
+        return
+
+    try:
+        notify(state, "info", "Sending message...")
+        answer = update_context(state)
+        # Safely copy the conversation whether it's a plain dict or an object with a _dict attribute
+        conv_source = getattr(state.conversation, "_dict", state.conversation)
+        conv = dict(conv_source)
+        conv["Conversation"] += [state.current_user_message, answer]
+        state.current_user_message = ""
+        state.conversation = conv
+        notify(state, "success", "Response received!")
+    except Exception as ex:
+        on_exception(state, "send_message", ex)
