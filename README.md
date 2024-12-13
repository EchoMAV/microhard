## Description
This repo contains code which runs on the RPi on the MONARK and communicates with the onboard Microhard radio over SSH. Generally speaking, information is extracted from the Microhard module via AT commands and processed in python.

## Design
For pairing, EchoMAV QGC will present a QR code which the drone's camera will scan and use the extracted info to perform AT commands over SSH into the Microhard.
For RSSI signaling, a service gets setup on the RPi which periodically sends `RADIO_STATUS` mavlink messages which a GCS like ATAK can ingest and render meaningfully to the user.


# MONARK_Management (Software Updates)
`monark.py` also has an action type which is designed to run as a background service on the pi and periodically poll for sd card activity. If detected, it will take care of auto mounting and configuring for two cases:
1. If only a file called `update.zip` is present then it is mounted in readonly mode and the file will be extracted and the containing `update.sh` script will be executed.
2. Otherwise, the sd card will be mounted in read/write mode so that high res photos/videos can be saved on it.
