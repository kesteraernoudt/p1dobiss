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

server = ""
token = ""
secure = False

def get_url(server, secure):
    if secure:
        return f"https://{server}"
    return f"http://{server}"

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
        global server
        global token
        global secure
        self._set_headers()
        content = urllib.request.urlopen(urllib.request.Request(f"{get_url(server, secure)}:7777/api/v2/datalogger/dsmrreading?limit=1&ordering=-timestamp", headers = {"Authorization": f"Token {token}"})).read()
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
        content = urllib.request.urlopen(urllib.request.Request(f"{get_url(server, secure)}:7777/api/v2/consumption/gas?limit=1&ordering=-read_at", headers = {"Authorization": f"Token {token}"})).read()
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


class _HARequestHandler(BaseHTTPRequestHandler):
    # Borrowing from https://gist.github.com/nitaku/10d0662536f37a087e1b
    def _set_headers(self):
        self.send_response(HTTPStatus.OK.value)
        self.send_header('Content-type', 'application/json')
        # Allow requests from any origin, so CORS policies don't
        # prevent local development.
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
    
    def get_timestamp(self, sensor):
        global server
        global token
        global secure
        content = urllib.request.urlopen(
            urllib.request.Request(f"{get_url(server, secure)}:8123/api/states/sensor.{sensor}", 
            headers = {"Authorization": f"Bearer {token}"})
            ).read()
        answer = json.loads(content)
        return answer["last_changed"]

    def get_data(self, sensor):
        global server
        global token
        global secure
        address = f"{get_url(server, secure)}:8123/api/states/sensor.{sensor}"
        header = f"Bearer {token}"
        #print(f"getting {address}")
        #print(f"with header {header}")
        content = urllib.request.urlopen(
                urllib.request.Request(url = address, headers = {"Authorization": header})
            ).read()
        answer = json.loads(content)
        return answer["state"]

    def do_GET(self):
        global server
        global token
        self._set_headers()
        youless_data_all = list()
        youless_data = dict()
        p1 = float(self.get_data("energy_consumption_tarif_1"))
        p2 = float(self.get_data("energy_consumption_tarif_2"))
        n1 = float(self.get_data("energy_production_tarif_1"))
        n2 = float(self.get_data("energy_production_tarif_2"))
        current_cons = float(self.get_data("power_consumption"))
        current_prod = float(self.get_data("power_production"))
        gas = float(self.get_data("gas_consumption"))
        timestamp = self.get_timestamp("energy_consumption_tarif_1")
        
        tm = int(dp.parse(timestamp).timestamp())
        pwr = int(current_cons*1000 - current_prod*1000)
        net = round(p1 + p2 - n1 - n2, 3)
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

def show_usage():
        print('p1server.py -s <server_ip> -t <token> -S True|False [-o HA] [-p <port>]')
        print('    -o HA will use dsmr integration in HA, otherwise dsmr_reader api is used')
        print('    -S or --secure: boolean, use https or http')

def run_server(argv):
    port = 8811
    global server
    global token
    global secure
    server_type = "dsmr_reader"
    try:
        opts, args = getopt.getopt(argv, "hs:t:p:o:S:", ["server=", "token=", "port=", "type=", "secure="])
    except getopt.GetoptError:
        show_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            show_usage()
            sys.exit()
        elif opt in ("-s", "--server"):
            server = arg
        elif opt in ("-t", "--token"):
            token = arg
        elif opt in ("-p", "--port"):
            port = int(arg)
        elif opt in ("-o", "--type"):
            server_type = arg
        elif opt in ("-S", "--secure"):
            secure = arg.lower() in ['true', '1', 't', 'y', 'yes']
    server_address = ('', port)
    if len(server) == 0 or len(token) == 0:
        show_usage()
        sys.exit()
    print(f"Running p1server on port {port} using server {server} (secure = {secure}; type = {server_type}) and token {token}")
    if server_type == "HA":
        httpd = HTTPServer(server_address, _HARequestHandler)
    else:
        httpd = HTTPServer(server_address, _RequestHandler)
    print('serving at %s:%d' % server_address)
    httpd.serve_forever()


if __name__ == '__main__':
    run_server(sys.argv[1:])
