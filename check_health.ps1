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

# [ ... Partes 1, 2 y 3 se mantienen igual ... ]

# 4. Validar API KEY y Sincronización
Write-Host "[4] Validando API KEY y envío de datos..." -NoNewline
if (Test-Path ".env") {
    # Extraer la API KEY del .env
    $envContent = Get-Content ".env" | ConvertFrom-StringData
    $apiKey = $envContent.SENSOR_API_KEY

    # Payload de prueba compatible con tu nuevo routes.py
    $testBody = @{
        sensor_id = "TEST_NODE"
        t_int = 25.5
        light = 500
    } | ConvertTo-Json

    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/api/sensor-data" `
                    -Method Post -Headers @{"X-API-KEY"="$apiKey"} `
                    -ContentType "application/json" -Body $testBody `
                    -ErrorAction Stop
        
        Write-Host " OK (Dato guardado y en cola de sincronización)" -ForegroundColor Green
    } catch {
        Write-Host " ERROR ($($_.Exception.Message))" -ForegroundColor Red
    }
} else {
    Write-Host " ERROR (No se encontró archivo .env)" -ForegroundColor Red
}