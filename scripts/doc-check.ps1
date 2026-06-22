param([string]$Root = (Split-Path -Parent $PSScriptRoot))

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$WarnCount = 0
$FailCount = 0

function Warn([string]$Message) {
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
    $script:WarnCount++
}

function Fail([string]$Message) {
    Write-Host "[FAIL] $Message" -ForegroundColor Red
    $script:FailCount++
}

$AcceptanceZh = [string]::Concat([char]0x9A8C, [char]0x6536)
$ConfigZh = [string]::Concat([char]0x914D, [char]0x7F6E)
$DataSourceZh = [string]::Concat([char]0x6570, [char]0x636E, [char]0x6E90)

Write-Host "=== Vgame Design Document Check ===" -ForegroundColor Cyan

$pairs = @{}
Get-ChildItem "$Root\design" -Filter "*.md" -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -notin @("README.md", "TEMPLATE.md", "REVERSE-ENGINEERING-TEMPLATE.md") } |
    ForEach-Object { $pairs[$_.BaseName] = $_ }

foreach ($name in $pairs.Keys) {
    $design = $pairs[$name]
    $content = Get-Content -Raw -Encoding UTF8 $design.FullName
    if ($content -notmatch "R\d{3}") { Warn "$($design.Name) is missing a rule ID such as R001" }
    if ($content -notmatch "Acceptance|$AcceptanceZh") { Warn "$($design.Name) is missing acceptance criteria" }
    if ($content -notmatch "Source|$ConfigZh|$DataSourceZh") { Warn "$($design.Name) is missing config or source references" }

    $proposalName = $design.Name.Replace("Design Doc", "Proposal Doc")
    $proposal = Join-Path "$Root\proposals" $proposalName
    if (-not (Test-Path $proposal)) { Warn "$($design.Name) has no matching proposal" }
}

foreach ($template in @("design\TEMPLATE.md", "proposals\TEMPLATE.md", "tasks\TEMPLATE.md")) {
    if (-not (Test-Path (Join-Path $Root $template))) { Fail "Missing template: $template" }
}

Write-Host "=== Result: FAIL $FailCount, WARN $WarnCount ===" -ForegroundColor Cyan
if ($FailCount -gt 0) { exit 1 }
