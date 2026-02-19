# GitHub Actions Workflows - Docker Setup

This directory contains GitHub Actions workflows optimized for your Halilit Support Center project (FastAPI + Celery + Docker Compose).

## Workflows Overview

### 1. `full-stack-ci.yml` (Main CI - Recommended)
Runs on every push to `main` and pull requests. Tests both frontend and backend.

**What it does:**
- Builds and tests the Next.js frontend (pnpm + TypeScript + build check)
- Builds the Docker image for backend services
- Runs pytest on backend Python code
- Lints the Dockerfile with Hadolint

**Triggers:** Push to main, pull requests to main

**Duration:** ~5-7 minutes

---

### 2. `backend-docker-ci.yml` (Dedicated Docker Tests)
Comprehensive Docker-focused tests for backend services.

**What it does:**
- Builds Docker image with BuildKit layer caching
- Runs Hadolint (Dockerfile best practices)
- Runs pytest unit tests
- Starts Docker Compose services (Redis, PostgreSQL) for integration tests
- Scans for security vulnerabilities with Trivy

**Triggers:** Changes to `backend/`, `Dockerfile`, or `docker-compose.yml`

**Duration:** ~10-12 minutes

**Key features:**
- **Layer caching**: Reuses Docker build layers across runs (faster rebuilds)
- **Service health checks**: Waits for Redis and PostgreSQL to be ready
- **Security scanning**: Identifies vulnerabilities in dependencies
- **Artifact upload**: Stores test results for review

---

### 3. `push-image.yml` (Container Registry Push)
Builds and pushes your Docker image to GitHub Container Registry (or Docker Hub).

**What it does:**
- Builds the Docker image
- Authenticates to container registry
- Pushes image with semantic versioning tags
- Uses GitHub Actions cache for faster builds

**Triggers:** Push to main, git tags (e.g., `v1.0.0`), manual workflow dispatch

**Example tags created:**
- `ghcr.io/your-repo/halilit:main` (latest from main)
- `ghcr.io/your-repo/halilit:v1.0.0` (from git tag)
- `ghcr.io/your-repo/halilit:main-abc123def` (commit hash)

**Setup required:**
- No setup needed for GitHub Container Registry (uses `GITHUB_TOKEN`)
- For Docker Hub: Add `DOCKER_USERNAME` and `DOCKER_PASSWORD` secrets to repo

**Duration:** ~5 minutes

---

## Docker Best Practices Included

### 1. **BuildKit Layer Caching**
```yaml
cache-from: type=local,src=/tmp/.buildx-cache
cache-to: type=local,dest=/tmp/.buildx-cache-new,mode=max
```
- Reuses unchanged layers between builds
- Dramatically speeds up repeated builds
- Essential for Docker multi-stage builds (Go, Node, Python)

### 2. **Docker Compose Service Health Checks**
```bash
docker compose exec -T redis redis-cli ping
docker compose exec -T postgres pg_isready -U halilit_user
```
- Verifies Redis and PostgreSQL are ready before running tests
- Prevents flaky test failures from service startup races

### 3. **Dockerfile Linting (Hadolint)**
- Catches Docker best practices violations
- Warns about deprecated instructions
- Enforces security hardening

### 4. **Security Scanning (Trivy)**
- Scans filesystem and dependencies for CVEs
- Uploads results to GitHub Security tab
- Helps track and fix vulnerabilities

### 5. **Image Tagging Strategy**
- Branch-based tags: `main`, `v8.6`
- Semantic versioning: `v1.0.0`, `v1.0`
- Commit-based: `main-abc123def` (for debugging)

---

## Container Registry Options

### GitHub Container Registry (Default)
**Pros:**
- Free for public repos
- Integrated with GitHub Actions (uses `GITHUB_TOKEN`)
- No additional setup needed
- Images stored at `ghcr.io/username/repo`

**Cons:**
- Separate from GitHub Packages
- Quota limits on large organizations

### Docker Hub (Alternative)
**Setup:**
1. Create Docker Hub account
2. Generate access token: https://hub.docker.com/settings/security
3. Add secrets to GitHub repo:
   - `DOCKER_USERNAME` = your Docker Hub username
   - `DOCKER_PASSWORD` = your access token

**Uncomment in `push-image.yml`:**
```yaml
# - name: Log in to Docker Hub
#   uses: docker/login-action@v3
#   with:
#     username: ${{ secrets.DOCKER_USERNAME }}
#     password: ${{ secrets.DOCKER_PASSWORD }}
```

Then update image name:
```yaml
REGISTRY: docker.io
IMAGE_NAME: yourname/halilit
```

---

## Secrets & Configuration

### Required Secrets (for `push-image.yml`)
If using Docker Hub:
- `DOCKER_USERNAME` - Your Docker Hub username
- `DOCKER_PASSWORD` - Docker Hub access token

If using GitHub Container Registry:
- No secrets needed (uses `GITHUB_TOKEN`)

### Environment Variables
Set via `.env` or `docker-compose.yml`:
- `CELERY_BROKER_URL` - Redis connection
- `CELERY_RESULT_BACKEND` - Results database
- `POSTGRES_PASSWORD` - Database password
- `GEMINI_API_KEY` - For AI agent services

---

## Common Tasks

### Run Full Stack CI on Demand
1. Go to **Actions** tab
2. Select **Full Stack CI**
3. Click **Run workflow**

### Push Image to Registry
1. Merge PR to `main`, or
2. Create git tag: `git tag v1.0.0 && git push --tags`, or
3. Go to **Actions** → **Push to Container Registry** → **Run workflow**

### Debug Build Failures
1. Check the failed workflow run in **Actions** tab
2. Expand the failed step
3. Look for error messages in logs
4. Common issues:
   - **Image pull rate limit**: Push `docker pull` earlier in workflow
   - **Dependency version conflicts**: Update `requirements.txt`
   - **Cache issues**: Clear cache in Actions → **Caches** tab

### Monitor Docker Image Size
After `push-image.yml` completes:
1. Go to **Packages** (top right of repo)
2. Click the image
3. See size, tags, and layer breakdown

---

## Performance Tuning

### Reduce Build Time
1. **Use specific Python version**: `python:3.11-slim` (smaller than `python:3.11`)
2. **Multi-stage Dockerfile**: Separate build stage from runtime
3. **Organize RUN commands**: Group similar commands to reuse layers

### Reduce Test Time
1. **Cache dependencies**: `actions/cache@v4` for pip packages
2. **Run tests in parallel**: Add `-n auto` to pytest
3. **Skip integration tests on PR**: Use `if: github.event_name == 'push'`

---

## Troubleshooting

### "Docker image build failed"
- Check Dockerfile syntax with `docker build .` locally
- Verify all `COPY` paths exist
- Check Docker Hub image availability (rate limiting?)

### "Service health check failed"
- Ensure Docker Compose ports don't conflict
- Check Docker logs: `docker compose logs redis`
- Increase timeout in workflow if services start slowly

### "Image push failed"
- Verify credentials in secrets
- Check image name format (lowercase, no special chars)
- Ensure registry has space available

---

## Next Steps

1. **Review workflows** in the **Actions** tab after first push
2. **Set up container registry**: Choose ghcr.io (default) or Docker Hub
3. **Enable branch protection**: Require CI to pass before merging
4. **Monitor security**: Check **Security** → **Dependabot** for alerts

---

For more info on Docker CI/CD best practices, see:
- https://docs.docker.com/build/ci/github-actions/
- https://docs.docker.com/build/concepts/overview/ (BuildKit)
- https://github.com/docker/build-push-action
