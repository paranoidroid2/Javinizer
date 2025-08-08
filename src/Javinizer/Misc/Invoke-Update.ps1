Write-Progress -Status "Updating Javinizer" -Activity "Fetching Javinizer settings files..." -PercentComplete 25
$modulePath = (Get-InstalledModule Javinizer -ErrorAction SilentlyContinue).InstalledLocation

if (-not $modulePath) {
    Write-Error "Could not determine the installation path of the Javinizer module."
    return
}

# Backup settings and data files
$backupPath = Join-Path -Path $env:TEMP -ChildPath "Javinizer_Backup_$(Get-Date -Format 'yyyyMMddHHmmss')"
New-Item -Path $backupPath -ItemType Directory | Out-Null

$filesToBackup = @(
    'jvSettings.json',
    'jvThumbs.csv',
    'jvGenres.csv',
    'jvUncensor.csv',
    'jvHistory.csv',
    'jvTags.csv'
)

foreach ($file in $filesToBackup) {
    $sourcePath = Join-Path -Path $modulePath -ChildPath $file
    if (Test-Path $sourcePath) {
        Copy-Item -Path $sourcePath -Destination $backupPath -Force
    }
}
Write-Host "Backed up settings and data to $backupPath"


# Check if the module path is a git repository
$gitPath = Join-Path -Path $modulePath -ChildPath '.git'
if (-not (Test-Path $gitPath)) {
    Write-Error "The module installation at $modulePath does not appear to be a git repository. Cannot update using git pull."
    Write-Error "Please install by cloning your forked repository."
    return
}

# Update from git repository
try {
    Write-Progress -Status "Updating Javinizer" -Activity "Pulling latest changes from your git repository..." -PercentComplete 50

    # Temporarily change location to the module path to run git pull
    Push-Location -Path $modulePath

    git pull

    Pop-Location

    Write-Host "Successfully pulled latest changes from the git repository."
} catch {
    Write-Error "Error occurred when running 'git pull' in $modulePath: $PSItem"
    # Restore from backup if git pull fails
    Write-Host "Restoring files from backup..."
    Copy-Item -Path (Join-Path $backupPath '*') -Destination $modulePath -Force -Recurse
    return
}

# Restore settings and data files from backup
try {
    Write-Progress -Status "Updating Javinizer" -Activity "Restoring settings and data files..." -PercentComplete 75
    Copy-Item -Path (Join-Path $backupPath '*') -Destination $modulePath -Force -Recurse
    Write-Host "Restored settings and data from backup."
}
catch {
    Write-Error "Failed to restore settings from backup. Your backed up files are in $backupPath"
    Write-Error $_
}

Write-Host "Javinizer update completed! Restart your shell to continue." -ForegroundColor Green
