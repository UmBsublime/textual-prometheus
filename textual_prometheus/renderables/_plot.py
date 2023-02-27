from datetime import datetime, timedelta

import plotext as plt
from rich.ansi import AnsiDecoder
from rich.console import Group
from rich.jupyter import JupyterMixin

from textual_prometheus.config import SETTINGS
from textual_prometheus.prom_api import PrometheusApi


def make_query_range_plot(width: int, height: int, instance: str, metric: str):
    api = PrometheusApi(SETTINGS.endpoint)
    plt.clear_data()
    plt.date_form('d/m/Y H:M')
    end = datetime.now()
    start = end - timedelta(days=30)
    plt.plotsize(width, height)
    data = api.parse_query_range(instance, metric, start, end, step='1h')

    for i, host in enumerate(data):
        values = [int(float(h[1])) for h in host]
        dates = plt.datetimes_to_string([datetime.fromtimestamp(h[0]) for h in host], 'd/m/Y H:M')
        plt.plot(dates, values, label=f"toto{i}")
    plt.title(f"{instance} {metric}")
    plt.xlabel("Date")
    plt.ylabel("Value")

    return plt.build()


class PlotMixin(JupyterMixin):
    def __init__(self, instance, metric=None):
        self.decoder = AnsiDecoder()
        self.instance = instance
        self.metric = metric

    def __rich_console__(self, console, options):
        self.width = options.max_width or console.width
        self.height = options.height or console.height
        try:
            self.canvas = make_query_range_plot(self.width, self.height, self.instance, self.metric)
        except IndexError as e:
            message = (
                f"Could not generate plot. Most likely no metric for that instance\n"
                f"EXCEPTION: {e}"
            )
            print(message)
            self.canvas = message
        self.rich_canvas = Group(*self.decoder.decode(self.canvas))
        yield self.rich_canvas
