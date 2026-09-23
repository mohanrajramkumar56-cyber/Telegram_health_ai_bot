# HealthBot-Proto: Auto Setup & Run Script (Windows PowerShell)

# 1. Create venv
python -m venv venv

# 2. Activate venv
.\venv\Scripts\Activate.ps1

# 3. Install backend requirements (FastAPI, etc.)
pip install -r backend\requirements.txt

# 4. Install Rasa core & SDK
cd rasa
pip install rasa==3.6.18 rasa-sdk==3.6.2

# 5. Train Rasa model
rasa train

Write-Host "\n---- LAUNCHING SERVERS ----\n"

# 6. Start Rasa action server in background
Start-Process powershell -ArgumentList 'cd rasa; .\..\venv\Scripts\Activate.ps1; rasa run actions --port 5055' -WindowStyle Minimized

# 7. Start Rasa chatbot API in background
Start-Process powershell -ArgumentList 'cd rasa; .\..\venv\Scripts\Activate.ps1; rasa run --enable-api --cors "*" --port 5005' -WindowStyle Minimized

# 8. Start FastAPI backend server in background
Start-Process powershell -ArgumentList 'cd backend; ..\venv\Scripts\Activate.ps1; uvicorn app:app --host 0.0.0.0 --port 8000' -WindowStyle Minimized

Write-Host "\nAll services launched.\n"
Write-Host "Test with:"
Write-Host 'curl -X POST http://localhost:5005/webhooks/rest/webhook -H "Content-Type: application/json" -d "{\"sender\":\"testuser\", \"message\":\"What are the symptoms of malaria?\"}"'
