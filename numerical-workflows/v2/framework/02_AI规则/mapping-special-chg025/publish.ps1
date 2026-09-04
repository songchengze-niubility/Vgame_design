$ErrorActionPreference = 'Stop'
$taskDir = $PSScriptRoot
$frameworkDir = (Resolve-Path -LiteralPath (Join-Path $taskDir '../..')).Path
$candidateDir = Join-Path $frameworkDir '06_最终配置/映射装备'
$pre = Get-Content -LiteralPath (Join-Path $taskDir 'preflight.json') -Raw -Encoding utf8 | ConvertFrom-Json
$valid = Get-Content -LiteralPath (Join-Path $frameworkDir '05_验算核算/mapping-special-CHG025-staged-validation.json') -Raw -Encoding utf8 | ConvertFrom-Json
if ($valid.status -ne 'PASS') { throw 'Staged validation failed.' }
function Get-SharedReadHash([string]$path) {
    $stream = [System.IO.File]::Open($path,[System.IO.FileMode]::Open,[System.IO.FileAccess]::Read,[System.IO.FileShare]::ReadWrite)
    $alg = [System.Security.Cryptography.SHA256]::Create()
    try { return [BitConverter]::ToString($alg.ComputeHash($stream)).Replace('-','').ToLower() } finally { $stream.Dispose(); $alg.Dispose() }
}
foreach ($entry in $pre.formalHashes.PSObject.Properties) {
    if ((Get-SharedReadHash $entry.Name) -ne $entry.Value) { throw "Source changed: $($entry.Name)" }
}
foreach ($entry in $pre.candidateHashes.PSObject.Properties) {
    if ((Get-FileHash -LiteralPath (Join-Path $candidateDir $entry.Name) -Algorithm SHA256).Hash.ToLower() -ne $entry.Value) { throw "Candidate changed: $($entry.Name)" }
}
$backup = Join-Path $frameworkDir ('05_验算核算/映射装备CHG025_候选备份/' + (Get-Date -Format 'yyyyMMddTHHmmss'))
New-Item -ItemType Directory -Path $backup | Out-Null
$streams = @{}
$written = [System.Collections.Generic.List[string]]::new()
try {
    foreach ($f in $pre.files) {
        $stage = Join-Path $taskDir ('staged/' + $f)
        $target = Join-Path $candidateDir $f
        if ((Get-FileHash -LiteralPath $stage -Algorithm SHA256).Hash.ToLower() -ne $valid.hashes.$f) { throw "Stage changed: $f" }
        Copy-Item -LiteralPath $target -Destination (Join-Path $backup $f)
        $streams[$f] = [System.IO.File]::Open($target,[System.IO.FileMode]::Open,[System.IO.FileAccess]::ReadWrite,[System.IO.FileShare]::None)
        $alg = [System.Security.Cryptography.SHA256]::Create()
        try { $lockedHash = [BitConverter]::ToString($alg.ComputeHash($streams[$f])).Replace('-','').ToLower() } finally { $alg.Dispose() }
        if ($lockedHash -ne $pre.candidateHashes.$f) { throw "Target changed before lock: $f" }
    }
    foreach ($f in $pre.files) {
        $inputStream = [System.IO.File]::OpenRead((Join-Path $taskDir ('staged/' + $f)))
        try { $written.Add($f); $streams[$f].Position=0; $streams[$f].SetLength(0); $inputStream.CopyTo($streams[$f]); $streams[$f].Flush($true) } finally { $inputStream.Dispose() }
    }
} catch {
    foreach ($f in $written) {
        $original = [System.IO.File]::OpenRead((Join-Path $backup $f))
        try { $streams[$f].Position=0; $streams[$f].SetLength(0); $original.CopyTo($streams[$f]); $streams[$f].Flush($true) } finally { $original.Dispose() }
    }
    throw
} finally { foreach ($stream in $streams.Values) { $stream.Dispose() } }
$receipt = @{revision='CHG-025';status='PUBLISHED_TO_06_ONLY';backup=$backup;files=$pre.files;hashes=$valid.hashes}
$receipt | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $frameworkDir '05_验算核算/mapping-special-CHG025.json') -Encoding utf8
$receipt | ConvertTo-Json -Depth 5
