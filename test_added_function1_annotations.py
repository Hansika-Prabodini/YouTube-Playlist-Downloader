import importlib


def test_annotations_deferred_import_and_string_annotation():
    # Import the module; prior to the patch this would raise NameError due to
    # evaluating the forward-referenced type annotation `State` at import time.
    mod = importlib.import_module('added_function1')

    # Ensure the function exists
    assert hasattr(mod, 'send_message'), 'send_message not found in added_function1'

    ann = mod.send_message.__annotations__

    # The annotation for 'state' should be stored as a string due to postponed evaluation
    assert 'state' in ann
    assert isinstance(ann['state'], str)
    assert ann['state'] == 'State'
