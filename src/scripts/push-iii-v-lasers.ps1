[CmdletBinding()]
param (
    [string]$CommitMessage = "Add III-V laser notes"
)

$ErrorActionPreference = "Stop"
$repositoryRoot = Split-Path -Parent $PSScriptRoot
$file = "iii-v_lasers.md"

Set-Location -LiteralPath $repositoryRoot

if (-not (Test-Path -LiteralPath $file -PathType Leaf)) {
    throw "Cannot find $file in the repository root."
}

$branch = (& git branch --show-current).Trim()
if ($LASTEXITCODE -ne 0) {
    throw "Could not determine the current Git branch."
}
if (-not $branch) {
    throw "Cannot push from a detached HEAD."
}

$remotes = & git remote
if ($LASTEXITCODE -ne 0) {
    throw "Could not list Git remotes."
}
if ($remotes -notcontains "origin") {
    throw "Git remote 'origin' is not configured."
}

& git add -- $file
if ($LASTEXITCODE -ne 0) {
    throw "Could not stage $file."
}

& git diff --cached --quiet -- $file
$diffExitCode = $LASTEXITCODE
if ($diffExitCode -eq 0) {
    Write-Host "$file has no staged changes; nothing to commit or push."
    exit 0
}
if ($diffExitCode -ne 1) {
    throw "Could not check staged changes for $file."
}

& git commit --only -m $CommitMessage -- $file
if ($LASTEXITCODE -ne 0) {
    throw "Could not commit $file."
}

& git push origin $branch
if ($LASTEXITCODE -ne 0) {
    throw "Could not push branch '$branch' to origin."
}

Write-Host "Pushed $file to origin/$branch."
