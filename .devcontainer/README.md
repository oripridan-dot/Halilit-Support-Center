# Codespace & Dev Container Setup

This directory contains the configuration for GitHub Codespaces and VS Code Dev Containers.

## What happens when you start the codespace

1. **Container Creation** - A Docker container is created with:
   - Node.js 20 (TypeScript/React development)
   - Python 3.11 (Backend development)
   - Docker-in-Docker (for running docker-compose services)

2. **Post-Create Setup** (`setup.sh`) - Automatically runs:
   - Installs `pnpm` globally
   - Installs Python dependencies from `backend/requirements.txt`
   - Installs frontend dependencies with `pnpm install`
   - Creates `.env` file from `.env.example` template

3. **Port Forwarding** - The following ports are automatically forwarded:
   - `5173` - Frontend (Vite dev server)
   - `8000` - Backend (FastAPI server)
   - `6379` - Redis (Celery broker)
   - `5555` - Flower (Celery monitoring UI)
   - `5432` - PostgreSQL (task persistence)

## After the codespace starts

1. **Configure Environment Variables**
   ```bash
   # Edit .env file and add your Google API key
   nano .env
   ```
   Get your API key from: https://aistudio.google.com/app/apikey

2. **Start Docker Services** (optional but recommended for full functionality)
   ```bash
   docker-compose up -d
   ```

3. **Start the Application**
   ```bash
   # Option 1: Start both backend & frontend together
   npm run dev
   
   # Option 2: Start services separately
   # Terminal 1 - Backend
   npm run dev:backend
   
   # Terminal 2 - Frontend
   npm run dev:frontend
   ```

4. **Access the Application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Flower Monitor: http://localhost:5555

## Troubleshooting

### Codespace won't start
- Check the "Creation Log" in GitHub Codespaces for error messages
- Common issues:
  - Insufficient resources: Try a larger machine type
  - Network timeout during dependency installation: Restart the codespace

### Dependencies not installed
If setup didn't complete, run manually:
```bash
bash .devcontainer/setup.sh
```

### Docker services not working
Make sure Docker-in-Docker is running:
```bash
docker ps
docker-compose up -d
```

### Python imports not working
Check PYTHONPATH is set:
```bash
echo $PYTHONPATH  # Should show workspace folder
export PYTHONPATH=$(pwd)
```

## VS Code Extensions

The following extensions are automatically installed:
- **Python** - Python language support
- **Pylance** - Python IntelliSense
- **ESLint** - JavaScript/TypeScript linting
- **Prettier** - Code formatting
- **Tailwind CSS IntelliSense** - Tailwind class completion
- **Ruff** - Fast Python linter

## Configuration Details

- **Version**: v9.7
- **Node Memory**: 2GB max old space size
- **TypeScript Server Memory**: 2GB
- **Python Interpreter**: `/usr/local/bin/python`
- **Format on Save**: Enabled (Prettier)

## Related Files

- `devcontainer.json` - Main configuration file
- `setup.sh` - Post-create setup script
- `../.env.example` - Environment variable template
- `../docker-compose.yml` - Docker services configuration
