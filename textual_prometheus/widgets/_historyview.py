from textual.containers import Container
from textual.widgets import Label, TextLog


class PopupTextLog(Container):
    DEFAULT_CSS = """\
    PopupTextLog {
        layer: history;
        scrollbar-gutter: auto;
        width: 100%;
        height: 100%;
        margin: 2 5;
        align: center middle;
        offset-x: 0;
        transition: offset 300ms in_out_cubic;
    }
    PopupTextLog:focus {
        offset: 0 0 !important;
    }
    PopupTextLog.-hidden {
        offset-x: 200%;
    }
    
    PopupTextLog > Label {
        border: hkey $primary-lighten-2;
        width: 100%;
        background: $primary-background;
        text-align: center;
        color: $secondary-darken-1;
    }
    
    PopupTextLog > TextLog {
        width: 1fr;
        height: 1fr;
        border: hkey $primary-lighten-2;
        background: $primary-background-lighten-1;
        color: $secondary-lighten-1;
        scrollbar-gutter: stable;
        scrollbar-size: 1 1;

    }
    """

    def __init__(self, title: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = title
        self.textlog = TextLog(wrap=True)

    def compose(self):
        self.add_class("-hidden")
        yield Label(self.title)
        yield self.textlog
