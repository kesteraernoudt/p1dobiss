## About

This is a simple python script connecting the dobiss NXT server to a dsmr-reader server for energy monitoring.

## Usage

To use this script, you need to have either:
* an existing dsmr-reader running, with API enabled.
* home assistant with the dsmr integration

The available options are:
-p <port> -s <server_ip> -t <server_token> -o dsmr_reader|HA -S false|true

* -p or --port: which port this process will listen to
* -o or --type: the server type this script will get its data from: either dsmr_reader or HA
* -s or --server: the IP of the server you connect to - either HA or dsmr-reader
* -t or --token: the API token or long lived token for authentication to the server above
* -S or --secure: use https or http - set to true or false

Then run this script - the easiest way to use this is docker:

For the dsm_reader version, run this:

docker run -it --rm -p 8811:8811 --name p1dobiss kesteraernoudt/p1dobiss -p 8811 -s <server_ip> -t <server_token> -o dsmr_reader -S false|true

For the Home Assistant version, run this:

docker run -it --rm -p 8811:8811 --name p1dobiss kesteraernoudt/p1dobiss -p 8811 -s <server_ip> -t <server_token> -o HA -S false|true

