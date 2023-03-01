from datetime import datetime, timedelta
from os import path

import requests

from textual_prometheus.config import SETTINGS


# TODO: So much to do here, currently only very
#       minimal queries are supported
class PrometheusApi:
    def __init__(self, url: str = ""):
        self.url = url
        self.headers = {'accept': 'application/json'}

    def query_range(self, query: str, start: datetime | None = None, end: datetime | None = None, step: str = '1h'):
        if not end:
            end = datetime.now()
        if not start:
            start = end - timedelta(days=30)

        start = start.strftime('%s')
        end = end.strftime('%s')
        query_params = {
            "query": query,
            "start": start,
            "end": end,
            "step": step
        }
        r = requests.get(
            path.join(self.url, "query_range"),
            params=query_params,
            headers=self.headers,
            verify=SETTINGS.verify_cert
        )
        if r.ok:
            return r.json()

        print(r.text)

    def parse_query_range(
        self,
        instance: str,
        metric: str,
        start: datetime = '',
        end: datetime = '',
        step: str = '1h'
    ) -> list[list]:
        query_params = {
            "query": f"{{__name__=~'{metric}', instance=~'{instance}'}}",
            "start": start,
            "end": end,
            "step": step
        }
        res = self.query_range(**query_params)
        if res:
            results = [v['values'] for v in res['data']['result']]
            if results:
                return results
        return [[]]

    def get_label_values(self, label="__name__"):
        end = datetime.now()
        start = end - timedelta(hours=1)
        h = {'accept': 'application/json'}
        p = {'start': datetime.timestamp(start), 'end': datetime.timestamp(end)}
        result = requests.get(
            path.join(self.url, f'label/{label}/values'),
            headers=h,
            params=p,
            verify=SETTINGS.verify_cert
        )
        if result.ok:
            return sorted(result.json().get('data', []))
        else:
            print(result.text)
        return []

    def get_instance_list(self):
        values = self.get_label_values('instance')
        output = []
        for v in values:
            if SETTINGS.instance_blacklist:
                if value_in_list(v, SETTINGS.instance_blacklist):
                    continue
            if SETTINGS.instance_whitelist:
                if value_in_list(v, SETTINGS.instance_whitelist):
                    output.append(v)
            else:
                output.append(v)
        return sorted(output)


def value_in_list(value, alist):
    for v in alist:
        if v in value:
            return True
    return False
