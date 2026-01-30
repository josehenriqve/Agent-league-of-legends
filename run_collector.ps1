$VENV_PYTHON = ".\.venv\Scripts\python.exe"
$VENV_ADK = ".\.venv\Scripts\adk.exe"

# Ensure dependencies are installed (optional check, but good for robust scripts)
# & $VENV_PYTHON -m pip install -r requirements.txt

# Run the Data Collector agent using ADK Web UI
& $VENV_ADK web data_collector
