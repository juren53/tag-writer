# Tag Writer Build Script
# Compiles Tag Writer into a standalone Windows executable

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Tag Writer Build Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if PyInstaller is installed
Write-Host "Checking for PyInstaller..." -ForegroundColor Yellow
$pyinstallerCheck = & python -c "import PyInstaller; print(PyInstaller.__version__)" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "PyInstaller not found. Installing..." -ForegroundColor Yellow
    & python -m pip install pyinstaller
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install PyInstaller. Exiting." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "PyInstaller version $pyinstallerCheck found" -ForegroundColor Green
}

Write-Host ""

# Clean previous build artifacts
Write-Host "Cleaning previous build artifacts..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist\tag-writer.exe") { Remove-Item -Force "dist\tag-writer.exe" }
Write-Host "Clean complete" -ForegroundColor Green
Write-Host ""

# Generate version_info.txt from constants.py
Write-Host "Generating version_info.txt..." -ForegroundColor Yellow
& python generate_version_info.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to generate version_info.txt. Exiting." -ForegroundColor Red
    exit 1
}
Write-Host ""

# Build the executable
Write-Host "Building tag-writer.exe..." -ForegroundColor Yellow
Write-Host "This may take several minutes..." -ForegroundColor Yellow
Write-Host ""

& pyinstaller tag-writer.spec --clean

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Build Complete!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Executable location: dist\tag-writer.exe" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Build Failed!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please check the error messages above." -ForegroundColor Yellow
    exit 1
}
