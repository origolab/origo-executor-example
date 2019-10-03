#!/usr/bin/env python3

from __future__ import print_function

from gevent.monkey import patch_all

patch_all()

import gevent
import os
import time
from executor.zokrates_proactive_eth_executor import ZokratesProactiveEthExecutor
from executor_service.executor_task_table import TaskTable, TaskTableItem
from executor_service.service_config_util import ServiceConfigUtil
from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_sockets import Sockets
from geventwebsocket.handler import WebSocketHandler
from geventwebsocket.exceptions import WebSocketError
from gevent.pywsgi import WSGIServer


app = Flask(__name__)
sockets = Sockets(app)

config_utils = ServiceConfigUtil()

executor_container = {}

time_format = {
    'one': "%H:%M:%S",
    'best': "%a, %d %b %Y %H:%M:%S +0000",
    'other': "%a, %H:%M",
}


@app.route("/data", methods=['GET'])
def data():
    """
    Provides the server's current timestamp, formatted in several different
    ways, across a WebSocket connection. NB While other Python JSON emitters
    will directly encode arrays and other data types, Flask.jsonify() appears to
    require a dict.
    """

    fmt = request.args.get('format', 'best')

    now = time.time()

    tasks = executor_container['executor'].get_all_task_status()

    table_items = []
    for contract_address, task_status in tasks.items():
        task_status['contract_address'] = contract_address
        table_items.append(TaskTableItem(task_status))

    table = TaskTable(table_items)

    info = {'value': now,
            'contents': table.__html__(),
            'format': fmt}
    return jsonify(info)


@app.route("/register_contract/<contract_address>")
def register_contract(contract_address):
    if executor_container['executor'].register_contract(contract_address, {}):
        return "Registration succeeded"
    return "Registration failed"


@app.route("/unregister_contract/<contract_address>")
def unregister_contract(contract_address):
    if executor_container['executor'].unregister_contract(contract_address):
        return "Unregistration succeeded"
    return "Unregistration failed"


@sockets.route('/updated')
def updated(ws):
    """
    Notify the client that an update is ready. Contacted by the client to
    'subscribe' to the notification service.
    """
    if not ws:
        raise RuntimeError("Environment lacks WSGI WebSocket support")

    while not ws.closed and executor_container['executor'].is_alive():
        gevent.sleep(1)
        try:
            ws.send('ready'.encode('utf-8'))
        except WebSocketError:
            # catch the socket dead error, which is triggered by closing the browser page.
            pass


@app.route('/favicon.ico')
def favicon():
    """
    Return the favicon from static.
    """
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route("/")
def main():
    """
    Main web site entry point.
    """
    return render_template("index.html", port=config_utils.get_service_port())


if __name__ == "__main__":
    config_utils.build_configurations()

    executor_container['executor'] = ZokratesProactiveEthExecutor(config_utils.get_options(),
                                                                  debug=config_utils.get_debug_mode())
    executor_container['executor'].start()

    http_server = WSGIServer(('', config_utils.get_service_port()), app, handler_class=WebSocketHandler)
    http_server.serve_forever()
