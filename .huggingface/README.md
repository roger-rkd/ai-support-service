# Deploying to Hugging Face Spaces

## Prerequisites

1. **Hugging Face Account**: Sign up at https://huggingface.co
2. **Access Token**: Create a token at https://huggingface.co/settings/tokens
   - Click "New token"
   - Name: `ai-support-service`
   - Type: Write access
   - Copy the token

## Setup Authentication

### Option 1: Using Git Credential Manager (Recommended)

```bash
# Push will prompt for credentials
git push huggingface main

# Username: Your Hugging Face username
# Password: Your Hugging Face access token (not your password!)
```

### Option 2: Using Token in URL

```bash
# Update remote with token
git remote remove huggingface
git remote add huggingface https://dubey-codes:<YOUR_TOKEN>@huggingface.co/spaces/dubey-codes/ai-support-service

# Push
git push huggingface main --force
```

### Option 3: Using Hugging Face CLI

```bash
# Install Hugging Face CLI
pip install huggingface_hub

# Login
huggingface-cli login

# Push
git push huggingface main
```

## Space Configuration

The Space is configured with:
- **SDK**: Docker
- **App Port**: 8000
- **Hardware**: CPU (can be upgraded to GPU if needed)

## Environment Variables

After deployment, add these secrets in your Space settings:

1. Go to https://huggingface.co/spaces/dubey-codes/ai-support-service/settings
2. Add secrets:
   - `GROQ_API_KEY`: Your Groq API key

## Files for Hugging Face Space

The following files are required:
- `README.md` (with YAML frontmatter)
- `Dockerfile` ✓
- `requirements.txt` ✓
- `app/` directory ✓

## Testing Your Space

After deployment:
1. Space URL: https://huggingface.co/spaces/dubey-codes/ai-support-service
2. API endpoint: https://dubey-codes-ai-support-service.hf.space/docs
3. Health check: https://dubey-codes-ai-support-service.hf.space/health

## Troubleshooting

### Build Fails
- Check logs in the Space's "App" tab
- Ensure all dependencies are in `requirements.txt`
- Verify Dockerfile builds locally first

### App Not Starting
- Check if `GROQ_API_KEY` is set in Space secrets
- Verify the port is 8000 in Dockerfile
- Check Space logs for errors

## Updating Your Space

```bash
# Make changes to your code
git add .
git commit -m "Update: description of changes"
git push huggingface main
```

The Space will automatically rebuild and redeploy.
