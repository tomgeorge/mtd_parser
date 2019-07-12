# Starts a simple wsgi server on specified port.
# Prometheus metrics avilable on:
# http://localhost:8080/metrics

# 'app.py' name used because s2i APP_FILE defaults to this value.
# https://docs.openshift.com/container-platform/3.11/using_images/s2i_images/python.html


PORT = 8080  # todo_someday - read this from an environment var w/ a default.

import prometheus_querier
from prometheus_client import make_wsgi_app
from wsgiref.simple_server import make_server

metrics_app = make_wsgi_app()

# Currently shows average minutes. But units not hard-coded, can change to seconds etc..
def get_downtime_average():
    results = prometheus_querier.query_prometheus()
    down_time_seconds = prometheus_querier.get_downtime_average_seconds(results)
    average_seconds = sum(down_time_seconds) / len(down_time_seconds)
    average_minutes = average_seconds / 60
    print("Count: ", len(down_time_seconds), "Avg length: (minutes)", average_minutes)
    return average_minutes

from prometheus_client import Gauge
IN_PROGRESS = Gauge("mtd_myapp_mean_time_to_recover", "Average time for app to recover")
IN_PROGRESS.set_function(get_downtime_average)

def my_app(environ, start_fn):
    if environ['PATH_INFO'] == '/metrics':
        # IN_PROGRESS.inc()

        return metrics_app(environ, start_fn)
    start_fn('200 OK', [])
    return [b'Metrics are hosted at /metrics']
    # return ["how are you"]

if __name__ == '__main__':
    print("Starting server on port ", PORT)
    httpd = make_server('', PORT, my_app)
    httpd.serve_forever()