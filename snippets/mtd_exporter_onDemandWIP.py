# This is a skeleton server (unfinished).
# The mtd_exporter queries prometheus for every scrape. This is can generate a lot of traffic/pressure on promehetus.
# One alternative is only query if you run a GET on a particular port.
# If this is required, feel free to extend this file.

import http.server
from prometheus_client import start_http_server
from prometheus_client import Summary

import time

LATENCY = Summary('hello_world_latency_seconds', 'Time for a request Hello World.')

class Update_metrics(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        print("handler fired")
        start = time.time()
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"metrics were updated\n")
        LATENCY.observe(time.time() - start)


if __name__ == "__main__":
    print("Starting http server")
    APP_METRICS_PORT = 9000
    update_metrics = 8080

    start_http_server(APP_METRICS_PORT) # Server system metrics on port
    server = http.server.HTTPServer(('localhost', update_metrics), Update_metrics)
    server.serve_forever()