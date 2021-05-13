## About

This is a simple python script connecting the dobiss NXT server to a dsmr-reader server for energy monitoring.

## Usage

To use this script, you need to have either:
* an existing dsmr-reader running, with API enabled.
* home assistant with the dsmr integration

Then run this script - the easiest way to use this is docker:

For the dsm_reader version, run this:

docker run -it --rm -p 8811:8811 --name p1dobiss kesteraernoudt/p1dobiss -p 8811 -s <server_ip> -t <server_token> -o dsmr_reader

For the Home Assistant version, run this:

docker run -it --rm -p 8811:8811 --name p1dobiss kesteraernoudt/p1dobiss -p 8811 -s <server_ip> -t <server_token> -o HA

