# Diagnóstico de solo lectura del equipo (no instala ni modifica nada).
# Uso: powershell -ExecutionPolicy Bypass -File scripts\diagnostico.ps1
$ErrorActionPreference = "SilentlyContinue"
$out = Join-Path $PSScriptRoot "..\evidence\fase-0"
New-Item -ItemType Directory -Force -Path $out | Out-Null
$f = Join-Path $out "diagnostico.txt"
function Linea($t) { Write-Output $t; Add-Content -Path $f -Value $t -Encoding UTF8 }
Remove-Item $f -ErrorAction SilentlyContinue
Linea "Fecha: $(Get-Date -Format o)"
$os = Get-CimInstance Win32_OperatingSystem
Linea "SO: $($os.Caption) $($os.Version) build $($os.BuildNumber)"
$cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
Linea "CPU: $($cpu.Name) | nucleos $($cpu.NumberOfCores) | hilos $($cpu.NumberOfLogicalProcessors) | virtualizacion firmware $($cpu.VirtualizationFirmwareEnabled)"
Linea ("RAM total: {0:N1} GB | libre: {1:N1} GB" -f ($os.TotalVisibleMemorySize/1MB), ($os.FreePhysicalMemory/1MB))
Get-CimInstance Win32_LogicalDisk -Filter "DriveType=3" | ForEach-Object { Linea ("Disco {0} libre {1:N1} GB de {2:N1} GB" -f $_.DeviceID, ($_.FreeSpace/1GB), ($_.Size/1GB)) }
Linea "--- WSL ---";      Linea ((wsl.exe --status 2>&1) -join " ")
Linea ((wsl.exe -l -v 2>&1) -join " ")
foreach ($c in @("docker --version","docker compose version","docker info --format '{{.ServerVersion}} {{.OperatingSystem}} {{.MemTotal}}'","git --version","node --version","npm --version","python --version","java -version","claude --version","gh --version")) {
  $r = (Invoke-Expression "$c 2>&1") -join " "
  if (-not $r) { $r = "no encontrado" }
  $nombre = ($c.Split(" ")[0..1] -join " ")
  Linea ("{0,-16} {1}" -f $nombre, $r)
}
Linea "Diagnostico terminado: $f"
