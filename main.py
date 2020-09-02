import platform
import re
import time
import uuid

import psutil
from flask import Flask, request, Response, render_template, jsonify

app = Flask(__name__)


@app.route('/stats', methods=["GET"])
def get_stats():
    info = {'system': platform.system(), 'platform-release': platform.release(),
            'platform-version': platform.version(), 'architecture': platform.machine(),
            'node': platform.node(), 'platform': platform.platform(), "num-cpus": psutil.cpu_count(),
            "num-physical-cpus: ": str(psutil.cpu_count(logical=False)),
            'mac-address': ':'.join(re.findall('..', '%012x' % uuid.getnode())), 'processor': platform.processor(),
            'ram': str(round(psutil.virtual_memory().total / (1024.0 ** 3))) + " GB"}
    if request.args.get("get_only"):
        key = request.args.get("get_only")
        info = {key: info.get(request.args.get("get_only"), "Not a valid param")}
    return jsonify(**info)


@app.route('/events')
def event_source():
    if request.headers.get('accept') == 'text/event-stream':
        def events():
            while True:
                yield 'data: {}\n\n'.format(get_message())

        return Response(events(), content_type='text/event-stream')
    else:
        c, m = get_message()
        return jsonify(**{"cpu_percent": c, "ram_usage": m})


@app.route('/')
def index():
    return render_template("index.html", info=get_stats().json)


def get_message():
    time.sleep(1.0)
    s = [psutil.cpu_percent(), dict(psutil.virtual_memory()._asdict())['percent']]
    return s


if __name__ == '__main__':
    app.run(port=4000, debug=True)
