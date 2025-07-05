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

def send_frames(sock, switch_addr, src_mac, dst_mac, payload=b"Hello from VPort"):
    """Send the Ethernet frames to the client"""
    
    frame = create_eth_frame(src_mac, dst_mac, payload)
    sock.sendto(frame, switch_addr)
    
    my_addr = sock.getsockname()
    
    print(f"VPort at {my_addr} (MAC: {src_mac}) sent a frame to {dst_mac}.")

    return


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
    
    # The OS will assign a random source port, simulating a VPort
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(1.0) # Set a 1-second timeout
    
    sent = send_frames(sock, switch_addr, src_mac, dst_mac)
    if not sent:
        print("Initial frames registered successful!!...\n")
    else:
        print("Error occured while registering...")
        sys.exit()
    # Listen for any frames forwarded by the switch
    while True:
        try:
            choice = input(f"Want to send the custom msg? y/n: ")
            if choice.lower() == "y":
                custom_msg = input(f"Enter your custom message to send or hit Enter for a default mesasge:  ")
                if not custom_msg:
                    sent = send_frames(sock, switch_addr, src_mac, dst_mac)
                else:
                    msg = f'{custom_msg}'.encode('utf-8')
                    sent = send_frames(sock, switch_addr, src_mac, dst_mac, msg)
            
            print("Listening for incoming frames...")
            data, sender_addr = sock.recvfrom(1024)
            
            if not data:
                continue
            else:
                # Parse frame to display info
                dst_mac_recv = ":".join("{:02x}".format(x) for x in data[0:6])
                src_mac_recv = ":".join("{:02x}".format(x) for x in data[6:12])
                message_rcv = str(data[12:].decode('utf-8'))
                print(f"\n---> Received a frame!")
                print(f"     From Switch: {sender_addr}")
                print(f"     Original Source MAC: {src_mac_recv}")
                print(f"     My MAC (Destination): {dst_mac_recv}")
                print(f"    message: {message_rcv}")
                continue

        except socket.timeout:
            # This is expected when no data is received.
            # The loop continues, allowing KeyboardInterrupt to be processed.
            continue
        except KeyboardInterrupt:
            print("\nClosing VPort.")
            break

if __name__ == "__main__":
    main()