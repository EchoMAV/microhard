# MONARK_Management

## Description
This repo contains code which runs on the RPi on the MONARK and communicates with the onboard Microhard radio over SSH. Generally speaking, information is extracted from the Microhard module via AT commands and processed in python.

## Design
For pairing, EchoMAV QGC will invoke commands via the command line which in turn translates into AT commands over SSH into the Microhard.
For RSSI signaling, a service gets setup on the RPi which periodically sends `RADIO_STATUS` mavlink messages which a GCS like ATAK can ingest and render meaningfully to the user.

## Deployment
### Make a monark user
### Update monark bashrc
### copy all .py files from this repo into /usr/local/monark and chmod +x
