@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul 2>&1

set "SCRIPT_DIR=%~dp0"
set "REPO_NAME=VisoMaster-Fusion"
set "REPO_DIR=%SCRIPT_DIR%%REPO_NAME%"
set "VENV_DIR=%REPO_DIR%\.venv"
set "LOG_FILE=%SCRIPT_DIR%setup_visomaster.log"
set "PYTHON_EXE=python"
set "PIP_EXE=%VENV_DIR%\Scripts\pip.exe"
set "PYTHON_VENV=%VENV_DIR%\Scripts\python.exe"

call :log "=== VisoMaster Setup gestartet %DATE% %TIME% ==="
call :log "Arbeitsverzeichnis: %SCRIPT_DIR%"

:: --- Python 3.11 pruefen ---
call :log "Pruefe Python 3.11 ..."
for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set "PY_VER=%%v"
echo !PY_VER! | findstr /b "3.11" >nul
if errorlevel 1 (
    call :fail "Python 3.11 nicht gefunden. Gefunden: !PY_VER!"
    exit /b 1
)
call :log "Gefunden: Python !PY_VER!"

:: --- Git pruefen ---
call :log "Pruefe Git ..."
for /f "tokens=*" %%g in ('git --version 2^>^&1') do set "GIT_VER=%%g"
if errorlevel 1 (
    call :fail "Git nicht gefunden."
    exit /b 1
)
call :log "Gefunden: !GIT_VER!"

:: --- NVIDIA Treiber pruefen ---
call :log "Pruefe NVIDIA Treiber ..."
nvidia-smi >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    call :log "WARNUNG: nvidia-smi nicht gefunden oder Fehler."
) else (
    call :log "nvidia-smi erfolgreich (Details im Log)."
)

:: --- Repo klonen oder updaten ---
if exist "%REPO_DIR%\.git" (
    call :log "Repo vorhanden - hole Updates ..."
    git -C "%REPO_DIR%" pull origin main 2>&1 | findstr /v "^$"
    if errorlevel 1 (
        git -C "%REPO_DIR%" pull origin master 2>&1 | findstr /v "^$"
    )
) else (
    call :log "Klone %REPO_NAME% ..."
    git clone https://github.com/visomaster/%REPO_NAME%.git "%REPO_DIR%" 2>&1
    if errorlevel 1 (
        call :fail "Git-Clone fehlgeschlagen."
        exit /b 1
    )
)

:: --- venv erstellen oder wiederverwenden ---
if exist "%VENV_DIR%\Scripts\activate.bat" (
    call :log "venv existiert bereits."
) else (
    call :log "Erstelle venv ..."
    python -m venv "%VENV_DIR%"
    if errorlevel 1 (
        call :fail "venv konnte nicht erstellt werden."
        exit /b 1
    )
)

:: --- pip/wheel/setuptools upgraden ---
call :log "Upgrade pip/wheel/setuptools ..."
"%PIP_EXE%" install --upgrade pip wheel 2>&1
"%PIP_EXE%" install "setuptools<82" 2>&1

:: --- PyTorch cu128 installieren ---
call :log "Installiere PyTorch cu128 (stable) ..."
"%PIP_EXE%" install torch torchvision --index-url https://download.pytorch.org/whl/cu128 2>&1

:: --- onnxruntime-gpu installieren ---
call :log "Installiere onnxruntime-gpu 1.20.1 ..."
"%PIP_EXE%" install onnxruntime-gpu==1.20.1 2>&1

:: --- Requirements-Datei suchen (flexibel) ---
call :log "Suche requirements-Datei ..."
set "REQ_FILE="

:: Bekannte Pfade in Prioritaetsreihenfolge pruefen
set CANDIDATES=
set CANDIDATES=%CANDIDATES% "%REPO_DIR%\requirements.txt"
set CANDIDATES=%CANDIDATES% "%REPO_DIR%\requirements\requirements.txt"
set CANDIDATES=%CANDIDATES% "%REPO_DIR%\requirements\base.txt"
set CANDIDATES=%CANDIDATES% "%REPO_DIR%\requirements\gpu.txt"
set CANDIDATES=%CANDIDATES% "%REPO_DIR%\requirements-gpu.txt"
set CANDIDATES=%CANDIDATES% "%REPO_DIR%\requirements_gpu.txt"
set CANDIDATES=%CANDIDATES% "%REPO_DIR%\setup\requirements.txt"

for %%f in (%CANDIDATES%) do (
    if "!REQ_FILE!"=="" (
        if exist %%f (
            set "REQ_FILE=%%~f"
            call :log "Requirements gefunden: %%~f"
        )
    )
)

:: Fallback: alle requirements*.txt im Repo suchen
if "!REQ_FILE!"=="" (
    call :log "Kein bekannter Pfad gefunden - durchsuche Repo ..."
    for /f "delims=" %%f in ('dir /b /s "%REPO_DIR%\requirements*.txt" 2^>nul') do (
        if "!REQ_FILE!"=="" (
            set "REQ_FILE=%%f"
            call :log "Requirements per Suche gefunden: %%f"
        )
    )
)

if "!REQ_FILE!"=="" (
    call :fail "Keine requirements-Datei gefunden im Repo. Repo-Layout geaendert?"
    call :log "Tipp: Repo-Inhalt:"
    dir /b "%REPO_DIR%" >> "%LOG_FILE%" 2>&1
    exit /b 1
)

:: --- Requirements installieren ---
call :log "Installiere Requirements aus !REQ_FILE! ..."
"%PIP_EXE%" install -r "!REQ_FILE!" 2>&1
if errorlevel 1 (
    call :fail "pip install -r !REQ_FILE! fehlgeschlagen."
    exit /b 1
)

:: --- Fertig ---
call :log ""
call :log "=== VisoMaster Setup abgeschlossen! ==="
call :log "Starten mit: %VENV_DIR%\Scripts\python.exe app.py"
echo.
echo [OK] Setup abgeschlossen. Log: %LOG_FILE%
exit /b 0

:: ===================== Hilfsfunktionen =====================
:log
set "MSG=[ %TIME%] %~1"
echo !MSG!
echo !MSG! >> "%LOG_FILE%"
exit /b 0

:fail
set "MSG=FAIL: %~1"
echo !MSG!
echo !MSG! >> "%LOG_FILE%"
exit /b 0
