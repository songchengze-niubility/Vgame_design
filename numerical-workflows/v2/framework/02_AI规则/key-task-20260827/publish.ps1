$ErrorActionPreference = 'Stop'
$taskRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
if (Test-Path -LiteralPath (Join-Path $taskRoot '05_验算核算/章节任务纠偏_20260827/plan.json')) {
    throw 'Historical batch superseded: rejected daily/weekly unlock edits must not be reapplied.'
}
$taskRun = Join-Path $taskRoot '05_验算核算/映射之匙任务_20260827'
$taskPlan = Get-Content -LiteralPath (Join-Path $taskRun 'plan.json') -Raw | ConvertFrom-Json
$taskCheck = Get-Content -LiteralPath (Join-Path $taskRun 'staged-validation.json') -Raw | ConvertFrom-Json
if ($taskCheck.status -ne 'PASS_STATIC_WITH_RUNTIME_GATES') { throw 'Staged validation has not passed' }
$taskFiles = @($taskPlan.files) + @($taskPlan.reports)
$taskHandles = @{}
$taskOriginals = @{}
$taskCreated = [Collections.Generic.List[string]]::new()
$taskWritten = [Collections.Generic.List[string]]::new()
function TaskHash([byte[]]$Bytes) { [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($Bytes)).ToLowerInvariant() }
try {
    foreach ($f in $taskFiles) {
        $resolved = [IO.Path]::GetFullPath($f.source)
        $allowed = [IO.Path]::GetFullPath((Join-Path $taskRoot '06_最终配置')) + [IO.Path]::DirectorySeparatorChar
        if (-not $resolved.StartsWith($allowed,[StringComparison]::OrdinalIgnoreCase)) { throw "Out of scope: $resolved" }
        $staged = Join-Path (Join-Path $taskRun 'stage') $f.file
        if ((TaskHash ([IO.File]::ReadAllBytes($staged))) -ne $f.stage_sha256) { throw "Stage drift: $staged" }
        if ($null -eq $f.sha256) {
            $stream = [IO.File]::Open($resolved,[IO.FileMode]::CreateNew,[IO.FileAccess]::ReadWrite,[IO.FileShare]::None)
            $taskCreated.Add($resolved)
            $taskOriginals[$resolved] = [byte[]]@()
        } else {
            $stream = [IO.File]::Open($resolved,[IO.FileMode]::Open,[IO.FileAccess]::ReadWrite,[IO.FileShare]::None)
            $bytes = [byte[]]::new($stream.Length)
            $stream.ReadExactly($bytes)
            if ((TaskHash $bytes) -ne $f.sha256) { $stream.Dispose(); throw "Destination drift: $resolved" }
            $taskOriginals[$resolved] = $bytes
        }
        $taskHandles[$resolved] = $stream
    }
    foreach ($f in $taskFiles) {
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
    foreach ($stream in $taskHandles.Values) { $stream.Dispose() }
    $taskHandles.Clear()
    foreach ($resolved in $taskCreated) { Remove-Item -LiteralPath $resolved }
    throw
} finally {
    foreach ($stream in $taskHandles.Values) { $stream.Dispose() }
}
foreach ($f in $taskFiles) {
    if ((TaskHash ([IO.File]::ReadAllBytes($f.source))) -ne $f.stage_sha256) { throw "Post-write hash mismatch: $($f.file)" }
}
"Published $($taskPlan.files.Count) workbooks and $($taskPlan.reports.Count) reports."
$global:LASTEXITCODE = 0
