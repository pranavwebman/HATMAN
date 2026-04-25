# HATMAN
# 🕵️ Hatman - Web Reconnaissance Scanner

[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Termux](https://img.shields.io/badge/Termux-Compatible-brightgreen.svg)](https://termux.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-4.0-red.svg)]()

> **Advanced, colorful, interactive web reconnaissance scanner with HTML reporting.**  
> Designed for **Termux** and any Linux environment. No heavy dependencies – pure Python.

![Hatman Banner](https://i.ibb.co/FL7SDwWL/hat.png)  
*(Replace with your actual banner image URL if desired)*

---

## 📌 Table of Contents

- [✨ Features](#-features)
- [📦 Installation](#-installation)
- [🚀 Usage](#-usage)
- [📊 Output & Reports](#-output--reports)
- [🔧 Advanced Options](#-advanced-options)
- [🖼️ Screenshots](#️-screenshots)
- [📝 Examples](#-examples)
- [🤝 Contributing](#-contributing)
- [📜 License](#-license)

---

## ✨ Features

| Module | Capability |
|--------|------------|
| **DNS Recon** | A, AAAA, MX, NS, TXT, SOA, Reverse DNS |
| **Port Scanning** | 18+ common ports, service detection, banner grabbing (sanitized) |
| **Web Enumeration** | Title extraction, technology fingerprinting (30+ engines: React, Angular, WordPress, etc.) |
| **Subdomain Discovery** | 52+ common subdomains + custom wordlist support |
| **Directory Bruteforce** | 35+ interesting paths (admin, backup, config, etc.) |
| **Security Headers** | CSP, HSTS, X‑Frame‑Options, etc. |
| **WHOIS Lookup** | Registrar, creation/expiry dates, name servers |
| **Interactive HTML Report** | Collapsible sections, port filters, clickable links – replaces JSON |
| **Colorful Animation** | Per‑character typing effect (toggle‑able) with ANSI colors |
| **Thread‑safe Output** | No more gibberish or mangled lines during port scanning |

---

## 📦 Installation

### On Termux (Android)
```bash
pkg update && pkg upgrade
pkg install python git
git clone https://github.com/pranavwebman/HATMAN.git
cd HATMAN
pip install requests dnspython
python hatman.py --help
```

### On Linux (Debian/Ubuntu)
```bash
sudo apt update
sudo apt install python3 python3-pip git
git clone https://github.com/pranavwebman/HATMAN.git
cd HATMAN
pip3 install requests dnspython
python3 hatman.py --help
```

> **Note:** No `sudo` is required inside Termux. The scanner works fully offline except for WHOIS lookups.

---

## 🚀 Usage

```bash
python hatman.py <target> [options]
```

### Basic Examples

| Command | Description |
|---------|-------------|
| `python hatman.py example.com` | Full scan (DNS, ports, web, subdomains, dirs, headers, WHOIS) + HTML report |
| `python hatman.py example.com --quick` | Quick scan: only common ports (80,443,22,21,53,8080) and web enumeration |
| `python hatman.py example.com --no-animation` | Disable letter‑by‑letter typing for faster output |
| `python hatman.py 192.168.1.1` | Scan an IP address instead of domain |

### Output Files

After a scan, you will get an **HTML report** named:  
`hatman_report_<target>_<timestamp>.html`

Open it in any browser:

```bash
firefox hatman_report_example.com_1700000000.html
# or on Termux:
termux-open hatman_report_example.com_1700000000.html
```

No JSON file is created unless you modify the code – everything is now in the interactive HTML.

---

## 📊 Output & Reports

The HTML report includes:

- 🔍 **DNS Records** – Expandable section with all found records.
- 🔒 **Open Ports** – Interactive table with **filter buttons** (All / Web / Database / Other).
- 🌐 **Web Servers** – Status codes, server headers, extracted titles, and detected technologies.
- 🔗 **Subdomains** – List of live subdomains.
- 📁 **Interesting Directories** – Clickable URLs to discovered paths (admin, backup, etc.).
- 🛡️ **Security Headers** – Missing or present headers with explanations.
- 📜 **WHOIS Information** – Registrar, creation date, expiry, and name servers.

All sections are **collapsible** and styled for dark mode.

---

## 🔧 Advanced Options

While the tool is designed to be simple, you can extend it by editing the wordlists inside the script (`subdomain_scan` and `directory_bruteforce` methods).  
Future versions may support external wordlist files.

### Color Codes in Terminal

| Color | Meaning |
|-------|---------|
| 🟢 Green | Success (open ports, found subdomains, valid endpoints) |
| 🔴 Red | Errors / Missing (no records, connection failures, missing headers) |
| 🟡 Yellow | Informational / Progress (scanning ports, starting modules) |
| 🔵 Blue | Target info |
| 🟣 Magenta | Section headers |
| ⚪ Gray | WHOIS / banner details |

---

## 🖼️ Screenshots

### Terminal Output (with animation)
![Terminal Animation](https://via.placeholder.com/800x400?text=Animated+Colorful+Output)  
*(Replace with actual screenshot)*

### HTML Report (Interactive)
![HTML Report](https://via.placeholder.com/800x400?text=HTML+Report+with+Buttons)  
*(Replace with actual screenshot)*

---


---

## 🤝 Contributing

Contributions are welcome! Follow these steps:

1. Fork the repository.
2. Create a new branch (`feature/amazing-feature`).
3. Commit your changes.
4. Push to the branch.
5. Open a Pull Request.

**Ideas for improvement:**
- Add vulnerability detection (SQLi, XSS).
- Integrate `nmap` XML output parsing.
- Add more subdomain wordlists (from CLI).
- Support concurrency limit flags.

---

## 📜 License

Distributed under the **MIT License**. See `LICENSE` file for more information.

---

## ⚠️ Disclaimer

> This tool is intended for **authorized security testing and educational purposes** only.  
> The author is not responsible for any misuse or damage caused by this software.  
> Always obtain proper permission before scanning any system.

---

**Enjoy scanning responsibly!** 🕵️‍♂️  
*Built with ❤️ for Termux and ethical hackers.*
