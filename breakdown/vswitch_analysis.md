# Analysis of `vswitch.py`

## Introduction

The `vswitch.py` script implements a simple Layer 2 virtual Ethernet switch. It allows multiple virtual machines or network endpoints (referred to as "VPorts") to communicate with each other as if they were connected to the same physical network switch. The script listens for UDP datagrams on a specified port, treating each datagram as a raw Ethernet frame.

## Core Concepts

*   **Virtual Switch (VSwitch):** The central component (`vserver_sock`) that listens for incoming frames from all VPorts. It makes decisions on where to forward these frames.
*   **Virtual Port (VPort):** Represents a network client connected to the switch. In this script, a VPort is identified by its UDP address (IP and port combination, e.g., `('127.0.0.1', 5000)`).
*   **MAC Address Table:** A dictionary (`mac_table`) that maps the MAC (Media Access Control) address of a VPort to its UDP address. This is how the switch "learns" where to send frames.
    *   **Example:** `{'0a:0b:0c:0d:0e:0f': ('127.0.0.1', 5000)}` means the VPort with MAC address `0a:0b:0c:0d:0e:0f` is reachable at `('127.0.0.1', 5000)`.

## Script Workflow

The script operates in a continuous loop, performing the following steps for each incoming frame:

1.  **Receive Frame:** The switch listens for an incoming UDP packet (`vserver_sock.recvfrom(1518)`). The packet's data is treated as an Ethernet frame, and the sender's address is identified as the VPort.

2.  **Parse Frame:** It extracts the destination and source MAC addresses from the first 14 bytes of the Ethernet header.

3.  **Learn (MAC Table Update):**
    *   The switch inspects the frame's **source MAC address** (`eth_src`).
    *   If the source MAC is not in the `mac_table`, or if the VPort address associated with that MAC has changed, the switch adds or updates the entry. This is how the switch learns which VPort corresponds to which MAC address.
    *   **Example:** If a frame arrives from VPort `('127.0.0.1', 5001)` with a source MAC of `aa:bb:cc:dd:ee:ff`, the `mac_table` is updated: `{'aa:bb:cc:dd:ee:ff': ('127.0.0.1', 5001)}`.

4.  **Forward Frame:** The switch decides what to do with the frame based on its **destination MAC address** (`eth_dst`):

    *   **Unicast (Known Destination):** If the destination MAC is found in the `mac_table`, the frame is forwarded directly to the corresponding VPort.
        *   **Real-Life Analogy:** Sending a letter to a specific, known address.

    *   **Broadcast:** If the destination MAC is `ff:ff:ff:ff:ff:ff`, the frame is sent to *every known VPort* except for the one it came from. This is used for network-wide announcements, like an ARP request ("Who has IP address 192.168.1.10?").
        *   **Real-Life Analogy:** Making an announcement on a PA system to everyone in a building.

    *   **Unknown/Discard:** If the destination MAC is not the broadcast address and is not in the `mac_table`, the script simply discards the frame. In a real-world switch, this is called "flooding" where the frame would be sent to all ports, but for simplicity, it's discarded here.
        *   **Real-Life Analogy:** Receiving a letter with an unknown recipient address and throwing it away.

## Real-Life Communication Scenario

Imagine two Virtual Machines, **VM1** and **VM2**, connected to the `vswitch.py` running on port `8000`.

*   **VM1:** IP `192.168.1.10`, MAC `0a:0a:0a:0a:0a:0a`, VPort `('127.0.0.1', 5001)`
*   **VM2:** IP `192.168.1.11`, MAC `0b:0b:0b:0b:0b:0b`, VPort `('127.0.0.1', 5002)`

**Initial State:** The `mac_table` is empty `{}`.

**Step 1: VM1 wants to ping VM2 (192.168.1.11)**

1.  **ARP Request (Broadcast):** VM1 doesn't know VM2's MAC address, so it sends an ARP request.
    *   **Source MAC:** `0a:0a:0a:0a:0a:0a`
    *   **Destination MAC:** `ff:ff:ff:ff:ff:ff` (Broadcast)
2.  **VSwitch Receives:** The switch gets the frame from `('127.0.0.1', 5001)`.
3.  **VSwitch Learns:** It sees the source MAC `0a:0a:0a:0a:0a:0a` and updates its table:
    *   `mac_table` is now `{'0a:0a:0a:0a:0a:0a': ('127.0.0.1', 5001)}`
4.  **VSwitch Broadcasts:** Since the destination is `ff:ff:ff:ff:ff:ff`, it looks at its `mac_table`. It knows about VM1, but it will send to all *other* known VPorts. Assuming VM2 has also communicated previously, so the table is `{'0a:0a:0a:0a:0a:0a': ('127.0.0.1', 5001), '0b:0b:0b:0b:0b:0b': ('127.0.0.1', 5002)}`. The switch would forward the ARP to `('127.0.0.1', 5002)`.

**Step 2: VM2 Responds to ARP**

1.  **ARP Reply (Unicast):** VM2 receives the ARP request and sends an ARP reply directly to VM1.
    *   **Source MAC:** `0b:0b:0b:0b:0b:0b`
    *   **Destination MAC:** `0a:0a:0a:0a:0a:0a`
2.  **VSwitch Receives:** The switch gets the frame from `('127.0.0.1', 5002)`.
3.  **VSwitch Learns:** It sees the source MAC `0b:0b:0b:0b:0b:0b` and updates its table:
    *   `mac_table` is now `{'0a:0a:0a:0a:0a:0a': ('127.0.0.1', 5001), '0b:0b:0b:0b:0b:0b': ('127.0.0.1', 5002)}`
4.  **VSwitch Forwards:** The destination is `0a:0a:0a:0a:0a:0a`, which is in the `mac_table`. The switch sends the frame directly to `('127.0.0.1', 5001)`.

**Step 3: VM1 sends ICMP Packet (Ping)**

1.  **ICMP Packet (Unicast):** Now that VM1 has VM2's MAC address, it can send the ping packet.
    *   **Source MAC:** `0a:0a:0a:0a:0a:0a`
    *   **Destination MAC:** `0b:0b:0b:0b:0b:0b`
2.  **VSwitch Receives and Forwards:** The switch receives the frame. The destination `0b:0b:0b:0b:0b:0b` is in its table, so it forwards the frame directly to `('127.0.0.1', 5002)`. Communication is now efficient and direct.

## How to Run the Script

To start the virtual switch, you need to provide a port number for it to listen on.

```bash
python3 vswitch.py {VSWITCH_PORT}
```

For example:
```bash
python3 vswitch.py 8000
```
The switch will then start and print a message indicating it's running.
