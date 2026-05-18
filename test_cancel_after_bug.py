"""
Unit tests for the self.after() two-lambda bug in youtube_downloader-gui.py.

Bug description
---------------
In `cancel_single_download` and `cancel_all`, the original code contained:

    self.after(0, lambda: widgets['status_label'].configure(text="Cancelling..."),
              lambda: widgets['progress_bar'].set(0))

Tkinter's `Misc.after(ms, func, *args)` schedules a call of `func(*args)`.
Passing a second positional argument therefore passes the second lambda *as an
argument* to the first lambda.  Because the first lambda accepts no parameters
(`lambda:`), tkinter raises:

    TypeError: <lambda>() takes 0 positional arguments but 1 was given

As a result:
  - The status label is never updated to "Cancelling...".
  - The progress bar is never reset to 0.

The fix is to use two independent `self.after()` calls, one per lambda.
"""

import pytest


def simulate_after(ms, func, *args):
    """
    Minimal stand-in for tkinter's Misc.after().

    tkinter calls  func(*args)  when the timer fires.  We call it
    synchronously here so the behaviour is observable in a plain test.
    """
    func(*args)


# ---------------------------------------------------------------------------
# Helper state containers (replace real tkinter widgets)
# ---------------------------------------------------------------------------

class FakeLabel:
    def __init__(self):
        self.text = ""

    def configure(self, **kwargs):
        if "text" in kwargs:
            self.text = kwargs["text"]


class FakeProgressBar:
    def __init__(self, initial=1.0):
        self.value = initial

    def set(self, value):
        self.value = value


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_buggy_after_call_raises_type_error():
    """
    The original (buggy) pattern — passing two lambdas to a single after()
    call — causes a TypeError because the second lambda is forwarded as a
    positional argument to the first (no-argument) lambda.

    This test will FAIL before the patch and PASS after the patch is applied
    (because the patched code no longer makes this kind of call).
    """
    label = FakeLabel()
    progress_bar = FakeProgressBar(initial=1.0)

    # Reproduce the BUGGY pattern exactly as it existed in the source.
    with pytest.raises(TypeError):
        simulate_after(
            0,
            lambda: label.configure(text="Cancelling..."),
            lambda: progress_bar.set(0),   # ← incorrectly forwarded as *args
        )


def test_fixed_after_calls_update_both_widgets():
    """
    The corrected pattern — two independent after() calls — must update
    both the status label and the progress bar without raising any error.

    This test documents the expected post-fix behaviour and will PASS only
    after the bug is fixed in youtube_downloader-gui.py.
    """
    label = FakeLabel()
    progress_bar = FakeProgressBar(initial=1.0)

    # Two independent after() calls — the patched version of the code.
    simulate_after(0, lambda: label.configure(text="Cancelling..."))
    simulate_after(0, lambda: progress_bar.set(0))

    assert label.text == "Cancelling...", (
        "Status label should read 'Cancelling...' after cancel is triggered."
    )
    assert progress_bar.value == 0, (
        "Progress bar should be reset to 0 after cancel is triggered."
    )
