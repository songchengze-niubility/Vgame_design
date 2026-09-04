param([switch]$VisualQaApproved)
$ErrorActionPreference = 'Stop'
if (-not $VisualQaApproved) { throw 'Require visual review of previews before publishing.' }
$runRoot = $PSScriptRoot
$base = Get-Content -LiteralPath (Join-Path $runRoot 'baseline.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$repair = Get-Content -LiteralPath (Join-Path $runRoot 'repair.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$valid = Get-Content -LiteralPath (Join-Path $runRoot 'validation-staged.json') -Raw -Encoding UTF8 | ConvertFrom-Json
if (-not $valid.allPassed) { throw 'Staged validation failed.' }
$expectedRoot = [IO.Path]::GetFullPath((Join-Path $runRoot '../../06_最终配置/映射装备'))
if ([IO.Path]::GetFullPath($repair.out) -ne $expectedRoot) { throw 'Unexpected publication target.' }
function Get-StreamHash($Stream) {
    $Stream.Position = 0
    $algo = [Security.Cryptography.SHA256]::Create()
    try { return [BitConverter]::ToString($algo.ComputeHash($Stream)).Replace('-', '').ToLowerInvariant() }
    finally { $algo.Dispose(); $Stream.Position = 0 }
}
$handles = @{}
$payloads = @{}
$originals = @{}
$touched = @()
try {
    # Acquire every write lock before changing any workbook; do not close user applications.
    foreach ($name in $repair.files) {
        $dest = [IO.Path]::GetFullPath((Join-Path $expectedRoot $name))
        if ([IO.Path]::GetDirectoryName($dest) -ne $expectedRoot) { throw 'Out-of-scope path.' }
        $handles[$name] = [IO.File]::Open($dest, [IO.FileMode]::Open, [IO.FileAccess]::ReadWrite, [IO.FileShare]::None)
        if ((Get-StreamHash $handles[$name]) -ne $base.candidateHashes.$name) { throw "Concurrent edit: $name" }
        $payload = Join-Path $repair.stage $name
        $stageHash = (Get-FileHash -LiteralPath $payload -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($stageHash -ne $repair.stageHashes.$name -or $stageHash -ne $valid.fileHashes.$name) { throw "Unvalidated staged content: $name" }
        $backup = Join-Path $repair.backup $name
        if ((Get-FileHash -LiteralPath $backup -Algorithm SHA256).Hash.ToLowerInvariant() -ne $base.candidateHashes.$name) { throw "Invalid rollback backup: $name" }
        $payloads[$name] = [IO.File]::ReadAllBytes($payload)
        $originals[$name] = [IO.File]::ReadAllBytes($backup)
    }
    foreach ($entry in $base.candidateHashes.PSObject.Properties) {
        if ($repair.files -contains $entry.Name) { continue }
        if ((Get-FileHash -LiteralPath (Join-Path $expectedRoot $entry.Name) -Algorithm SHA256).Hash.ToLowerInvariant() -ne $entry.Value) { throw "Other candidate changed: $($entry.Name)" }
    }
    foreach ($entry in $base.formalHashes.PSObject.Properties) {
        if ((Get-FileHash -LiteralPath $entry.Name -Algorithm SHA256).Hash.ToLowerInvariant() -ne $entry.Value) { throw "Formal baseline changed: $($entry.Name)" }
    }
    foreach ($name in $repair.files) {
        $touched += $name
        $stream = $handles[$name]; $bytes = $payloads[$name]
        $stream.Position = 0; $stream.SetLength(0); $stream.Write($bytes, 0, $bytes.Length); $stream.Flush($true)
        if ((Get-StreamHash $stream) -ne $repair.stageHashes.$name) { throw "Publication hash mismatch: $name" }
    }
} catch {
    foreach ($name in $touched) {
        $stream = $handles[$name]; $bytes = $originals[$name]
        $stream.Position = 0; $stream.SetLength(0); $stream.Write($bytes, 0, $bytes.Length); $stream.Flush($true)
    }
    throw
} finally {
    foreach ($stream in $handles.Values) { $stream.Dispose() }
}
$publication = @{ revision = 'CHG-026'; publishedAt = [DateTime]::UtcNow.ToString('o'); visualQaApproved = $true; files = $repair.files; outputHashes = $repair.stageHashes; backup = $repair.backup; scope = '06 only; no SVN writes' }
$publication | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $runRoot 'publication.json') -Encoding UTF8
Write-Output 'Published 3 validated candidate workbooks; SVN unchanged.'
