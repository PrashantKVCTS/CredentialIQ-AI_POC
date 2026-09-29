# CredentialIQ AI Smoke Test Script for Windows PowerShell
$ErrorActionPreference = "Stop"

$port = $env:PORT
if ([string]::IsNullOrWhiteSpace($port)) { $port = "5050" }
$baseUrl = "http://localhost:$port"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "    CredentialIQ AI API Smoke Tests       " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

Write-Host "[1/5] Testing GET /health..." -ForegroundColor Yellow
$health = Invoke-RestMethod -Uri "$baseUrl/health" -Method Get
Write-Host "Health Status: $($health.status)" -ForegroundColor Green

Write-Host "`n[2/5] Testing GET /api/system/info..." -ForegroundColor Yellow
$info = Invoke-RestMethod -Uri "$baseUrl/api/system/info" -Method Get
Write-Host "System App: $($info.applicationName) | Provider: $($info.llmProvider)" -ForegroundColor Green

Write-Host "`n[3/5] Testing POST /api/credentialingcases (Clean)..." -ForegroundColor Yellow
$cleanBody = Get-Content -Raw -Path "samples/clean-provider.json"
$cleanRes = Invoke-RestMethod -Uri "$baseUrl/api/credentialingcases" -Method Post -ContentType "application/json" -Body $cleanBody
Write-Host "Clean Result Status: $($cleanRes.status) | Risk: $($cleanRes.riskClassification)" -ForegroundColor Green

Write-Host "`n[4/5] Testing POST /api/credentialingcases (Exception)..." -ForegroundColor Yellow
$excBody = Get-Content -Raw -Path "samples/exception-provider.json"
$excRes = Invoke-RestMethod -Uri "$baseUrl/api/credentialingcases" -Method Post -ContentType "application/json" -Body $excBody
Write-Host "Exception Result Status: $($excRes.status) | Risk: $($excRes.riskClassification)" -ForegroundColor Green

Write-Host "`n[5/5] Testing POST /api/credentialingcases (Hold)..." -ForegroundColor Yellow
$holdBody = Get-Content -Raw -Path "samples/hold-provider.json"
$holdRes = Invoke-RestMethod -Uri "$baseUrl/api/credentialingcases" -Method Post -ContentType "application/json" -Body $holdBody
Write-Host "Hold Result Status: $($holdRes.status) | Risk: $($holdRes.riskClassification)" -ForegroundColor Green

Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "   All Smoke Tests Passed Successfully!   " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
