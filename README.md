I used a software called VSPE (Virtual Serial Port Emulator) to simulate virtual ports.
In this software, I created a port pair, which consists of two ports connected to each other.
This means that if information is sent to one port, it will be received by the other port.
To set this up, I sent data from Python into one port, and connected the other port to the Arduino via COMPIM (a tool for serial communication with virtual ports).
This way, the information from Python was successfully transmitted to the Arduino for further processing.
