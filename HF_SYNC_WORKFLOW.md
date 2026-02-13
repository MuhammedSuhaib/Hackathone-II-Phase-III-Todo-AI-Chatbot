# Hugging Face Space Sync Workflow

This project includes a GitHub Actions workflow that automatically syncs the backend code to a Hugging Face Space when changes are pushed to the main branch.

## How it Works

The workflow (`sync-hf-space.yml`) is triggered when:
- Changes are pushed to the `main` or `master` branch
- Specifically when files in the `backend/**` directory are modified
- Or manually via the "workflow_dispatch" trigger

## Setup Requirements

To use this workflow, you need to configure the following:

### 1. Hugging Face Token

Add your Hugging Face token as a GitHub secret:
1. Go to your repository settings
2. Navigate to "Secrets and variables" → "Actions"
3. Add a new secret named `RAHEELTOKEN`
4. Use a Hugging Face access token with write permissions

To generate a Hugging Face token:
1. Go to your Hugging Face account settings
2. Navigate to "Access Tokens"
3. Create a new token with write permissions
4. Copy the token value

### 2. Hugging Face Space Repository

The workflow assumes your Hugging Face Space repository is located at:
```
https://huggingface.co/spaces/[username]/[space-name]
```

Update the repository URL in the workflow file if your Space has a different name or username.

## Configuration

The workflow file `.github/workflows/sync-hf-space.yml` contains the following configuration options:

- `branches`: Specifies which branches trigger the sync (defaults to `main` and `master`)
- `paths`: Specifies which file changes trigger the sync (defaults to `backend/**`)
- `RAHEELTOKEN`: The secret token for authenticating with Hugging Face

## Files Included in Sync

The workflow copies all files from the `backend/` directory to the Hugging Face Space, excluding:
- Python cache files (`*.pyc`, `__pycache__/`)
- Git directories (`.git/`)
- Virtual environments (`.venv/`, `venv/`)
- Node modules (`node_modules/`)
- Environment files (`.env`)
- Database files (`*.db`)

## Manual Trigger

You can manually trigger the workflow by:
1. Going to the "Actions" tab in your GitHub repository
2. Selecting "Sync Backend to Hugging Face Space"
3. Clicking "Run workflow"

## Troubleshooting

### Common Issues

1. **Permission Error**: Make sure your RAHEELTOKEN has write permissions to the Space repository
2. **Repository Not Found**: Verify the Hugging Face Space URL in the workflow file
3. **Workflow Not Triggering**: Check that the path filters match your file changes

### Logs

Check the workflow run logs in GitHub Actions for detailed error messages and execution information.