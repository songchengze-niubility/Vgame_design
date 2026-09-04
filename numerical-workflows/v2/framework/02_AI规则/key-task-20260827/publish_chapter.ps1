$ErrorActionPreference = 'Stop'
$taskRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$taskRun = Join-Path $taskRoot '05_验算核算/章节任务纠偏_20260827'
$taskPlan = Get-Content -LiteralPath (Join-Path $taskRun 'plan.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$taskCheck = Get-Content -LiteralPath (Join-Path $taskRun 'staged-validation.json') -Raw -Encoding UTF8 | ConvertFrom-Json
if ($taskCheck.status -ne 'PASS_STATIC_WITH_RUNTIME_GATES') { throw 'Staged validation has not passed' }
$taskHandles = @{}
$taskOriginals = @{}
$taskWritten = [Collections.Generic.List[string]]::new()
function TaskHash([byte[]]$Bytes) { [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($Bytes)).ToLowerInvariant() }
try {
    foreach ($f in $taskPlan.files) {
        $resolved = [IO.Path]::GetFullPath($f.source)
        $allowed = [IO.Path]::GetFullPath((Join-Path $taskRoot '06_最终配置')) + [IO.Path]::DirectorySeparatorChar
        if (-not $resolved.StartsWith($allowed,[StringComparison]::OrdinalIgnoreCase)) { throw "Out of scope: $resolved" }
        $staged = Join-Path (Join-Path $taskRun 'stage') $f.file
        if ((TaskHash ([IO.File]::ReadAllBytes($staged))) -ne $f.stage_sha256) { throw "Stage drift: $staged" }
        $stream = [IO.File]::Open($resolved,[IO.FileMode]::Open,[IO.FileAccess]::ReadWrite,[IO.FileShare]::None)
        $taskHandles[$resolved] = $stream
        $bytes = [byte[]]::new($stream.Length)
        $stream.ReadExactly($bytes)
        if ((TaskHash $bytes) -ne $f.sha256) { throw "Destination drift: $resolved" }
        $taskOriginals[$resolved] = $bytes
    }
    foreach ($f in $taskPlan.files) {
        $resolved = [IO.Path]::GetFullPath($f.source)
        $bytes = [IO.File]::ReadAllBytes((Join-Path (Join-Path $taskRun 'stage') $f.file))
        $stream = $taskHandles[$resolved]
        $taskWritten.Add($resolved)
        $stream.Position=0; $stream.SetLength(0); $stream.Write($bytes); $stream.Flush($true)
    }
} catch {
    foreach ($resolved in $taskWritten) {
        $stream=$taskHandles[$resolved]; $bytes=$taskOriginals[$resolved]
        $stream.Position=0; $stream.SetLength(0); $stream.Write($bytes); $stream.Flush($true)
    }
    throw
} finally {
    foreach ($stream in $taskHandles.Values) { $stream.Dispose() }
}
foreach ($f in $taskPlan.files) {
    if ((TaskHash ([IO.File]::ReadAllBytes($f.source))) -ne $f.stage_sha256) { throw "Post-write hash mismatch: $($f.file)" }
}
"Published chapter correction: 2 workbooks and 1 report."
$global:LASTEXITCODE = 0
