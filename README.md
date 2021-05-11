## About

This is a simple python script connecting the dobiss NXT server to a dsmr-reader server for energy monitoring.

## Usage

To use this script, you need to have an existing dsmr-reader running, with API enabled.

Then run this script - the easiest way to use this is docker:

docker run -it --rm -p 8811:8811 --name p1dobiss kesteraernoudt/p1dobiss -p 8811 -s <dsmr_ip> -t <dsmr_token>


