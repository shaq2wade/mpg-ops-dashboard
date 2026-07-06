param(
  [int]$Port = 8765,
  [int]$RefreshMinutes = 5
)

$ErrorActionPreference = "Stop"

$Root = $PSScriptRoot
$ExportScript = Join-Path $Root "Export Outlook Agenda.ps1"
$OutputPath = Join-Path $Root "outlook-agenda-private.json"
$AgendaUrl = "https://shaq2wade.github.io/mpg-ops-dashboard/agenda.html?local=1"
$LastExport = Get-Date "2000-01-01"

function Invoke-AgendaExport {
  param([switch]$Force)
  $stale = ((Get-Date) - $script:LastExport).TotalMinutes -ge $RefreshMinutes
  if ($Force -or $stale -or -not (Test-Path $OutputPath)) {
    Write-Host "Refreshing Outlook digest..."
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $ExportScript -OutputPath $OutputPath | Out-Null
    $script:LastExport = Get-Date
    Write-Host "Updated $OutputPath"
  }
}

function Write-HttpResponse {
  param(
    [System.Net.Sockets.NetworkStream]$Stream,
    [int]$StatusCode,
    [string]$StatusText,
    [string]$ContentType,
    [string]$Body
  )
  $bodyBytes = [System.Text.Encoding]::UTF8.GetBytes($Body)
  $header = "HTTP/1.1 $StatusCode $StatusText`r`n" +
    "Content-Type: $ContentType; charset=utf-8`r`n" +
    "Content-Length: $($bodyBytes.Length)`r`n" +
    "Access-Control-Allow-Origin: https://shaq2wade.github.io`r`n" +
    "Access-Control-Allow-Methods: GET, OPTIONS`r`n" +
    "Access-Control-Allow-Headers: Content-Type`r`n" +
    "Access-Control-Allow-Private-Network: true`r`n" +
    "Cache-Control: no-store`r`n" +
    "Connection: close`r`n`r`n"
  $headerBytes = [System.Text.Encoding]::ASCII.GetBytes($header)
  $Stream.Write($headerBytes, 0, $headerBytes.Length)
  $Stream.Write($bodyBytes, 0, $bodyBytes.Length)
}

if (-not (Test-Path $ExportScript)) {
  throw "Could not find $ExportScript"
}

Invoke-AgendaExport -Force

$listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Parse("127.0.0.1"), $Port)
$listener.Start()
Write-Host ""
Write-Host "Agenda auto-refresh is running."
Write-Host "Local endpoint: http://127.0.0.1:$Port/digest"
Write-Host "Refresh cadence: every $RefreshMinutes minutes"
Write-Host "Keep this window open. Press Ctrl+C to stop."
Write-Host ""
if ($env:MPG_AGENDA_OPEN_BROWSER -eq "1") {
  try {
    Start-Process $AgendaUrl
  } catch {
    Write-Host "Could not auto-open agenda page: $($_.Exception.Message)"
  }
}

try {
  while ($true) {
    $client = $listener.AcceptTcpClient()
    $client.ReceiveTimeout = 3000
    $client.SendTimeout = 3000
    try {
      $stream = $client.GetStream()
      $stream.ReadTimeout = 3000
      $stream.WriteTimeout = 3000
      $reader = [System.IO.StreamReader]::new($stream, [System.Text.Encoding]::ASCII, $false, 1024, $true)
      $requestLine = $reader.ReadLine()
      while ($true) {
        $line = $reader.ReadLine()
        if ($null -eq $line -or $line -eq "") { break }
      }

      if (-not $requestLine) {
        Write-HttpResponse $stream 400 "Bad Request" "text/plain" "Bad request"
        continue
      }

      $parts = $requestLine.Split(" ")
      $method = $parts[0]
      $path = $parts[1]

      if ($method -eq "OPTIONS") {
        Write-HttpResponse $stream 204 "No Content" "text/plain" ""
      } elseif ($path -like "/digest*") {
        Invoke-AgendaExport
        $json = Get-Content $OutputPath -Raw -Encoding UTF8
        Write-HttpResponse $stream 200 "OK" "application/json" $json
      } elseif ($path -like "/status*") {
        $status = @{
          ok = $true
          lastExport = $LastExport.ToString("o")
          outputPath = $OutputPath
        } | ConvertTo-Json
        Write-HttpResponse $stream 200 "OK" "application/json" $status
      } else {
        Write-HttpResponse $stream 404 "Not Found" "text/plain" "Use /digest"
      }
    } catch {
      try { Write-HttpResponse $stream 500 "Server Error" "text/plain" $_.Exception.Message } catch {}
    } finally {
      $client.Close()
    }
  }
} finally {
  $listener.Stop()
}
