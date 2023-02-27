from textual import events
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Button, Footer, Header, Input, Static
from textual_autocomplete import AutoComplete, Dropdown, DropdownItem

from textual_prometheus.config import SETTINGS
from textual_prometheus.prom_api import PrometheusApi
from textual_prometheus.renderables import PlotMixin
from textual_prometheus.widgets import Form, PopupTextLog


def get_list_autocomplete(alist: list[str]) -> list[DropdownItem]:
    return [DropdownItem(i) for i in alist]


class TProm(App):
    """Textual prometheus query tool"""
    TITLE = "Prometheus Query Tool"
    SUB_TITLE = "Work in progress"
    CSS_PATH = "tprom.scss"
    BINDINGS = [
        ("ctrl+q", "quit", "Quit"),
        ("p", "screenshot", "Take Screenshot"),
        ("ctrl+r", "clear", "Clear all fields"),
        Binding("ctrl+r", "reset", "Reset", show=True, priority=True),
        ("ctrl+l", "app.toggle_class('PopupTextLog', '-hidden')", "History"),
    ]

    def compose(self) -> ComposeResult:
        """Compose our UI."""
        api = PrometheusApi(SETTINGS.endpoint)
        instances = api.get_instance_list()
        metrics = api.get_label_values()

        yield Header(classes="main_layer")
        with Form(button=Button("Run query", id="run-button"), id="form", classes="main_layer"):
            yield AutoComplete(
                Input(id="search-server", placeholder=SETTINGS.endpoint),
                Dropdown(items=get_list_autocomplete(SETTINGS.endpoints), id="server-picker"),
                id='autocomplete-server'
            )
            yield AutoComplete(
                Input(id="search-instance", placeholder="Select an instance"),
                Dropdown(items=get_list_autocomplete(instances), id="instance-picker"),
                id='autocomplete-instance'
            )
            yield AutoComplete(
                Input(id="search-metric", placeholder="Select a metric"),
                Dropdown(items=get_list_autocomplete(metrics), id="metric-picker"),
                id='autocomplete-metric'
            )
        yield Static(self.TITLE, id='prom-plot', classes="main_layer")
        yield PopupTextLog(title="History")
        yield Footer()

    def action_reset(self):
        for i in self.query_one(Form).query(Input):
            i.value = ""
        self.query_one('#search-server', Input).placeholder = SETTINGS.endpoint
        self.query_one('#prom-plot', Static).update(self.TITLE)

    def on_mount(self, event: events.Mount) -> None:
        self.query_one("#search-instance").focus()

    def on_key(self, event: events.Key) -> None:
        # TODO: move this logic in the Form
        # TODO: very wonky to do this on _every_ key
        #       would be much better to tie into Button.on_input_submitted
        server = self.query_one("#search-server", Input).value

        if server in SETTINGS.endpoints:
            if server is not SETTINGS.endpoint:
                SETTINGS.endpoint = server
                api = PrometheusApi(SETTINGS.endpoint)

                instances = api.get_instance_list()
                metrics = api.get_label_values()

                # TODO: getting the autocomplete list is blocking
                #       need to figure out how to handle in a thread _or_
                #       at the very least pop a "loading" modal screen
                self.query_one('#instance-picker', Dropdown).items = get_list_autocomplete(instances)
                self.query_one('#metric-picker', Dropdown).items = get_list_autocomplete(metrics)
                self.action_reset()
                self.query_one('#search-server', Input).value = SETTINGS.endpoint

    def on_button_pressed(self, event: Button.Pressed) -> None:
        # TODO: move this logic to the Form
        if event.button.id == "run-button":
            host = self.query_one("#search-instance", Input).value
            metric = self.query_one("#search-metric", Input).value
            plot = PlotMixin(host, metric)
            self.query_one("#prom-plot", Static).update(plot)

            self.query_one(PopupTextLog).textlog.write(
                f"---\n[RUN] server: {SETTINGS.endpoint}, instance: {host}, metric: {metric}"
            )
            self.query_one(PopupTextLog).textlog.write(plot)


def main():
    print("Warming up...")
    print(TProm().run())


if __name__ == "__main__":
    main()
