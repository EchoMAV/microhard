#!/usr/bin/env python3

from constants import (
    RSSI_SOCKET_HOST,
    RSSI_SOCKET_PORT,
)
import socket

"""
This service sends RSSI data over a socket connection to the mavproxy app.
"""


class SocketService:
    @staticmethod
    def send_data_out(data: str) -> bool:
        """
        Used to send data out over another host:port client socket connection.
        """
        is_success = False

        try:
            print(f"Attempting to send data: {data}")
            _data = data.strip().encode()
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((RSSI_SOCKET_HOST, RSSI_SOCKET_PORT))
            client_socket.sendall(_data)
            is_success = True
        except Exception as e:
            print(f"{RSSI_SOCKET_HOST}:{RSSI_SOCKET_PORT} {e}")
        finally:
            client_socket.close()

        return is_success
