# The below are sample commands to run the monark.py script:
"""
Get info about the microhard default radio
    python monark.py --action=info --encryption_key="admin"
Start the pairing process
    python monark.py --action=pair --network_id="MONARK-123" --encryption_key="echomavechomav" --tx_power=15 --frequency=2311
Get the status on the pairing process
    python monark.py --action=pair_status
Get info after the pairing
    python monark.py --action=info --encryption_key="echomavechomav"
Update frequency
    python monark.py --action=update --frequency=1800 --encryption_key="echomavechomav" --verbose
Update tx power
    python monark.py --action=update --tx_power=10 --encryption_key="echomavechomav" --verbose
Update encryption key
    python monark.py --action=update --encryption_key="echomavechomav" --new_encryption_key="echomavechomav1"

MicrohardService(action='pair', verbose=True).pair_monark('MONARK-123', 'admin', 15, 2310)
"""