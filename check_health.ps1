# check_health.ps1 - Script de Diagnóstico para Sistema de Sensores
Clear-Host
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "   🔍 DIAGNÓSTICO DEL SISTEMA DE SENSORES" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan

# 1. Verificar Contenedores
Write-Host "`n[1] Verificando Docker..." -NoNewline
$dockerStatus = docker ps --filter "name=sensor_server_app" --format "{{.Status}}"
if ($dockerStatus -like "*Up*") {
    Write-Host " OK (Corriendo)" -ForegroundColor Green
} else {
    Write-Host " ERROR (Contenedor detenido o no existe)" -ForegroundColor Red
}

# 2. Identificar IP para el ESP32
Write-Host "[2] Buscando IP para el ESP32..." -NoNewline
$localIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { 
    $_.InterfaceAlias -notlike "*vEthernet*" -and 
    $_.InterfaceAlias -notlike "*Loopback*" -and 
    $_.InterfaceAlias -notlike "*Docker*" 
}).IPAddress[0]

if ($localIP) {
    Write-Host " OK" -ForegroundColor Green
    Write-Host "    👉 IP detectada: $localIP" -ForegroundColor Yellow
    Write-Host "    👉 URL para el ESP32: http://$($localIP):8000/api/sensor-data" -ForegroundColor Yellow
} else {
    Write-Host " ERROR (No se detectó IP válida)" -ForegroundColor Red
}

# 3. Verificar Puerto 8000
Write-Host "[3] Verificando puerto 8000..." -NoNewline
$portCheck = Test-NetConnection -ComputerName localhost -Port 8000 -WarningAction SilentlyContinue
if ($portCheck.TcpTestSucceeded) {
    Write-Host " OK (Escuchando)" -ForegroundColor Green
} else {
    Write-Host " ERROR (Puerto cerrado o bloqueado)" -ForegroundColor Red
}

# 4. Validar API KEY
Write-Host "[4] Validando API KEY del archivo .env..." -NoNewline
if (Test-Path ".env") {
    $envFile = Get-Content ".env" | Select-String "SENSOR_API_KEY="
    $apiKey = ($envFile -split "=")[1].Trim()
    
    # Prueba de autenticación real
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/api/sensor-data" `
                    -Method Post -Headers @{"X-API-KEY"="$apiKey"} `
                    -ContentType "application/json" -Body '{"test":1}' `
                    -ErrorAction Stop
        Write-Host " OK (Autenticación exitosa)" -ForegroundColor Green
    } catch {
        if ($_.Exception.Response.StatusCode -eq "Unauthorized") {
            Write-Host " ERROR (Clave .env no coincide con el Servidor)" -ForegroundColor Red
        } else {
            Write-Host " ERROR (Servidor no respondió correctamente)" -ForegroundColor Red
        }
    }
} else {
    Write-Host " ERROR (No se encontró archivo .env)" -ForegroundColor Red
}

Write-Host "`n===============================================" -ForegroundColor Cyan
Write-Host "              FIN DEL DIAGNÓSTICO" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan