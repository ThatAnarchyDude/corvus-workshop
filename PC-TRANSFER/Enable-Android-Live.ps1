# Run once from an Administrator PowerShell while the live runner is active.
$ErrorActionPreference = 'Stop'
$lan = Get-NetIPConfiguration | Where-Object { $_.IPv4DefaultGateway -and $_.IPv4Address } | Select-Object -First 1
$lanIp = $lan.IPv4Address.IPAddress
$wslIp = ((wsl -d Ubuntu -- hostname -I).Trim() -split '\s+')[0]
netsh interface portproxy add v4tov4 listenaddress=$lanIp listenport=8080 connectaddress=$wslIp connectport=8080
if ($LASTEXITCODE -ne 0) { throw 'Port forwarding failed; run PowerShell as Administrator.' }
if (-not (Get-NetFirewallRule -DisplayName 'Psyduck Yellow local live testing' -ErrorAction SilentlyContinue)) {
    New-NetFirewallRule -DisplayName 'Psyduck Yellow local live testing' -Direction Inbound -Action Allow -Protocol TCP -LocalPort 8080 -LocalAddress $lanIp -RemoteAddress LocalSubnet -Profile Private | Out-Null
}
Write-Host "Android dashboard: http://${lanIp}:8080/ (same Wi-Fi; Private network profile required)"
Write-Host 'Stop the testing server when finished. Rerun this script if WSL or Wi-Fi addresses change.'
