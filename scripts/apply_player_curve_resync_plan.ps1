param(
    [Parameter(Mandatory = $true)]
    [string]$PlanPath
)

$ErrorActionPreference = 'Stop'

function Get-Sha256([string]$Path) {
    return (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToLowerInvariant()
}

function Assert-Hash([string]$Path, [string]$Expected) {
    $actual = Get-Sha256 $Path
    if ($actual -ne $Expected.ToLowerInvariant()) {
        throw "文件已变化，停止写入：$Path expected=$Expected actual=$actual"
    }
}

$resolvedPlan = (Resolve-Path -LiteralPath $PlanPath).Path
$plan = Get-Content -Raw -Encoding UTF8 -LiteralPath $resolvedPlan | ConvertFrom-Json
$difficultyPath = [string]$plan.source.difficulty_path
$levelPath = [string]$plan.source.level_path
$roguePath = [string]$plan.source.roguelike_path_readonly

Assert-Hash $difficultyPath ([string]$plan.source.difficulty_sha256)
Assert-Hash $levelPath ([string]$plan.source.level_sha256)
Assert-Hash $roguePath ([string]$plan.source.roguelike_sha256)

$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$outputDir = Split-Path -Parent $resolvedPlan
$backupDir = Join-Path $outputDir "backup-player-curve-resync-$stamp"
New-Item -ItemType Directory -Path $backupDir | Out-Null
Copy-Item -LiteralPath $difficultyPath -Destination (Join-Path $backupDir '全玩法难度填写表.xlsx')
Copy-Item -LiteralPath $levelPath -Destination (Join-Path $backupDir 'level.xlsx')

$excel = New-Object -ComObject Excel.Application
$difficultyWorkbook = $null
$levelWorkbook = $null
$difficultyLinks = 0
$levelLinks = 0
$mappingFormulaBefore = @{}
$result = $null

try {
    $excel.Visible = $false
    $excel.DisplayAlerts = $false
    $excel.AskToUpdateLinks = $false
    $excel.Calculation = -4135

    $difficultyWorkbook = $excel.Workbooks.Open($difficultyPath, 0, $false)
    if ($difficultyWorkbook.ReadOnly) {
        throw "难度源表以只读方式打开，可能正被占用：$difficultyPath"
    }
    $curveSheet = $difficultyWorkbook.Worksheets.Item('_玩家曲线')
    foreach ($row in $plan.curve_rows) {
        $targetRow = [int]$row.target_row
        for ($index = 0; $index -lt 9; $index++) {
            $cell = $curveSheet.Cells.Item($targetRow, $index + 1)
            $value = $row.values[$index]
            if ($null -eq $value) {
                $cell.Value = $null
            }
            else {
                $cell.Value = [double]$value
            }
        }
    }

    $mappingSheet = $difficultyWorkbook.Worksheets.Item('映射')
    for ($row = 6; $row -le 33; $row++) {
        $mappingFormulaBefore[[string]$row] = [string]$mappingSheet.Cells.Item($row, 10).Formula
    }
    foreach ($write in $plan.source_writes) {
        $sheet = $difficultyWorkbook.Worksheets.Item([string]$write.sheet)
        $cell = $sheet.Cells.Item([int]$write.row, [int]$write.column)
        if ([string]$cell.Formula -like '=*') {
            throw "目标单元格为公式，停止覆盖：$($write.sheet)!$($write.cell)"
        }
        $cell.Value = [int]$write.new_level
    }

    $excel.Calculation = -4105
    $difficultyWorkbook.ForceFullCalculation = $true
    $excel.CalculateFullRebuild()
    $excel.CalculateUntilAsyncQueriesDone()
    foreach ($row in 6..33) {
        $actual = [string]$mappingSheet.Cells.Item($row, 10).Formula
        if ($actual -ne $mappingFormulaBefore[[string]$row]) {
            throw "映射线性公式发生变化：映射!J$row"
        }
    }
    $links = $difficultyWorkbook.LinkSources(1)
    if ($null -ne $links) {
        $difficultyLinks = @($links).Count
    }
    $difficultyWorkbook.Save()
    $difficultyWorkbook.Close($false)
    $difficultyWorkbook = $null

    $excel.Calculation = -4135
    $levelWorkbook = $excel.Workbooks.Open($levelPath, 0, $false)
    if ($levelWorkbook.ReadOnly) {
        throw "level.xlsx以只读方式打开，可能正被占用：$levelPath"
    }
    foreach ($write in $plan.level_writes) {
        $sheet = $levelWorkbook.Worksheets.Item([string]$write.sheet)
        $cell = $sheet.Cells.Item([int]$write.row, [int]$write.column)
        if ([string]$cell.Formula -like '=*') {
            throw "Grade目标单元格为公式，停止覆盖：$($write.sheet)!$($write.cell)"
        }
        if ([double]$cell.Value2 -ne [double]$write.old_grade) {
            throw "Grade旧值已变化：LevelId=$($write.level_id) expected=$($write.old_grade) actual=$($cell.Value2)"
        }
        $cell.Value = [int]$write.new_grade
    }
    $excel.Calculation = -4105
    $levelWorkbook.ForceFullCalculation = $true
    $excel.CalculateFullRebuild()
    $excel.CalculateUntilAsyncQueriesDone()
    $links = $levelWorkbook.LinkSources(1)
    if ($null -ne $links) {
        $levelLinks = @($links).Count
    }
    $levelWorkbook.Save()
    $levelWorkbook.Close($false)
    $levelWorkbook = $null

    Assert-Hash $roguePath ([string]$plan.source.roguelike_sha256)
    $result = [ordered]@{
        generated_at = (Get-Date).ToString('s')
        status = 'PASS'
        plan = $resolvedPlan
        backup_dir = $backupDir
        difficulty = [ordered]@{
            path = $difficultyPath
            sha256_before = [string]$plan.source.difficulty_sha256
            sha256_after = Get-Sha256 $difficultyPath
            curve_rows_written = @($plan.curve_rows).Count
            grade_cells_written = @($plan.source_writes).Count
            external_links = $difficultyLinks
        }
        level = [ordered]@{
            path = $levelPath
            sha256_before = [string]$plan.source.level_sha256
            sha256_after = Get-Sha256 $levelPath
            grade_cells_written = @($plan.level_writes).Count
            grade_cells_changed = [int]$plan.checks.level_changed_count
            external_links = $levelLinks
        }
        roguelike = [ordered]@{
            path = $roguePath
            unchanged = $true
            sha256 = Get-Sha256 $roguePath
        }
    }
}
finally {
    if ($null -ne $difficultyWorkbook) {
        $difficultyWorkbook.Close($false)
        [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($difficultyWorkbook)
    }
    if ($null -ne $levelWorkbook) {
        $levelWorkbook.Close($false)
        [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($levelWorkbook)
    }
    $excel.Quit()
    [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($excel)
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}

$reportPath = Join-Path $outputDir "player-curve-resync-apply-report-$stamp.json"
[IO.File]::WriteAllText($reportPath, ($result | ConvertTo-Json -Depth 20), [Text.UTF8Encoding]::new($false))
$result | ConvertTo-Json -Depth 20
