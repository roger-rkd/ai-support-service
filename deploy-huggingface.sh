#!/bin/bash
# Deploy to Hugging Face Space

echo "🤗 Hugging Face Space Deployment"
echo "================================="
echo ""

# Check if huggingface remote exists
if ! git remote | grep -q "huggingface"; then
    echo "Adding Hugging Face remote..."
    git remote add huggingface https://huggingface.co/spaces/dubey-codes/ai-support-service
fi

echo "Space URL: https://huggingface.co/spaces/dubey-codes/ai-support-service"
echo ""

# Check for authentication
echo "Authentication Required"
echo "----------------------"
echo ""
echo "You need a Hugging Face access token to push code."
echo ""
echo "Get your token:"
echo "  1. Go to: https://huggingface.co/settings/tokens"
echo "  2. Click 'New token'"
echo "  3. Name: 'ai-support-service'"
echo "  4. Type: 'Write'"
echo "  5. Copy the token"
echo ""

read -p "Do you have your Hugging Face token ready? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Please get your token and run this script again."
    echo ""
    echo "Alternative: Use Hugging Face CLI"
    echo "  pip install huggingface_hub"
    echo "  huggingface-cli login"
    echo "  git push huggingface main"
    exit 0
fi

echo ""
echo "Pushing to Hugging Face Space..."
echo ""
echo "When prompted:"
echo "  Username: dubey-codes (or your HF username)"
echo "  Password: [paste your HF token]"
echo ""

if git push huggingface main --force; then
    echo ""
    echo "✅ Successfully pushed to Hugging Face!"
    echo ""
    echo "Your Space is deploying..."
    echo "View it at: https://huggingface.co/spaces/dubey-codes/ai-support-service"
    echo ""
    echo "⚠️  IMPORTANT: Add your GROQ_API_KEY"
    echo "1. Go to Space Settings: https://huggingface.co/spaces/dubey-codes/ai-support-service/settings"
    echo "2. Scroll to 'Repository secrets'"
    echo "3. Add secret: GROQ_API_KEY = your_groq_api_key"
    echo "4. Save and rebuild"
    echo ""
else
    echo ""
    echo "❌ Push failed!"
    echo ""
    echo "Common issues:"
    echo "  - Invalid token"
    echo "  - Token doesn't have write access"
    echo "  - Space doesn't exist"
    echo ""
    echo "Try using the Hugging Face CLI instead:"
    echo "  pip install huggingface_hub"
    echo "  huggingface-cli login"
    echo "  git push huggingface main"
fi
