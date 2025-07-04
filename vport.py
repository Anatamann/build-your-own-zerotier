#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import sys
import time

def create_eth_frame(src_mac, dst_mac, payload=b"Hello from VPort"):
    """Creates a simple raw Ethernet frame."""
    # Convert "aa:bb:cc:dd:ee:ff" to b'\xaa\xbb\xcc\xdd\xee\xff'
    dst_mac_bytes = bytes.fromhex(dst_mac.replace(':', ''))
    src_mac_bytes = bytes.fromhex(src_mac.replace(':', ''))
    
    # EtherType for IPv4, though it's just a placeholder here
    ethertype = b'\x08\x00'
    
    # Frame: [Dst MAC (6)] + [Src MAC (6)] + [EtherType (2)] + [Payload]
    return dst_mac_bytes + src_mac_bytes + ethertype + payload

def main():
    if len(sys.argv) != 5:
        print("Usage: python3 vport.py {VSWITCH_IP} {VSWITCH_PORT} {SRC_MAC} {DST_MAC}")
        sys.exit(1)

    # VSwitch address
    switch_ip = sys.argv[1]
    switch_port = int(sys.argv[2])
    switch_addr = (switch_ip, switch_port)

    # VPort MACs
    src_mac = sys.argv[3]
    dst_mac = sys.argv[4]

    # Create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(1.0) # Set a 1-second timeout
    
    # The OS will assign a random source port, simulating a VPort
    
    # Create and send the frame
    frame = create_eth_frame(src_mac, dst_mac)
    sock.sendto(frame, switch_addr)
    my_addr = sock.getsockname()
    print(f"VPort at {my_addr} (MAC: {src_mac}) sent a frame to {dst_mac}.")

    # Listen for any frames forwarded by the switch
    print("Listening for incoming frames...")
    while True:
        try:
            data, sender_addr = sock.recvfrom(1518)
            
            # Parse frame to display info
            dst_mac_recv = ":".join("{:02x}".format(x) for x in data[0:6])
            src_mac_recv = ":".join("{:02x}".format(x) for x in data[6:12])
            
            print(f"\n---> Received a frame!")
            print(f"     From Switch: {sender_addr}")
            print(f"     Original Source MAC: {src_mac_recv}")
            print(f"     My MAC (Destination): {dst_mac_recv}")

        except socket.timeout:
            # This is expected when no data is received.
            # The loop continues, allowing KeyboardInterrupt to be processed.
            continue
        except KeyboardInterrupt:
            print("\nClosing VPort.")
            break

if __name__ == "__main__":
    main()