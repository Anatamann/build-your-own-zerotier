# Testing `vswitch.py` on WSL2

This guide explains how to test the `vswitch.py` script on a Windows 10 machine with WSL2 by simulating two virtual network ports (VPorts).

## The Plan

1.  **Create a VPort Client Script:** A Python script named `vport.py` will act as a virtual machine, creating and sending a basic Ethernet frame over UDP.
2.  **Set up the Environment:** We will use three separate WSL2 terminals to simulate a network:
    *   **Terminal 1:** Will run the `vswitch.py` (the switch).
    *   **Terminal 2:** Will run `vport.py` as "VM1".
    *   **Terminal 3:** Will run `vport.py` as "VM2".
3.  **Run the Test:** We'll walk through sending frames and observe how the switch learns MAC addresses and forwards traffic.

---

## Step 1: The VPort Client Script (`vport.py`)

This script allows you to specify a source MAC, a destination MAC, and the switch's address to send a test Ethernet frame. It has already been created in `/home/vport.py`.

*Code for `vport.py` (for reference):*
---

## Step 2: Set Up Your Terminals

Open **three separate WSL2 terminals**.

#### In Terminal 1 (The Switch):

1.  Navigate to your project directory:
    ```bash
    cd /home
    ```
2.  Start the virtual switch and have it listen on port `8000`:
    ```bash
    python3 vswitch.py 8000
    ```
    You will see a message like `[VSwitch] Started at 0.0.0.0:8000`. It is now waiting for frames.

#### In Terminal 2 (Virtual Machine 1):

1.  Navigate to your project directory:
    ```bash
    cd /home
    ```
2.  Get ready to run `vport.py`. We will use this terminal to send a frame *from* MAC `0a:0a:0a:0a:0a:0a` *to* MAC `0b:0b:0b:0b:0b:0b`.

#### In Terminal 3 (Virtual Machine 2):

1.  Navigate to your project directory:
    ```bash
    cd /home
    ```
2.  This terminal will also run `vport.py`, but it will act as the recipient. It will listen for frames destined for `0b:0b:0b:0b:0b:0b`.

---

## Step 3: Run the Test & Observe

Now we'll simulate a conversation.

### A. VM1 Sends a Frame to VM2 (Switch Learns about VM1)

*   **In Terminal 2 (VM1), execute:**
    ```bash
    python3 vport.py 127.0.0.1 8000 0a:0a:0a:0a:0a:0a 0b:0b:0b:0b:0b:0b
    ```

*   **What to Expect:**
    *   **Terminal 2 (VM1) Output:** It will say it sent a frame and is now listening.
    *   **Terminal 1 (Switch) Output:** The switch will see the frame, print the source and destination MACs, and **add VM1's MAC to its table**. Since it doesn't know `0b:0b:0b:0b:0b:0b` yet, it will print `Discarded`.
        ```
        [VSwitch] vport_addr<('127.0.0.1', 54321)> src<0a:0a:0a:0a:0a:0a> dst<0b:0b:0b:0b:0b:0b> ...
            ARP Cache: {'0a:0a:0a:0a:0a:a': ('127.0.0.1', 54321)}
            Discarded
        ```

### B. VM2 Sends a Frame to VM1 (Switch Learns about VM2 and Forwards)

*   **In Terminal 3 (VM2), execute:**
    ```bash
    python3 vport.py 127.0.0.1 8000 0b:0b:0b:0b:0b:0b 0a:0a:0a:0a:0a:0a
    ```

*   **What to Expect:**
    *   **Terminal 3 (VM2) Output:** It will say it sent a frame and is now listening.
    *   **Terminal 1 (Switch) Output:**
        1.  The switch sees the frame from VM2.
        2.  It **learns VM2's MAC address** and adds it to the table. The table now contains both MACs.
        3.  The destination `0a:0a:0a:0a:0a:0a` is now in its table, so it prints **`Forwarded to: 0a:0a:0a:0a:0a:0a`**.
    *   **Terminal 2 (VM1) Output:** VM1, which has been listening, will suddenly print a message saying **`---> Received a frame!`**, showing the details of the frame sent by VM2.

This completes the test. You have successfully simulated a basic network exchange, demonstrating that the switch learns MAC addresses and forwards frames correctly between VPorts.

```