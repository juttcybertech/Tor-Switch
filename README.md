# 🛡️ Tor-Switch

<p align="center">
  <img src="https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black" alt="Linux" />
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Tor_Project-7D4698?style=for-the-badge&logo=tor-project&logoColor=white" alt="Tor" />
  <img src="https://img.shields.io/badge/Security-Shield-00b4d8?style=for-the-badge" alt="Security" />
</p>

> **A professional-grade, transparent Tor routing utility. Features a hard-coded Kill Switch, DNS leak protection, and real-time circuit monitoring without relying on third-party scripts.**

---

## 📸 Preview
![Switch To Tor Screenshot](screenshort/pic.png)
*Modern TUI (Terminal User Interface) built for clarity and speed.*

---

## ✨ Key Features

* **🌐 Full System Tunneling** – Automatically routes all TCP traffic through the Tor network.
* **🚫 Fail-Safe Kill Switch** – Prevents "Clear-Net" data leaks by dropping all traffic if the Tor service fails.
* **🛡️ Multi-Layer Leak Protection** – Hardened rules to block **IPv4**, **IPv6**, and **DNS** deanonymization attempts.
* **📊 Live Status Dashboard** – Monitor your active Exit IP, Country, and Tor Relay status in real-time.
* **⚡ Native Implementation** – Direct integration with `iptables` and `stem`; no need for Anonsurf.

---

## 🛠️ System Requirements

| Component | Requirement |
| :--- | :--- |
| **Operating System** | 🐧 Linux (Debian, Ubuntu, Kali, Parrot OS) |
| **Language** | 🐍 Python 3.8+ |
| **Permissions** | 🔑 Root / Sudo (Required for network routing) |
| **Dependencies** | `tor`, `iptables`, `iproute2` |

---

## 🚀 Installation & Usage

Follow these steps to set up **Tor-Switch** on your machine:

### 1. Update & Install Core Dependencies
```bash
sudo apt update && sudo apt install -y tor iptables python3 python3-pip
```bash
pip3 install requests stem rich
Bash
git clone [https://github.com/juttcybertech/Tor-Switch.git](https://github.com/juttcybertech/Tor-Switch.git)
cd Tor-Switch
Bash
sudo python3 switch_to_tor.py
🧪 Verified Environments
Tested and confirmed stable on the following distributions:

Parrot Security

Kali Linux

Ubuntu / Debian

⚖️ Legal Disclaimer
[!WARNING]

This tool is developed for educational and privacy research purposes only. The developers are not responsible for any misuse or illegal activities conducted with this software. Always ensure you are in compliance with your local regulations.

<p align="center">
<b>Developed by JuttCyberTech</b>


<i>Securing your footprint, one hop at a time.</i>
</p>
