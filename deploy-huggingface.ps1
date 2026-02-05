# Deploy to Hugging Face Space
# This script helps you push your code to Hugging Face Spaces

Write-Host "🤗 Hugging Face Space Deployment" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Check if huggingface remote exists
$remotes = git remote
if ($remotes -notcontains "huggingface") {
    Write-Host "Adding Hugging Face remote..." -ForegroundColor Yellow
    git remote add huggingface https://huggingface.co/spaces/dubey-codes/ai-support-service
}

Write-Host "Space URL: https://huggingface.co/spaces/dubey-codes/ai-support-service" -ForegroundColor Green
Write-Host ""

# Check for authentication
Write-Host "Authentication Required" -ForegroundColor Yellow
Write-Host "----------------------" -ForegroundColor Yellow
Write-Host ""
Write-Host "You need a Hugging Face access token to push code." -ForegroundColor White
Write-Host ""
Write-Host "Get your token:" -ForegroundColor Cyan
Write-Host "  1. Go to: https://huggingface.co/settings/tokens" -ForegroundColor White
Write-Host "  2. Click 'New token'" -ForegroundColor White
Write-Host "  3. Name: 'ai-support-service'" -ForegroundColor White
Write-Host "  4. Type: 'Write'" -ForegroundColor White
Write-Host "  5. Copy the token" -ForegroundColor White
Write-Host ""

$response = Read-Host "Do you have your Hugging Face token ready? (y/n)"

if ($response -ne "y") {
    Write-Host ""
    Write-Host "Please get your token and run this script again." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Alternative: Use Hugging Face CLI" -ForegroundColor Cyan
    Write-Host "  pip install huggingface_hub" -ForegroundColor White
    Write-Host "  huggingface-cli login" -ForegroundColor White
    Write-Host "  git push huggingface main" -ForegroundColor White
    exit
}

Write-Host ""
Write-Host "Pushing to Hugging Face Space..." -ForegroundColor Yellow
Write-Host ""
Write-Host "When prompted:" -ForegroundColor Cyan
Write-Host "  Username: dubey-codes (or your HF username)" -ForegroundColor White
Write-Host "  Password: [paste your HF token]" -ForegroundColor White
Write-Host ""

try {
    git push huggingface main --force
    Write-Host ""
    Write-Host "✅ Successfully pushed to Hugging Face!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your Space is deploying..." -ForegroundColor Yellow
    Write-Host "View it at: https://huggingface.co/spaces/dubey-codes/ai-support-service" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "⚠️  IMPORTANT: Add your GROQ_API_KEY" -ForegroundColor Yellow
    Write-Host "1. Go to Space Settings: https://huggingface.co/spaces/dubey-codes/ai-support-service/settings" -ForegroundColor White
    Write-Host "2. Scroll to 'Repository secrets'" -ForegroundColor White
    Write-Host "3. Add secret: GROQ_API_KEY = your_groq_api_key" -ForegroundColor White
    Write-Host "4. Save and rebuild" -ForegroundColor White
    Write-Host ""
} catch {
    Write-Host ""
    Write-Host "❌ Push failed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "  - Invalid token" -ForegroundColor White
    Write-Host "  - Token doesn't have write access" -ForegroundColor White
    Write-Host "  - Space doesn't exist" -ForegroundColor White
    Write-Host ""
    Write-Host "Try using the Hugging Face CLI instead:" -ForegroundColor Cyan
    Write-Host "  pip install huggingface_hub" -ForegroundColor White
    Write-Host "  huggingface-cli login" -ForegroundColor White
    Write-Host "  git push huggingface main" -ForegroundColor White
}
