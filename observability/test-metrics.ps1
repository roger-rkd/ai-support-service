# Test script to generate metrics for the AI Support Service

param(
    [string]$ServiceUrl = "http://localhost:8000",
    [int]$NumRequests = 10
)

Write-Host "Testing AI Support Service Metrics" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Green
Write-Host "Service URL: $ServiceUrl"
Write-Host "Number of requests: $NumRequests"
Write-Host ""

# Test health endpoint
Write-Host "1. Testing health endpoint..." -ForegroundColor Yellow
for ($i = 1; $i -le $NumRequests; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "$ServiceUrl/health" -Method GET -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "  ✓ Health check $i/$NumRequests - OK" -ForegroundColor Green
        }
    } catch {
        Write-Host "  ✗ Health check $i/$NumRequests - Failed" -ForegroundColor Red
    }
    Start-Sleep -Milliseconds 500
}

Write-Host ""
Write-Host "2. Testing /ask endpoint..." -ForegroundColor Yellow

# Sample questions
$questions = @(
    "How do I reset my password?",
    "How do I update my billing information?",
    "What are your support hours?",
    "How can I contact technical support?",
    "How do I delete my account?"
)

for ($i = 1; $i -le $NumRequests; $i++) {
    $questionIndex = ($i - 1) % $questions.Count
    $question = $questions[$questionIndex]

    Write-Host "  Request $i/$NumRequests: `"$question`""

    try {
        $body = @{
            question = $question
        } | ConvertTo-Json

        $response = Invoke-RestMethod -Uri "$ServiceUrl/ask" -Method POST `
            -ContentType "application/json" -Body $body

        $answer = $response.answer.Substring(0, [Math]::Min(80, $response.answer.Length))
        Write-Host "  ✓ Response: $answer..." -ForegroundColor Green
    } catch {
        Write-Host "  ✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
    }

    Start-Sleep -Seconds 2
}

Write-Host ""
Write-Host "3. Viewing metrics..." -ForegroundColor Yellow
Write-Host ""

try {
    $metrics = Invoke-WebRequest -Uri "$ServiceUrl/metrics" -Method GET -UseBasicParsing
    $lines = $metrics.Content -split "`n" | Where-Object {
        $_ -match "(ai_support_requests_total|ai_support_request_latency|ai_support_rag)"
    } | Select-Object -First 20

    foreach ($line in $lines) {
        Write-Host $line
    }
} catch {
    Write-Host "Failed to retrieve metrics" -ForegroundColor Red
}

Write-Host ""
Write-Host "===================================" -ForegroundColor Green
Write-Host "Test complete!" -ForegroundColor Green
Write-Host ""
Write-Host "View metrics:"
Write-Host "  Raw: $ServiceUrl/metrics"
Write-Host "  Prometheus: http://localhost:9090"
Write-Host "  Grafana: http://localhost:3000"
