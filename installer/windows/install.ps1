Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..") ).Path
$ShortcutFlag = $false
if ($args -contains "-SkipShortcut") { $ShortcutFlag = $true }

function Write-Info([string]$Message) {
    Write-Host "[installer] $Message"
}

function Ensure-Command([string]$Name, [string]$InstallCommand, [string]$DisplayName) {
    if (Get-Command $Name -ErrorAction SilentlyContinue) { return }
    Write-Info "Installing $DisplayName..."
    Invoke-Expression $InstallCommand
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "$DisplayName could not be installed or was not found on PATH."
    }
}

function Ensure-VisualStudioBuildTools {
    Write-Info "Checking for Visual Studio Build Tools..."
    $vswhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"
    if (Test-Path $vswhere) {
        $result = & $vswhere -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
        if ($LASTEXITCODE -eq 0 -and $result) {
            Write-Info "Visual Studio Build Tools are already installed."
            return
        }
    }

    Write-Info "Installing Visual Studio Build Tools for native dependencies..."
    winget install --id Microsoft.VisualStudio.2022.BuildTools --override "--wait --passive --add Microsoft.VisualStudio.Component.VC.Tools.x86.x64 --add Microsoft.VisualStudio.Component.Windows11SDK.22621 --includeRecommended" --accept-source-agreements --accept-package-agreements
    if (-not (Test-Path $vswhere)) {
        Write-Info "Visual Studio Build Tools may still be installing. Please rerun the installer if the toolchain is not yet visible."
    }
}

function Ensure-Environment {
    Ensure-Command "git" "winget install --id Git.Git --source winget --accept-source-agreements --accept-package-agreements" "Git"
    Ensure-Command "python" "winget install --id Python.Python.3.14 --source winget --accept-source-agreements --accept-package-agreements" "Python 3.14"
    Ensure-Command "ffmpeg" "winget install --id Gyan.Dev.FFmpeg --source winget --accept-source-agreements --accept-package-agreements" "FFmpeg"
    Ensure-VisualStudioBuildTools
}

function Ensure-VenvAndDeps {
    $venvPath = Join-Path $RepoRoot ".venv"
    if (-not (Test-Path $venvPath)) {
        Write-Info "Creating virtual environment..."
        & python -m venv $venvPath
    }

    $pythonExe = Join-Path $venvPath "Scripts\python.exe"
    Write-Info "Installing Python dependencies..."
    & $pythonExe -m pip install --upgrade pip setuptools wheel
    & $pythonExe -m pip install -r (Join-Path $RepoRoot "requirements.txt")

    if (-not (Test-Path (Join-Path $RepoRoot "models\inswapper_128_fp16.onnx"))) {
        Write-Info "Downloading model files..."
        $models = @(
            @{ Name = "gfpgan-1024.onnx"; Url = "https://huggingface.co/hacksider/deep-live-cam/resolve/main/gfpgan-1024.onnx" },
            @{ Name = "inswapper_128_fp16.onnx"; Url = "https://huggingface.co/hacksider/deep-live-cam/resolve/main/inswapper_128_fp16.onnx" }
        )
        foreach ($model in $models) {
            $target = Join-Path $RepoRoot "models\$($model.Name)"
            if (-not (Test-Path $target)) {
                Invoke-WebRequest -Uri $model.Url -OutFile $target
            }
        }
    }
}

function Create-Shortcut {
    $shortcutName = "Artesys-DLC"
    $shortcutTarget = Join-Path $RepoRoot "generate_desktop_shortcut.py"
    $desktopDir = Join-Path $env:USERPROFILE "Desktop"
    if (-not (Test-Path $desktopDir)) { New-Item -ItemType Directory -Path $desktopDir | Out-Null }
    & python $shortcutTarget --name $shortcutName --install-dir $desktopDir
    Write-Info "Launcher created on Desktop."
}

Write-Info "Starting Windows bootstrap install..."
Ensure-Environment
Ensure-VenvAndDeps

if (-not $ShortcutFlag) {
    Create-Shortcut
}

Write-Info "Installation complete. Open the app by running:"
Write-Host "  $RepoRoot\.venv\Scripts\python.exe $RepoRoot\run.py"
