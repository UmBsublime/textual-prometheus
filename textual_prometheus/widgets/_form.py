from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button, Input
from textual_autocomplete import AutoComplete


class Form(Horizontal):
    DEFAULT_CSS = """\
    Form {
        height: auto;
        min-height: 3;
        max-width: 1fr;
        background: $boost;
    }
    Form > AutoComplete {
        width: 1fr;        
    }
    Form > Button {
        color: $secondary;
    }
    """

    def __init__(self, *inputs: Input | AutoComplete, button: Button, **kwargs):
        super().__init__(**kwargs)
        self.inputs = inputs
        self.button = button

    def compose(self) -> ComposeResult:
        yield from self.inputs
        yield self.button
