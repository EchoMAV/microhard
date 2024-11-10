# MONARK_Management

## Description
This repo contains code which manages the provisioning and management of MONARK drones via USB-C connection from the GCS. The command suite is designed to interface with Microhard radios on the MONARK through 'AT' commands.

## Design
`GCSSerialListener` runs as a service on the RPi. It continually listens for incoming serial data on `SERIAL_PATH`. The incoming data is then parsed and handled by `MicrohardService`.
