<#
.SYNOPSIS
    Sets up virtual environment and continuously runs the Python program located at ./src/main.py, restarting it upon exit.

.DESCRIPTION
    This script:
    1. Creates a virtual environment (.venv) if it doesn't exist
    2. Activates the virtual environment
    3. Installs dependencies from requirements.txt if needed
    4. Enters an infinite loop where it starts the specified Python program
    If the program exits, the script waits for 2 seconds and then restarts it.
    The loop can be interrupted by pressing Ctrl+C, which triggers the catch block to display a stop message and error details.

.NOTES
    - Requires Python to be installed and accessible via the "python" command.
    - Intended for streaming or testing scenarios where automatic restarts are useful.
    - Automatically manages virtual environment and dependencies.

.EXAMPLE
    PS> .\run.ps1
#>

# Function to check if dependencies are installed
function Test-DependenciesInstalled {
    $requirementsPath = "./requirements.txt"
    if (-not (Test-Path $requirementsPath)) {
        Write-Host "requirements.txt not found, skipping dependency check"
        return $true
    }

    try {
        $requirements = Get-Content $requirementsPath | Where-Object { $_ -match "^[^#]" -and $_.Trim() -ne "" }
        foreach ($requirement in $requirements) {
            $packageName = ($requirement -split "==")[0].Trim()
            $result = & ".venv/Scripts/python" -m pip show $packageName 2>$null
            if (-not $result) {
                return $false
            }
        }
        return $true
    }
    catch {
        return $false
    }
}

try {
    # Check if virtual environment exists
    if (-not (Test-Path ".venv")) {
        Write-Host "Creating virtual environment..."
        & "python" -m venv .venv
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to create virtual environment"
        }
        Write-Host "Virtual environment created successfully."
    }

    # Activate virtual environment
    Write-Host "Activating virtual environment..."
    & ".venv/Scripts/Activate.ps1"

    # Check if dependencies need to be installed
    if (-not (Test-DependenciesInstalled)) {
        Write-Host "Installing dependencies..."
        & ".venv/Scripts/python" -m pip install -r requirements.txt
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to install dependencies"
        }
        Write-Host "Dependencies installed successfully."
    } else {
        Write-Host "Dependencies already installed."
    }

    # Run the application
    while ($true) {
        Write-Host "Starting program..."
        & ".venv/Scripts/python" "./src/main.py"
        $exitCode = $LASTEXITCODE

        if ($exitCode -eq 0) {
            Write-Host "Program was closed by user. Exiting..."
            break
        } else {
            Write-Host "Program exited with error code $exitCode. Restarting in 2 seconds... Press Ctrl+C to stop."
            Start-Sleep -Seconds 2
        }
    }
}
catch {
    Write-Host "Stopped by user or error occurred."
    Write-Host "Error details:"
    Write-Host $_  # This shows the error that was caught
}