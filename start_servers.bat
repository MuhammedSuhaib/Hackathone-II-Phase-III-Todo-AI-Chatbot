# Start the backend server in the background
Start-Process powershell -ArgumentList "-Command", "cd '$PWD\backend'; uvicorn main:app --host 0.0.0.0 --port 8000"

# Give backend a moment to start
Start-Sleep -Seconds 3

# Start the frontend server in the background
Start-Process powershell -ArgumentList "-Command", "cd '$PWD\frontend'; npm run dev"