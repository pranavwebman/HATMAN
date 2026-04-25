#!/usr/bin/env python3
"""
Hatman - Web Reconnaissance Scanner for Termux
Version 4.0 - Colorful + Interactive HTML Report
Author: Hatman Developer
"""

import requests
import socket
import dns.resolver
import sys
import time
import argparse
import json
from concurrent.futures import ThreadPoolExecutor
import threading
import ssl
import re
import datetime
from datetime import datetime as dt
import html

# ANSI color codes
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    ORANGE = '\033[38;5;208m'
    PINK = '\033[38;5;205m'
    DARK_GREEN = '\033[38;5;22m'
    GRAY = '\033[90m'

class HatmanScanner:
    def __init__(self, target, animation=True):
        self.target = target
        self.animation = animation
        self.print_lock = threading.Lock()
        self.results = {
            'target': target,
            'timestamp': dt.now().isoformat(),
            'scan_type': 'full'
        }

    # --------------------------------------------------------------
    # Colorful animated print (thread-safe)
    # --------------------------------------------------------------
    def animated_print(self, text, color=Colors.RESET, delay=0.02, end='\n'):
        """Print text with per-character animation and color."""
        with self.print_lock:
            if not self.animation:
                print(f"{color}{text}{Colors.RESET}", end=end)
                return
            sys.stdout.write(color)
            for char in text:
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(delay)
            sys.stdout.write(Colors.RESET)
            if end:
                sys.stdout.write(end)
                sys.stdout.flush()

    def banner(self):
        banner_text = """
    ██╗  ██╗ █████╗ ████████╗███╗   ███╗ █████╗ ███╗   ██╗
    ██║  ██║██╔══██╗╚══██╔══╝████╗ ████║██╔══██╗████╗  ██║
    ███████║███████║   ██║   ██╔████╔██║███████║██╔██╗ ██║
    ██╔══██║██╔══██║   ██║   ██║╚██╔╝██║██╔══██║██║╚██╗██║
    ██║  ██║██║  ██║   ██║   ██║ ╚═╝ ██║██║  ██║██║ ╚████║
    ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝
                
        Web Reconnaissance Scanner v4.0 (Colorful + HTML Report)
        Termux Edition - Pure Python
        Made by - Pranav Krishna H
        """
        self.animated_print(banner_text, Colors.CYAN, delay=0.003)

    # --------------------------------------------------------------
    # Dependencies & validation
    # --------------------------------------------------------------
    def check_dependencies(self):
        try:
            import requests, dns.resolver, urllib3
            return True
        except ImportError as e:
            self.animated_print(f"[!] Missing dependency: {e}", Colors.RED)
            self.animated_print("[!] Install: pip install requests dnspython", Colors.YELLOW)
            return False

    def validate_target(self):
        try:
            socket.inet_aton(self.target)
            return True, "ip"
        except:
            if '.' in self.target and len(self.target) > 3:
                return True, "domain"
        return False, "Invalid target"

    # --------------------------------------------------------------
    # DNS Recon (same as before, but with colors)
    # --------------------------------------------------------------
    def dns_recon(self):
        self.animated_print("[+] Starting DNS reconnaissance...", Colors.GREEN)
        dns_results = {}
        record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA']
        for rtype in record_types:
            try:
                answers = dns.resolver.resolve(self.target, rtype)
                records = [str(r) for r in answers]
                dns_results[f'{rtype.lower()}_records'] = records
                self.animated_print(f"  ✅ {rtype}: {len(records)} records found", Colors.CYAN)
            except:
                dns_results[f'{rtype.lower()}_records'] = []
                self.animated_print(f"  ❌ {rtype}: No records found", Colors.RED)
        try:
            hostname = socket.gethostbyaddr(self.target)
            dns_results['reverse_dns'] = hostname[0]
            self.animated_print(f"  ✅ Reverse DNS: {hostname[0]}", Colors.CYAN)
        except:
            dns_results['reverse_dns'] = "Not found"
        self.results['dns'] = dns_results

    # --------------------------------------------------------------
    # Port scanning (fixed: no animation inside threads, sanitize banners)
    # --------------------------------------------------------------
    def get_banner(self, sock, port):
        try:
            sock.settimeout(3)
            if port in [21,22,25,110,143,3306,5432]:
                banner = sock.recv(1024).decode('utf-8', errors='ignore')
                # Clean non-printable chars
                return ''.join(filter(lambda x: x.isprintable() or x in '\n\r\t', banner)).strip()
            elif port in [80,443,8080,8443]:
                sock.send(b"HEAD / HTTP/1.0\r\n\r\n")
                banner = sock.recv(1024).decode('utf-8', errors='ignore')
                return ''.join(filter(lambda x: x.isprintable() or x in '\n\r\t', banner)).strip()
        except:
            pass
        return ""

    def port_scan(self, ports=None, timeout=2):
        self.animated_print("[+] Starting port scan...", Colors.GREEN)
        if ports is None:
            ports = [21,22,23,25,53,80,110,143,443,465,587,993,995,8080,8443,3306,3389,5432]
        open_ports = []
        service_info = {}
        service_map = {
            21:'FTP',22:'SSH',23:'Telnet',25:'SMTP',53:'DNS',80:'HTTP',110:'POP3',
            143:'IMAP',443:'HTTPS',465:'SMTPS',587:'SMTP',993:'IMAPS',995:'POP3S',
            8080:'HTTP-Alt',8443:'HTTPS-Alt',3306:'MySQL',3389:'RDP',5432:'PostgreSQL'
        }

        def scan_port(port):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                result = sock.connect_ex((self.target, port))
                if result == 0:
                    service = service_map.get(port, 'Unknown')
                    banner = self.get_banner(sock, port)
                    with self.print_lock:  # lock to avoid mixing prints from threads
                        print(f"{Colors.GREEN}  ✅ Port {port} ({service}) - OPEN{Colors.RESET}")
                        if banner:
                            print(f"{Colors.GRAY}      Banner: {banner[:200]}{Colors.RESET}")
                    open_ports.append(port)
                    service_info[port] = {'service': service, 'banner': banner}
                sock.close()
            except:
                pass

        self.animated_print(f"  [*] Scanning {len(ports)} ports...", Colors.YELLOW)
        with ThreadPoolExecutor(max_workers=100) as executor:
            executor.map(scan_port, ports)

        self.results['open_ports'] = open_ports
        self.results['service_info'] = service_info

    # --------------------------------------------------------------
    # Web enumeration (enhanced tech detection)
    # --------------------------------------------------------------
    def advanced_tech_detection(self, response):
        tech = []
        headers = response.headers
        content = response.text.lower()
        server = headers.get('Server', '').lower()
        if 'apache' in server: tech.append('Apache')
        if 'nginx' in server: tech.append('Nginx')
        if 'litespeed' in server: tech.append('LiteSpeed')
        cms_signatures = {
            'WordPress': ['wp-content', 'wp-includes'],
            'Drupal': ['drupal', 'sites/default'],
            'Joomla': ['joomla', 'com_content'],
        }
        for cms, patterns in cms_signatures.items():
            if any(p in content for p in patterns):
                tech.append(cms)
        js_frameworks = {
            'React': ['react', 'reactjs'], 'Angular': ['ng-', 'angular'],
            'Vue.js': ['vue', 'vuejs'], 'jQuery': ['jquery', '$('],
            'Bootstrap': ['bootstrap']
        }
        for name, patterns in js_frameworks.items():
            if any(p in content for p in patterns):
                tech.append(name)
        if 'google-analytics' in content: tech.append('Google Analytics')
        if 'php' in content: tech.append('PHP')
        return list(set(tech))

    def extract_title(self, html):
        match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip()[:100] if match else "No title"

    def web_enumeration(self):
        self.animated_print("[+] Starting web enumeration...", Colors.GREEN)
        web_results = {}
        web_ports = [80, 443, 8080, 8443, 8000, 8888, 3000, 5000]
        for port in web_ports:
            try:
                protocol = 'https' if port in [443,8443] else 'http'
                url = f"{protocol}://{self.target}:{port}"
                r = requests.get(url, timeout=10, verify=False, headers={'User-Agent': 'Hatman/4.0'})
                tech = self.advanced_tech_detection(r)
                web_results[port] = {
                    'status_code': r.status_code,
                    'server': r.headers.get('Server', 'Unknown'),
                    'title': self.extract_title(r.text),
                    'technologies': tech,
                    'headers': dict(r.headers)
                }
                self.animated_print(f"  ✅ Port {port}: {web_results[port]['server']} - {r.status_code} - '{web_results[port]['title']}'", Colors.CYAN)
                if tech:
                    self.animated_print(f"      Technologies: {', '.join(tech[:5])}", Colors.MAGENTA)
            except Exception as e:
                web_results[port] = {'error': str(e)}
                self.animated_print(f"  ❌ Port {port}: Unable to connect", Colors.RED)
        self.results['web_info'] = web_results

    # --------------------------------------------------------------
    # Subdomain discovery (colored)
    # --------------------------------------------------------------
    def subdomain_scan(self, wordlist=None):
        if wordlist is None:
            wordlist = ['www','mail','ftp','webmail','admin','blog','shop','api','test','dev',
                        'staging','secure','portal','email','webdisk','forum','support','vpn',
                        'status','backup','gitlab','jenkins','wiki','docs','cdn','static','assets',
                        'download','files','media','live','video','images','img','css','js','cloud',
                        'app','dashboard','control','manage']
        self.animated_print(f"[+] Subdomain enumeration ({len(wordlist)} candidates)...", Colors.GREEN)
        found = []
        def check(sub):
            full = f"{sub}.{self.target}"
            try:
                socket.gethostbyname(full)
                with self.print_lock:
                    print(f"{Colors.GREEN}  ✅ Found: {full}{Colors.RESET}")
                found.append(full)
            except:
                pass
        with ThreadPoolExecutor(max_workers=30) as ex:
            ex.map(check, wordlist)
        self.results['subdomains'] = found

    # --------------------------------------------------------------
    # Directory bruteforce (colored)
    # --------------------------------------------------------------
    def directory_bruteforce(self, wordlist=None):
        if wordlist is None:
            wordlist = ['admin','login','wp-admin','administrator','phpmyadmin','backup','uploads',
                        'images','css','js','cgi-bin','dashboard','control','manager','web','site',
                        'root','old','tmp','temp','logs','database','sql','config','include','lib',
                        'src','assets','downloads','files','public','private','secure','hidden']
        self.animated_print(f"[+] Directory bruteforce ({len(wordlist)} paths)...", Colors.GREEN)
        found = []
        def check_dir(d):
            for port in [80,443]:
                protocol = 'https' if port==443 else 'http'
                url = f"{protocol}://{self.target}:{port}/{d}"
                try:
                    r = requests.get(url, timeout=4, verify=False)
                    if r.status_code in [200,301,302,403]:
                        with self.print_lock:
                            print(f"{Colors.GREEN}  ✅ Found: {url} [{r.status_code}]{Colors.RESET}")
                        found.append({'url': url, 'status': r.status_code})
                        return
                except:
                    pass
        with ThreadPoolExecutor(max_workers=15) as ex:
            ex.map(check_dir, wordlist)
        self.results['directories'] = found

    # --------------------------------------------------------------
    # WHOIS lookup (colored)
    # --------------------------------------------------------------
    def python_whois(self):
        self.animated_print("[+] Performing WHOIS lookup...", Colors.GREEN)
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(("whois.verisign-grs.com", 43))
            s.send((self.target + "\r\n").encode())
            resp = b""
            s.settimeout(5)
            while True:
                try:
                    data = s.recv(4096)
                    if not data: break
                    resp += data
                except socket.timeout:
                    break
            s.close()
            data = resp.decode('utf-8', errors='ignore')
            useful = []
            for line in data.split('\n'):
                if any(k in line.lower() for k in ['registrar','creation date','updated date','expiration','name server','status']):
                    useful.append(line.strip())
            self.results['whois'] = {'useful_info': useful[:15]}
            self.animated_print("  ✅ WHOIS data retrieved", Colors.CYAN)
            for info in useful[:8]:
                self.animated_print(f"      {info}", Colors.GRAY)
        except Exception as e:
            self.results['whois'] = {'error': str(e)}
            self.animated_print(f"  ❌ WHOIS lookup failed: {e}", Colors.RED)

    # --------------------------------------------------------------
    # Security headers check (colored)
    # --------------------------------------------------------------
    def security_headers_check(self):
        self.animated_print("[+] Checking security headers...", Colors.GREEN)
        headers_list = ['Content-Security-Policy','X-Frame-Options','X-Content-Type-Options',
                        'Strict-Transport-Security','X-XSS-Protection','Referrer-Policy']
        found = {}
        for port in [80,443]:
            try:
                protocol = 'https' if port==443 else 'http'
                url = f"{protocol}://{self.target}:{port}"
                r = requests.get(url, timeout=5, verify=False)
                for h in headers_list:
                    if h in r.headers:
                        found[h] = r.headers[h]
                        self.animated_print(f"  ✅ {h}: {r.headers[h]}", Colors.GREEN)
                    else:
                        self.animated_print(f"  ❌ {h}: Missing", Colors.RED)
            except:
                pass
        self.results['security_headers'] = found

    # --------------------------------------------------------------
    # Generate interactive HTML report (replaces JSON)
    # --------------------------------------------------------------
    def generate_html_report(self):
        timestamp = int(time.time())
        filename = f"hatman_report_{self.target}_{timestamp}.html"
        # Prepare data for HTML
        target = self.target
        scan_date = self.results['timestamp']
        duration = self.results.get('scan_duration', 'N/A')
        dns = self.results.get('dns', {})
        open_ports = self.results.get('open_ports', [])
        service_info = self.results.get('service_info', {})
        web_info = self.results.get('web_info', {})
        subdomains = self.results.get('subdomains', [])
        directories = self.results.get('directories', [])
        whois = self.results.get('whois', {})
        security = self.results.get('security_headers', {})

        # Build HTML content
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hatman Report - {target}</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0a0f1e; color: #e0e0e0; margin: 0; padding: 20px; }}
        .container {{ max-width: 1400px; margin: auto; }}
        h1 {{ color: #4caf50; border-left: 5px solid #4caf50; padding-left: 20px; }}
        h2 {{ color: #ff9800; margin-top: 30px; cursor: pointer; background: #1e2a3a; padding: 10px; border-radius: 8px; }}
        h2:hover {{ background: #2c3e50; }}
        .card {{ background: #1e1e2f; border-radius: 12px; padding: 15px; margin: 15px 0; box-shadow: 0 4px 8px rgba(0,0,0,0.3); transition: 0.2s; }}
        .card h3 {{ margin-top: 0; color: #ffaa66; }}
        button {{ background: #2c3e50; border: none; color: white; padding: 6px 12px; border-radius: 20px; cursor: pointer; margin: 5px; }}
        button:hover {{ background: #4caf50; }}
        .collapsible {{ display: none; padding: 10px; background: #252c3a; border-radius: 8px; margin-top: 5px; }}
        .show {{ display: block; }}
        .badge {{ background: #4caf50; padding: 2px 8px; border-radius: 20px; font-size: 12px; margin-left: 10px; }}
        .badge-red {{ background: #f44336; }}
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        th, td {{ text-align: left; padding: 8px; border-bottom: 1px solid #444; }}
        th {{ background: #2c3e50; }}
        a {{ color: #80cbc4; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .footer {{ text-align: center; margin-top: 40px; font-size: 12px; color: #888; }}
        .filter-buttons {{ margin-bottom: 20px; }}
        hr {{ border-color: #2c3e50; }}
    </style>
    <script>
        function toggleSection(id) {{
            var elem = document.getElementById(id);
            elem.classList.toggle('show');
        }}
        function filterPorts(type) {{
            var rows = document.querySelectorAll('#ports-table tr');
            rows.forEach(row => {{
                if (type === 'all') row.style.display = '';
                else if (type === 'web' && (row.cells[0].innerText.includes('80') || row.cells[0].innerText.includes('443') || row.cells[0].innerText.includes('8080'))) row.style.display = '';
                else if (type === 'db' && (row.cells[0].innerText.includes('3306') || row.cells[0].innerText.includes('5432'))) row.style.display = '';
                else if (type === 'other' && !row.cells[0].innerText.includes('80') && !row.cells[0].innerText.includes('443') && !row.cells[0].innerText.includes('3306')) row.style.display = '';
                else row.style.display = 'none';
            }});
        }}
    </script>
</head>
<body>
<div class="container">
    <h1>🕵️ Hatman Scan Report</h1>
    <h2>Author: Pranav Krishna H</h2>
    <p><strong>Target:</strong> {target} &nbsp;|&nbsp; <strong>Scan Date:</strong> {scan_date} &nbsp;|&nbsp; <strong>Duration:</strong> {duration} sec</p>
    <hr>

    <!-- DNS Section -->
    <h2 onclick="toggleSection('dnsSection')">🔍 DNS Records <span class="badge">click to expand</span></h2>
    <div id="dnsSection" class="collapsible">
        <div class="card">
"""

        # DNS records
        for k, v in dns.items():
            if v and 'reverse' not in k:
                html_content += f"<p><strong>{k.upper()}:</strong> {', '.join(v[:5])}{' ...' if len(v)>5 else ''}</p>"
        if dns.get('reverse_dns'):
            html_content += f"<p><strong>Reverse DNS:</strong> {dns['reverse_dns']}</p>"

        html_content += """</div></div>

    <!-- Ports Section with filters -->
    <h2 onclick="toggleSection('portsSection')">🔒 Open Ports <span class="badge">click to expand</span></h2>
    <div id="portsSection" class="collapsible">
        <div class="filter-buttons">
            <button onclick="filterPorts('all')">All ports</button>
            <button onclick="filterPorts('web')">Web (80,443,8080)</button>
            <button onclick="filterPorts('db')">Database (3306,5432)</button>
            <button onclick="filterPorts('other')">Other</button>
        </div>
        <div class="card">
            <table id="ports-table">
                <tr><th>Port</th><th>Service</th><th>Banner (first 150 chars)</th></tr>
"""
        for port in open_ports:
            svc = service_info.get(port, {}).get('service', 'Unknown')
            banner = service_info.get(port, {}).get('banner', '')[:150]
            html_content += f"<tr><td>{port}</td><td>{svc}</td><td>{html.escape(banner)}</td></tr>"
        html_content += """</table></div></div>

    <!-- Web Servers -->
    <h2 onclick="toggleSection('webSection')">🌐 Web Servers</h2>
    <div id="webSection" class="collapsible">
        <div class="card">
"""
        for port, info in web_info.items():
            if 'error' in info:
                html_content += f"<p><strong>Port {port}:</strong> ❌ {info['error']}</p>"
            else:
                html_content += f"<p><strong>Port {port}:</strong> {info.get('server','Unknown')} - Status {info.get('status_code')}<br>"
                html_content += f"<em>Title:</em> {info.get('title','')}<br>"
                if info.get('technologies'):
                    html_content += f"<em>Technologies:</em> {', '.join(info['technologies'])}</p>"
        html_content += """</div></div>

    <!-- Subdomains -->
    <h2 onclick="toggleSection('subSection')">🔗 Subdomains</h2>
    <div id="subSection" class="collapsible">
        <div class="card">
            <ul>
"""
        for sub in subdomains:
            html_content += f"<li>{sub}</li>"
        html_content += """</ul></div></div>

    <!-- Directories found -->
    <h2 onclick="toggleSection('dirSection')">📁 Interesting Directories</h2>
    <div id="dirSection" class="collapsible">
        <div class="card">
            <ul>
"""
        for d in directories:
            html_content += f"<li><a href='{d['url']}' target='_blank'>{d['url']}</a> [HTTP {d['status']}]</li>"
        html_content += """</ul></div></div>

    <!-- Security Headers -->
    <h2 onclick="toggleSection('secSection')">🛡️ Security Headers</h2>
    <div id="secSection" class="collapsible">
        <div class="card">
"""
        for h, val in security.items():
            html_content += f"<p>✅ <strong>{h}:</strong> {val}</p>"
        if not security:
            html_content += "<p>⚠️ No security headers found.</p>"
        html_content += """</div></div>

    <!-- WHOIS Info -->
    <h2 onclick="toggleSection('whoisSection')">📜 WHOIS Information</h2>
    <div id="whoisSection" class="collapsible">
        <div class="card">
            <pre style="white-space: pre-wrap;">"""
        if 'useful_info' in whois:
            html_content += "\n".join(whois['useful_info'])
        else:
            html_content += whois.get('error', 'No WHOIS data')
        html_content += """</pre></div></div>

    <div class="footer">
        Generated by Hatman v4.0 | Interactive HTML Report, Author: Pranav Krishna H
    </div>
</div>
<script>
    // Auto-expand first section for visibility
    document.getElementById('dnsSection').classList.add('show');
</script>
</body>
</html>"""

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        self.animated_print(f"💾 HTML report saved to: {filename}", Colors.GREEN)
        return filename

    # --------------------------------------------------------------
    # Main scan orchestrator
    # --------------------------------------------------------------
    def run_full_scan(self):
        self.banner()
        if not self.check_dependencies():
            return
        valid, typ = self.validate_target()
        if not valid:
            self.animated_print(f"[!] Invalid target: {self.target}", Colors.RED)
            return
        self.animated_print(f"[*] Target: {self.target} ({typ})", Colors.BLUE)
        self.animated_print(f"[*] Start time: {dt.now().strftime('%Y-%m-%d %H:%M:%S')}", Colors.GRAY)
        self.animated_print("[*] Starting comprehensive scan...\n", Colors.YELLOW)

        start = time.time()
        scans = [
            ('DNS Reconnaissance', self.dns_recon),
            ('Port Scanning', self.port_scan),
            ('Web Enumeration', self.web_enumeration),
            ('Subdomain Discovery', self.subdomain_scan),
            ('Directory Bruteforce', self.directory_bruteforce),
            ('Security Headers Check', self.security_headers_check),
            ('WHOIS Lookup', self.python_whois)
        ]
        for name, func in scans:
            self.animated_print(f"\n[+] {name}", Colors.MAGENTA)
            func()
            time.sleep(0.5)
        self.results['scan_duration'] = round(time.time() - start, 2)
        self.animated_print(f"\n[*] Scan completed in {self.results['scan_duration']} seconds", Colors.CYAN)

        # Generate HTML report instead of JSON
        self.generate_html_report()
        self.animated_print("\n✅ Scan completed successfully!", Colors.GREEN)

# --------------------------------------------------------------
# Main entry point
# --------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description='Hatman - Colorful Web Recon Scanner with HTML Report')
    parser.add_argument('target', help='Domain or IP')
    parser.add_argument('--no-animation', action='store_true', help='Disable typing animation')
    parser.add_argument('--quick', action='store_true', help='Quick scan (common ports only)')
    args = parser.parse_args()

    scanner = HatmanScanner(args.target, animation=not args.no_animation)
    if args.quick:
        scanner.animated_print("[*] Quick scan mode", Colors.YELLOW)
        scanner.port_scan([80,443,22,21,53,8080], timeout=1.5)
        scanner.web_enumeration()
        scanner.generate_html_report()
    else:
        scanner.run_full_scan()

if __name__ == "__main__":
    # Silence SSL warnings
    try:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    except:
        pass
    if len(sys.argv) < 2:
        print("Usage: python3 hatman.py <target> [--no-animation] [--quick]")
        sys.exit(1)
    main()
