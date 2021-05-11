from http.server import HTTPServer, BaseHTTPRequestHandler
from http import HTTPStatus
import json
import urllib.request
import dateutil.parser as dp
import sys
import getopt

# curl -H "Authorization:Token <token>" "http://<ip>:7777/api/v2/datalogger/dsmrreading?limit=1&ordering=-timestamp"
#
# {"count":408509,"next":"http://<ip>:7777/api/v2/datalogger/dsmrreading?limit=1&offset=1&ordering=-timestamp","previous":null,"results":[
# {"id":601721,
# "timestamp":"2021-05-07T10:48:32+02:00",
# "electricity_delivered_1":"3691.449",
# "electricity_returned_1":"3273.813",
# "electricity_delivered_2":"4460.509",
# "electricity_returned_2":"1309.776",
# "electricity_currently_delivered":"0.243",
# "electricity_currently_returned":"0.000",
# "phase_currently_delivered_l1":"0.209",
# "phase_currently_delivered_l2":"0.000",
# "phase_currently_delivered_l3":"0.611",
# "extra_device_timestamp":"2021-05-07T10:45:29+02:00",
# "extra_device_delivered":"3492.813",
# "phase_currently_returned_l1":"0.000",
# "phase_currently_returned_l2":"0.577",
# "phase_currently_returned_l3":"0.000",
# "phase_voltage_l1":"236.5",
# "phase_voltage_l2":"236.7",
# "phase_voltage_l3":"238.4",
# "phase_power_current_l1":1,
# "phase_power_current_l2":3,
# "phase_power_current_l3":3}]}

dsmr_server = ""
dsmr_token = ""


class _RequestHandler(BaseHTTPRequestHandler):
    # Borrowing from https://gist.github.com/nitaku/10d0662536f37a087e1b
    def _set_headers(self):
        self.send_response(HTTPStatus.OK.value)
        self.send_header('Content-type', 'application/json')
        # Allow requests from any origin, so CORS policies don't
        # prevent local development.
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def do_GET(self):
        global dsmr_server
        global dsmr_token
        self._set_headers()
        content = urllib.request.urlopen(urllib.request.Request(f"http://{dsmr_server}:7777/api/v2/datalogger/dsmrreading?limit=1&ordering=-timestamp", headers = {"Authorization": f"Token {dsmr_token}"})).read()
        dsmr_data = json.loads(content)["results"][0]
        youless_data_all = list()
        youless_data = dict()
        timestamp = dp.parse(dsmr_data["timestamp"])
        tm = int(timestamp.timestamp())
        pwr = int(float(dsmr_data["electricity_currently_delivered"])*1000 - float(dsmr_data["electricity_currently_returned"])*1000)
        p1 = float(dsmr_data["electricity_delivered_1"])
        p2 = float(dsmr_data["electricity_delivered_2"])
        n1 = float(dsmr_data["electricity_returned_1"])
        n2 = float(dsmr_data["electricity_returned_2"])
        net = round(p1 + p2 - n1 - n2,3)
        content = urllib.request.urlopen(urllib.request.Request(f"http://{dsmr_server}:7777/api/v2/consumption/gas?limit=1&offset=1&ordering=-timestamp", headers = {"Authorization": f"Token {dsmr_token}"})).read()
        dsmr_data = json.loads(content)["results"][0]
        gas = float(dsmr_data["delivered"])
        youless_data_all.append(youless_data)
        #self.wfile.write(content)
        youless_data["tm"] = tm
        youless_data["net"] = net
        youless_data["pwr"] = pwr
        youless_data["p1"] = p1
        youless_data["p2"] = p2
        youless_data["n1"] = n1
        youless_data["n2"] = n2
        youless_data["gas"] = gas
        self.wfile.write(json.dumps(youless_data_all, separators=(',', ':')).encode('utf-8'))

    def do_OPTIONS(self):
        # Send allow-origin header for preflight POST XHRs.
        self.send_response(HTTPStatus.NO_CONTENT.value)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.send_header('Access-Control-Allow-Headers', 'content-type')
        self.end_headers()


def run_server(argv):
    port = '8811'
    global dsmr_server
    global dsmr_token
    try:
        opts, args = getopt.getopt(argv, "hs:t:p:", ["server=", "token=", "port="])
    except getopt.GetoptError:
        print('p1server.py -s <dsmr_server_ip> -t <dsmr_token> -p <dsmr_port>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('p1server.py -s <dsmr_server_ip> -t <dsmr_token> -p <dsmr_port>')
            sys.exit()
        elif opt in ("-s", "--server"):
            dsmr_server = arg
        elif opt in ("-t", "--token"):
            dsmr_token = arg
        elif opt in ("-p", "--port"):
            port = int(arg)
    server_address = ('', port)
    if len(dsmr_server) == 0 or len(dsmr_token) == 0:
        print('p1server.py -s <dsmr_server_ip> -t <dsmr_token> -p <dsmr_port>')
        sys.exit()
    print(f"Running p1server on port {port} using dsmr server {dsmr_server} and token {dsmr_token}")
    httpd = HTTPServer(server_address, _RequestHandler)
    print('serving at %s:%d' % server_address)
    httpd.serve_forever()


if __name__ == '__main__':
    run_server(sys.argv[1:])
