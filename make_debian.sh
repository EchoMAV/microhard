#!/bin/bash
# create and install debian file if `microhard`

set -e

SUDO=$(test ${EUID} -ne 0 && which sudo)

$SUDO apt install -y python3-paramiko

cd "microhard"
# copy this so we can call `microhard` from anywhere without .py added to it
$SUDO cp usr/lib/python3.11/dist-packages/microhard/microhard.py usr/bin/microhard
$SUDO chmod 755 usr/bin/microhard
dpkg-deb --root-owner-group --build . ../
cd ..
$SUDO apt install ./microhard_* --reinstall
