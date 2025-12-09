# 🔒 Tor Switch

> **A secure, transparent Tor routing tool with a built-in kill switch, leak protection, and real-time monitoring.  
No third-party anonymization frameworks required.**

![Switch To Tor Screenshot](screenshort/pic.png)  
*A modern terminal-based Tor anonymization utility for Linux systems.*

---

## ✨ Features

- **Full System Tor Routing**  
  All traffic is transparently routed through Tor without manual browser configuration.

- **Kill Switch**  
  Automatically blocks all traffic if Tor disconnects to prevent deanonymization.

- **IPv4 and IPv6 Leak Protection**

- **DNS Leak Protection**

- **Real-Time IP Rotation Dashboard**  
  Monitor your current exit IP, country, and Tor circuit status live.

- **Leak Detection and Validation**

- **No Dependency on Anonsurf or Third-Party Tools**

- **Beautiful TUI**  
  Built using Rich for a clean, interactive interface.

---

## ⚠️ Requirements

- Linux OS  
  Recommended: Debian, Ubuntu, Kali, Parrot OS

- Python 3.8 or newer

- Root access (sudo)

- Required packages:  
  tor, iptables, iproute2

---

## 📦 Installation

Install system dependencies:

```bash
sudo apt update
sudo apt install -y tor iptables python3 python3-pip
```
Install Python dependencies:
```bash
pip3 install requests stem rich
```

Clone the repository:
```bash
git clone https://github.com/juttcybertech/Tor-Switch.git
cd Tor-Switch
```

▶️ Usage

Run the tool with root privileges:
```bash
sudo python3 switch_to_tor.py
```

Tested and confirmed working on:

* Parrot OS
* Kali Linux
* Ubuntu and Debian

🛡️ Disclaimer

This tool is created strictly for privacy, research, and educational purposes.
Misuse for illegal activity is prohibited.
