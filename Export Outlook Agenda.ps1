param(
  [int]$DaysBack = 7,
  [int]$MaxInbox = 80,
  [int]$MaxTasks = 80,
  [string]$OutputPath = ""
)

$ErrorActionPreference = "Stop"

if (-not $OutputPath) {
  $OutputPath = Join-Path $PSScriptRoot "outlook-agenda-private.json"
}

function Clean-Text {
  param([object]$Value, [int]$Max = 500)
  if ($null -eq $Value) { return "" }
  $text = [string]$Value
  $text = $text -replace "`r|`n|`t", " "
  $text = $text -replace "\s+", " "
  $text = $text.Trim()
  if ($text.Length -gt $Max) { return $text.Substring(0, $Max).Trim() + "..." }
  return $text
}

function Has-Any {
  param([string]$Text, [string[]]$Words)
  foreach ($word in $Words) {
    if ($Text -match [regex]::Escape($word)) { return $true }
  }
  return $false
}

function Score-Mail {
  param($Mail)
  $score = 0
  $subject = Clean-Text $Mail.Subject 250
  $body = Clean-Text $Mail.Body 900
  $text = ($subject + " " + $body).ToLowerInvariant()
  if ($Mail.UnRead) { $score += 25 }
  if ($Mail.Importance -eq 2) { $score += 35 }
  if ($Mail.FlagStatus -ne 0) { $score += 45 }
  if (Has-Any $text @("urgent","asap","today","approval","approve","review","action required","please action","can you","could you","needed","deadline","blocked","query")) { $score += 30 }
  try {
    $ageHours = ((Get-Date) - ([datetime]$Mail.ReceivedTime)).TotalHours
    if ($ageHours -le 24) { $score += 20 }
    elseif ($ageHours -le 72) { $score += 10 }
  } catch {}
  return $score
}

function Score-Task {
  param($Task)
  $score = 20
  if ($Task.Importance -eq 2) { $score += 35 }
  if ($Task.PercentComplete -gt 0 -and $Task.PercentComplete -lt 100) { $score += 15 }
  try {
    $due = [datetime]$Task.DueDate
    if ($due.Year -gt 1900) {
      $today = (Get-Date).Date
      $days = ($due.Date - $today).Days
      if ($days -lt 0) { $score += 70 }
      elseif ($days -eq 0) { $score += 55 }
      elseif ($days -le 7) { $score += 30 }
    }
  } catch {}
  return $score
}

$outlook = New-Object -ComObject Outlook.Application
$namespace = $outlook.GetNamespace("MAPI")
$cutoff = (Get-Date).AddDays(-1 * [math]::Abs($DaysBack))

$inboxRows = New-Object System.Collections.Generic.List[object]
$inboxItems = $namespace.GetDefaultFolder(6).Items
$inboxItems.Sort("[ReceivedTime]", $true)

$seenInbox = 0
foreach ($item in $inboxItems) {
  if ($seenInbox -ge $MaxInbox) { break }
  if ($item.Class -ne 43) { continue }
  $received = $null
  try { $received = [datetime]$item.ReceivedTime } catch {}
  if ($received -and $received -lt $cutoff -and -not $item.UnRead -and $item.FlagStatus -eq 0) { continue }
  $seenInbox += 1
  $inboxRows.Add([pscustomobject]@{
    subject = Clean-Text $item.Subject 220
    sender = Clean-Text $item.SenderName 120
    senderEmail = Clean-Text $item.SenderEmailAddress 160
    received = if ($received) { $received.ToString("o") } else { "" }
    unread = [bool]$item.UnRead
    flagged = [bool]($item.FlagStatus -ne 0)
    importance = if ($item.Importance -eq 2) { "high" } elseif ($item.Importance -eq 0) { "low" } else { "normal" }
    categories = Clean-Text $item.Categories 120
    preview = Clean-Text $item.Body 420
    score = Score-Mail $item
  })
}

$taskRows = New-Object System.Collections.Generic.List[object]
try {
  $tasks = $namespace.GetDefaultFolder(13).Items
  $tasks.Sort("[DueDate]", $false)
  $seenTasks = 0
  foreach ($task in $tasks) {
    if ($seenTasks -ge $MaxTasks) { break }
    if ($task.Class -ne 48) { continue }
    if ($task.Status -eq 2 -or $task.PercentComplete -ge 100) { continue }
    $seenTasks += 1
    $due = $null
    try { $due = [datetime]$task.DueDate } catch {}
    $taskRows.Add([pscustomobject]@{
      subject = Clean-Text $task.Subject 220
      due = if ($due -and $due.Year -gt 1900) { $due.ToString("yyyy-MM-dd") } else { "" }
      status = [string]$task.Status
      percentComplete = [int]$task.PercentComplete
      importance = if ($task.Importance -eq 2) { "high" } elseif ($task.Importance -eq 0) { "low" } else { "normal" }
      categories = Clean-Text $task.Categories 120
      preview = Clean-Text $task.Body 420
      score = Score-Task $task
    })
  }
} catch {}

$inboxSorted = @($inboxRows | Sort-Object score -Descending | Select-Object -First 30)
$tasksSorted = @($taskRows | Sort-Object score -Descending | Select-Object -First 30)

$digest = [pscustomobject]@{
  generatedAt = (Get-Date).ToString("o")
  source = "Outlook desktop local export"
  inboxWindowDays = $DaysBack
  counts = [pscustomobject]@{
    inbox = $inboxSorted.Count
    unread = @($inboxSorted | Where-Object { $_.unread }).Count
    flagged = @($inboxSorted | Where-Object { $_.flagged }).Count
    tasks = $tasksSorted.Count
  }
  inbox = $inboxSorted
  tasks = $tasksSorted
}

$digest | ConvertTo-Json -Depth 6 | Set-Content -Path $OutputPath -Encoding UTF8
Write-Host "Outlook agenda exported:"
Write-Host $OutputPath
