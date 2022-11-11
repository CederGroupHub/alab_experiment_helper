"""
The script to launch task_view and executor, which are the core of the system.
"""

import multiprocessing
import sys
import time
from threading import Thread

from gevent.pywsgi import WSGIServer

try:
    multiprocessing.set_start_method("spawn")
except RuntimeError:
    pass


def launch_dashboard(host: str, port: int, debug: bool = False):
    from alab_experiment_helper.dashboard import create_app

    if debug:
        print("Debug mode is on, the dashboard will be served with CORS enabled!")
    app = create_app(cors=debug)  # if debug enabled, allow cross-origin requests to API
    if debug:
        server = WSGIServer((host, port), app)  # print server's log on the console
    else:
        server = WSGIServer((host, port), app, log=None, error_log=None)
    server.serve_forever()


def launch_batching_worker():
    from alab_experiment_helper.batching import QueueWorker

    worker = QueueWorker()
    worker.run()


def launch_server(host, port, debug):
    dashboard_thread = Thread(
        target=launch_dashboard, args=(host, port, debug), daemon=True
    )
    batching_thread = Thread(target=launch_batching_worker, daemon=True)
    # task_launcher_thread = Thread(target=launch_task_manager)
    # device_manager_thread = Thread(target=launch_device_manager)

    dashboard_thread.start()
    batching_thread.start()

    while True:
        time.sleep(1)
        if not batching_thread.is_alive():
            sys.exit(1001)

        if not dashboard_thread.is_alive():
            sys.exit(1001)
