# Vgame Harness Check Script
# Run: powershell -ExecutionPolicy Bypass -File scripts/check.ps1

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$Root = Split-Path -Parent $PSScriptRoot
$LocalEnv = Join-Path $Root "local.env.bat"
if (Test-Path -LiteralPath $LocalEnv) {
    foreach ($line in Get-Content -LiteralPath $LocalEnv -Encoding UTF8) {
        if ($line -match '^\s*set\s+"?([A-Za-z_][A-Za-z0-9_]*)=(.*?)"?\s*$') {
            $name = $Matches[1]
            $value = $Matches[2].TrimEnd('"')
            if (-not [Environment]::GetEnvironmentVariable($name, "Process")) {
                [Environment]::SetEnvironmentVariable($name, $value, "Process")
            }
        }
    }
}
$DefaultVgameRoot = [System.IO.Path]::GetFullPath((Join-Path $Root "..\Vgame"))
$VgameRoot = if ($env:VGAME_ROOT) { $env:VGAME_ROOT } else { $DefaultVgameRoot }
$SkillRoot = if ($env:VGAME_SKILL_ROOT) { $env:VGAME_SKILL_ROOT } else { Join-Path $Root "skills" }
$FailCount = 0
$WarnCount = 0

function Write-Result {
    param([string]$Level, [string]$Message, [string]$Fix = "")

    $color = if ($Level -eq "FAIL") { "Red" } else { "Yellow" }
    Write-Host "[$Level] $Message" -ForegroundColor $color
    if ($Fix) {
        Write-Host "       FIX: $Fix" -ForegroundColor "Gray"
    }

    if ($Level -eq "FAIL") {
        $script:FailCount++
    } else {
        $script:WarnCount++
    }
}

Write-Host ""
Write-Host "=== Vgame Harness Check ===" -ForegroundColor "Cyan"
Write-Host "Design repo: $Root"
Write-Host "Vgame root : $VgameRoot"
Write-Host "Skill root : $SkillRoot"
Write-Host ""

Write-Host "--- Structure Check ---" -ForegroundColor "White"

$RequiredFiles = @(
    @{ Path = "AGENTS.md"; Desc = "agent entry" },
    @{ Path = "CLAUDE.md"; Desc = "agent instructions" },
    @{ Path = "ARCHITECTURE.md"; Desc = "architecture map" },
    @{ Path = "DESIGN.md"; Desc = "design rules" },
    @{ Path = "PLANS.md"; Desc = "plan index" },
    @{ Path = "SECURITY.md"; Desc = "security guide" },
    @{ Path = "CROSS-REPO-CHANGES.md"; Desc = "cross repo log" },
    @{ Path = "golden-principles.md"; Desc = "golden principles" },
    @{ Path = "quality-score.md"; Desc = "quality score" },
    @{ Path = "tech-debt-tracker.md"; Desc = "debt tracker" },
    @{ Path = "harness\maintenance-gates.md"; Desc = "maintenance gates" },
    @{ Path = "harness\integration-guide.md"; Desc = "skill integration guide" },
    @{ Path = "design\TEMPLATE.md"; Desc = "design template" },
    @{ Path = "proposals\TEMPLATE.md"; Desc = "proposal template" },
    @{ Path = "tasks\TEMPLATE.md"; Desc = "task template" },
    @{ Path = "knowledge-graph\KG-AI-RULES.md"; Desc = "knowledge graph AI rules" },
    @{ Path = "scripts\build_vgame_graph.py"; Desc = "knowledge graph build entry" },
    @{ Path = "scripts\check_vgame_graph.py"; Desc = "knowledge graph check entry" }
)

foreach ($item in $RequiredFiles) {
    $fullPath = Join-Path $Root $item.Path
    if (-not (Test-Path -LiteralPath $fullPath)) {
        Write-Result "FAIL" "Missing $($item.Desc): $($item.Path)" "Create the file or restore it from the harness scaffold."
    }
}

$RequiredDirs = @(
    "harness",
    "harness\concepts",
    "design",
    "proposals",
    "tasks",
    "plans",
    "knowledge-graph",
    "scripts"
)

foreach ($dir in $RequiredDirs) {
    $fullPath = Join-Path $Root $dir
    if (-not (Test-Path -LiteralPath $fullPath)) {
        Write-Result "FAIL" "Missing directory: $dir" "Create the directory and add a README if it should stay empty."
    }
}

Write-Host ""
Write-Host "--- Concept Docs Check ---" -ForegroundColor "White"

$ConceptDocs = @(
    "00-overview.md",
    "01-repo-as-source-of-truth.md",
    "02-mechanical-enforcement.md",
    "03-throughput-changes-merge.md",
    "04-entropy-management.md",
    "05-design-proposal-task.md"
)

foreach ($doc in $ConceptDocs) {
    $fullPath = Join-Path $Root "harness\concepts\$doc"
    if (-not (Test-Path -LiteralPath $fullPath)) {
        Write-Result "FAIL" "Missing harness concept: $doc" "Restore the concept document under harness/concepts."
    }
}

Write-Host ""
Write-Host "--- Repository Hygiene ---" -ForegroundColor "White"

$pendingPattern = "\bT" + "ODO\b"
$todoHits = Get-ChildItem -LiteralPath $Root -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Extension -in @(".md", ".ps1") } |
    Where-Object {
        $_.FullName -notmatch "\\.git\\" -and
        $_.FullName -notmatch "\\knowledge-graph\\understand-anything-new\\" -and
        $_.Name -ne "tech-debt-tracker.md"
    } |
    Select-String -Pattern $pendingPattern -ErrorAction SilentlyContinue |
    Select-Object -First 20

foreach ($hit in $todoHits) {
    $rel = $hit.Path.Replace($Root, "").TrimStart("\")
    Write-Result "WARN" "${rel}:$($hit.LineNumber) contains pending marker" "Register it in tech-debt-tracker.md or rewrite it as an explicit task."
}

Write-Host ""
Write-Host "--- Portable Path Check ---" -ForegroundColor "White"
$portableExtensions = @(".md", ".html", ".toml", ".py", ".ps1", ".bat")
$trackedFiles = git -c core.quotepath=false -C $Root ls-files 2>$null
foreach ($relativePath in $trackedFiles) {
    if ($relativePath -like "knowledge-graph/understand-anything-new/*") { continue }
    $extension = [System.IO.Path]::GetExtension($relativePath).ToLowerInvariant()
    if ($portableExtensions -notcontains $extension) { continue }
    $fullPath = Join-Path $Root $relativePath
    if (-not (Test-Path -LiteralPath $fullPath)) { continue }
    $matches = Select-String -LiteralPath $fullPath -Pattern '[A-Za-z]:\\' -Encoding UTF8
    foreach ($match in $matches) {
        Write-Result "FAIL" "$relativePath contains a machine-specific absolute path at line $($match.LineNumber)" "Use VGAME_* variables or a repository-relative path."
    }
}

$largeDocs = Get-ChildItem -LiteralPath $Root -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Extension -eq ".md" } |
    Where-Object {
        $_.FullName -notmatch "\\.git\\" -and
        $_.FullName -notmatch "\\knowledge-graph\\understand-anything-new\\"
    } |
    ForEach-Object {
        $lineCount = (Get-Content -LiteralPath $_.FullName -ErrorAction SilentlyContinue).Count
        [PSCustomObject]@{ File = $_; Lines = $lineCount }
    } |
    Where-Object { $_.Lines -gt 800 }

foreach ($doc in $largeDocs) {
    $rel = $doc.File.FullName.Replace($Root, "").TrimStart("\")
    Write-Result "WARN" "$rel has $($doc.Lines) lines" "Split the document or turn it into an index."
}

$tableExtensions = @(".xlsx", ".xlsm", ".csv")
$tableLikeFiles = Get-ChildItem -LiteralPath $Root -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { $tableExtensions -contains $_.Extension.ToLowerInvariant() } |
    Where-Object { $_.FullName -notmatch "\\.git\\" }

foreach ($file in $tableLikeFiles) {
    $rel = $file.FullName.Replace($Root, "").TrimStart("\")
    if ($file.Name -notmatch "sample|example|示例") {
        Write-Result "WARN" "$rel looks like a real table file" "Confirm it is a sample. Real configs should stay under VGAME_ROOT."
    }
}

Write-Host ""
Write-Host "--- External Roots Check ---" -ForegroundColor "White"

if (-not (Test-Path -LiteralPath $VgameRoot)) {
    Write-Result "WARN" "Vgame root not found: $VgameRoot" "Set VGAME_ROOT or clone/open the project root."
} else {
    $configPath = Join-Path $VgameRoot "Config"
    if (-not (Test-Path -LiteralPath $configPath)) {
        Write-Result "WARN" "Vgame Config directory not found under $VgameRoot" "Check whether the project path changed."
    }
}

if (-not $SkillRoot) {
    Write-Host "  [SKIP] VGAME_SKILL_ROOT is not configured." -ForegroundColor "DarkGray"
} elseif (-not (Test-Path -LiteralPath $SkillRoot)) {
    Write-Result "WARN" "Vgame skill root not found: $SkillRoot" "Check VGAME_SKILL_ROOT."
} else {
    $skillLayout = if (Test-Path -LiteralPath (Join-Path $SkillRoot "skills")) {
        @("config.toml", "skills", "agents")
    } else {
        @("config.toml", "agents", "vgame-core-understanding")
    }
    foreach ($path in $skillLayout) {
        $fullPath = Join-Path $SkillRoot $path
        if (-not (Test-Path -LiteralPath $fullPath)) {
            Write-Result "WARN" "Skill root missing $path" "Check Vgame agent skill installation."
        }
    }
}

Write-Host ""
Write-Host "--- Git Check ---" -ForegroundColor "White"

try {
    $upstream = git -C $Root rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>$null
    $pendingCommits = if ($upstream) {
        git -C $Root log --oneline "$upstream..HEAD" 2>$null
    } else {
        git -C $Root log --oneline -1 2>$null
    }
    if ($pendingCommits) {
        $badCommits = $pendingCommits | Where-Object {
            $_ -notmatch "^[0-9a-f]+\s+(feat|fix|docs|style|refactor|perf|test|chore|ci|build|revert)(\(.+\))?:\s" -and
            $_ -notmatch "^[0-9a-f]+\s+Merge"
        }
        foreach ($commit in $badCommits) {
            Write-Result "WARN" "Non-conventional commit: $commit" "Use format like docs(harness): add Vgame scaffold."
        }
    } else {
        Write-Host "  [PASS] No unpushed commits require message validation." -ForegroundColor "DarkGray"
    }
} catch {
    Write-Host "  [SKIP] Git is unavailable or this is not a git repo." -ForegroundColor "DarkGray"
}

Write-Host ""

if ($FailCount -gt 0) {
    $status = "FAIL"
    $color = "Red"
} elseif ($WarnCount -gt 0) {
    $status = "WARN"
    $color = "Yellow"
} else {
    $status = "PASS"
    $color = "Green"
}

Write-Host "=== Result: $status (FAIL: $FailCount, WARN: $WarnCount) ===" -ForegroundColor $color
Write-Host ""

if ($FailCount -gt 0) {
    exit 1
}
