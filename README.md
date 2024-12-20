## Description
This repo contains code which runs on the RPi on the MONARK and communicates with the onboard Microhard radio over SSH. Generally speaking, information is extracted from the Microhard module via AT commands and processed in python.

## Design
For pairing, EchoMAV QGC will present a QR code which the drone's camera will scan and use the extracted info to perform AT commands over SSH into the Microhard.
For RSSI signaling, a service gets setup on the RPi which periodically sends `RADIO_STATUS` mavlink messages which a GCS like ATAK can ingest and render meaningfully to the user.


## Building
Run `./make_debian.sh` to build and install `microhard` deb package.
