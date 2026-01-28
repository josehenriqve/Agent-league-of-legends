
$UV_PATH = "C:\Users\jqueiroz\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.8_qbz5n2kfra8p0\LocalCache\Local-Packages\Python38\Scripts\uv.exe"
$VENV_PYTHON = "C:\Users\jqueiroz\Documents\projeto\.venv\Scripts\python.exe"
$VENV_ADK = "C:\Users\jqueiroz\Documents\projeto\.venv\Scripts\adk.exe"

Write-Output "Installing dependencies..."
& $UV_PATH pip install -r requirements.txt

Write-Output "Starting ADK Web Interface..."
# We run 'adk web .' inside the project root
& $VENV_ADK web .
