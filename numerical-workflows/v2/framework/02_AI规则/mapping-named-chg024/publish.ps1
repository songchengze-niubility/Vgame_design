$ErrorActionPreference = 'Stop'
throw 'CHG-024 FixEffect publication is retired. Use mapping-special-chg025/publish.ps1.'
$taskDir = $PSScriptRoot
$frameworkDir = (Resolve-Path -LiteralPath (Join-Path $taskDir '../..')).Path
$candidateDir = Join-Path $frameworkDir '06_最终配置/映射装备'
$preflight = Get-Content -LiteralPath (Join-Path $taskDir 'preflight.json') -Raw -Encoding utf8 | ConvertFrom-Json
$validation = Get-Content -LiteralPath (Join-Path $frameworkDir '05_验算核算/mapping-named-CHG024-staged-validation.json') -Raw -Encoding utf8 | ConvertFrom-Json
if ($validation.status -ne 'PASS') { throw 'Staged validation did not pass.' }
foreach ($entry in $preflight.formalHashes.PSObject.Properties) {
    if ((Get-FileHash -LiteralPath $entry.Name -Algorithm SHA256).Hash.ToLower() -ne $entry.Value) { throw "Source changed: $($entry.Name)" }
}
foreach ($entry in $preflight.candidateHashes.PSObject.Properties) {
    if ((Get-FileHash -LiteralPath (Join-Path $candidateDir $entry.Name) -Algorithm SHA256).Hash.ToLower() -ne $entry.Value) { throw "Candidate changed: $($entry.Name)" }
}
$backupDir = Join-Path $frameworkDir ('05_验算核算/映射装备CHG024_候选备份/' + (Get-Date -Format 'yyyyMMddTHHmmss'))
New-Item -ItemType Directory -Path $backupDir -ErrorAction Stop | Out-Null
$streams = @{}
$written = [System.Collections.Generic.List[string]]::new()
try {
    foreach ($file in $preflight.files) {
        $target = Join-Path $candidateDir $file
        $stage = Join-Path $taskDir ('staged/' + $file)
        if ((Get-FileHash -LiteralPath $stage -Algorithm SHA256).Hash.ToLower() -ne $validation.hashes.$file) { throw "Staged file changed: $file" }
        Copy-Item -LiteralPath $target -Destination (Join-Path $backupDir $file) -ErrorAction Stop
        $streams[$file] = [System.IO.File]::Open($target, [System.IO.FileMode]::Open, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
        $hashAlgorithm = [System.Security.Cryptography.SHA256]::Create()
        try { $lockedHash = [BitConverter]::ToString($hashAlgorithm.ComputeHash($streams[$file])).Replace('-', '').ToLower() } finally { $hashAlgorithm.Dispose() }
        if ($lockedHash -ne $preflight.candidateHashes.$file) { throw "File changed before lock: $file" }
    }
    foreach ($file in $preflight.files) {
        $inputStream = [System.IO.File]::OpenRead((Join-Path $taskDir ('staged/' + $file)))
        try {
            $written.Add($file)
            $streams[$file].Position = 0
            $streams[$file].SetLength(0)
            $inputStream.CopyTo($streams[$file])
            $streams[$file].Flush($true)
        } finally { $inputStream.Dispose() }
    }
} catch {
    foreach ($file in $written) {
        $original = [System.IO.File]::OpenRead((Join-Path $backupDir $file))
        try {
            $streams[$file].Position = 0
            $streams[$file].SetLength(0)
            $original.CopyTo($streams[$file])
            $streams[$file].Flush($true)
        } finally { $original.Dispose() }
    }
    throw
} finally {
    foreach ($stream in $streams.Values) { $stream.Dispose() }
}
$receipt = @{revision='CHG-024'; backup=$backupDir; files=$preflight.files; hashes=$validation.hashes; status='PUBLISHED_TO_06_ONLY'}
$receipt | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $frameworkDir '05_验算核算/mapping-named-CHG024.json') -Encoding utf8
$receipt | ConvertTo-Json -Depth 5
