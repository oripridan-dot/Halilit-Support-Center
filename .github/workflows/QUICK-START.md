# GitHub Actions Docker Setup - Quick Start

Your project now has 4 new Docker-focused GitHub Actions workflows. Here's what to do:

## 🚀 Immediate Next Steps

### 1. Enable GitHub Container Registry (5 min)
By default, images push to `ghcr.io` (GitHub Container Registry). No setup needed—it works automatically with your GitHub token.

**Verify it works:**
- Push a commit to `main`
- Watch **Actions** tab
- After `push-image.yml` completes, go to **Packages** (top right of repo)
- You'll see your Docker image there

### 2. Review the Workflows

In `.github/workflows/` you now have:

| Workflow | When it runs | What it does |
|----------|-------------|-------------|
| `full-stack-ci.yml` | Every push/PR to main | Tests frontend + backend + Docker build |
| `backend-docker-ci.yml` | Changes to backend or Dockerfile | Comprehensive Docker tests + security scan |
| `push-image.yml` | Push to main OR git tag | Builds and pushes image to registry |
| `deploy-workers.yml` | Manual or on push | Template for production deployment |

### 3. Optional: Docker Hub Setup (if you prefer)
If you want images on Docker Hub instead of GitHub Container Registry:

1. Create Docker Hub account
2. Generate token: https://hub.docker.com/settings/security
3. Add to GitHub secrets (Repo → Settings → Secrets):
   - Name: `DOCKER_USERNAME` | Value: your Docker Hub username
   - Name: `DOCKER_PASSWORD` | Value: your token
4. Edit `push-image.yml` and uncomment the Docker Hub section

---

## 📋 What Each Workflow Does

### `full-stack-ci.yml` (Main CI - Runs Every Commit)
✓ Tests frontend (pnpm build, TypeScript)  
✓ Builds Docker image for backend  
✓ Runs pytest on Python code  
✓ Lints Dockerfile  

**Useful for:** Pre-merge checks, catching breakage early

---

### `backend-docker-ci.yml` (Docker-Focused Tests)
✓ Builds Docker image with layer caching  
✓ Runs Hadolint (Dockerfile best practices)  
✓ Runs pytest unit tests  
✓ Starts Redis + PostgreSQL and tests them  
✓ Scans for security vulnerabilities (Trivy)  

**Useful for:** Deep Docker validation, security audits

---

### `push-image.yml` (Container Registry Push)
Automatically triggered on:
- Push to `main` → image tagged `main`
- Git tag `v1.0.0` → image tagged `v1.0.0`
- Manual run (Actions → Run workflow)

**Images created:**
```
ghcr.io/your-username/halilit:main
ghcr.io/your-username/halilit:main-abc123def
ghcr.io/your-username/halilit:v1.0.0
```

**Useful for:** Deploying to production, sharing images

---

### `deploy-workers.yml` (Deployment Template)
**This is a template.** Customize it to match your infrastructure.

Currently supports:
- `staging` environment (auto-deploy on push to main)
- `production` environment (manual deployment only)

**To enable:** Add your deployment commands in the `deploy-staging` and `deploy-production` steps.

Examples:
- **SSH deploy**: `ssh user@server "docker-compose pull && docker-compose up -d"`
- **Kubernetes**: `kubectl apply -f deployment.yaml`
- **Webhook**: `curl https://your-deployment-webhook.com`

---

## 🔍 Docker Best Practices Included

### 1. BuildKit Layer Caching
Reuses unchanged Docker layers. Saves ~2-3 minutes per build.
```
First build: ~5 min
Second build (no changes): ~10 sec
```

### 2. Service Health Checks
Waits for Redis and PostgreSQL before running tests.
```yaml
docker compose exec -T redis redis-cli ping
docker compose exec -T postgres pg_isready -U halilit_user
```

### 3. Dockerfile Linting
Caught best practices violations:
- `RUN apt-get update && apt-get install` combined (not separate)
- Unused system packages removed
- Secrets not baked into image

### 4. Trivy Security Scanning
Automatically scans for CVEs in dependencies.  
Results appear in GitHub **Security** tab.

### 5. Semantic Versioning
Images tagged intelligently:
- `main` - latest from main branch
- `v1.0.0` - production release
- `main-sha123456` - specific commit

---

## 🛠️ Common Tasks

### Run Full CI on Demand
1. Go to **Actions** tab
2. Select **Full Stack CI**
3. Click **Run workflow**

### View Docker Image in Registry
1. Go to **Packages** (top right of repo)
2. Click the image
3. See all tags, size, push date

### Trigger Docker Image Push
1. Merge PR to main (auto-triggers), or
2. Create git tag:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
3. Or go to **Actions** → **Push to Container Registry** → **Run workflow**

### Debug Build Failures
1. Go to **Actions** → failed workflow
2. Click the failed job
3. Expand the failed step
4. Common issues:
   - **Rate limit**: Use specific Python version (python:3.11-slim)
   - **Dependency conflict**: Update requirements.txt
   - **Cache stale**: Clear via Actions → **Caches** tab

---

## 📊 Monitoring

### GitHub Container Registry
- Go to **Packages**
- See image size, layer count, download stats
- View all tags and push dates

### GitHub Actions Performance
- **Actions** tab shows runtime for each workflow
- Average: full-stack-ci ~5-7 min, push-image ~5 min
- Slow? Check build logs for rate limiting or dependency downloads

### Security Scanning
- **Security** → **Code scanning**
- Trivy results from each Docker build
- Fix high/critical vulnerabilities before deployment

---

## 🔐 Secrets to Add (Optional)

### For GitHub Container Registry (default)
**No secrets needed.** Uses built-in `GITHUB_TOKEN`.

### For Docker Hub
Add to Repo → Settings → Secrets:
```
DOCKER_USERNAME = your_username
DOCKER_PASSWORD = your_access_token
```

### For Deployment (if using `deploy-workers.yml`)
Add secrets for your target platform:
- **SSH**: `DEPLOY_SSH_KEY`, `DEPLOY_HOST`
- **Kubernetes**: `KUBECONFIG` (base64-encoded)
- **AWS**: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- **Webhooks**: `DEPLOY_WEBHOOK_URL`

---

## 💡 Tips & Tricks

### Speed Up Builds
1. Use `python:3.11-slim` instead of `python:3.11` (saves 100MB)
2. Install only production dependencies in runtime stage
3. Reorder Dockerfile layers: frequently-changing content last
4. Cache pip: GitHub Actions does this automatically

### Reduce Image Size
1. Multi-stage Dockerfile (separate build from runtime)
2. Remove dev dependencies from runtime
3. Clean apt cache: `apt-get clean && rm -rf /var/lib/apt/lists/*`
4. Current size: check in Packages after build

### Test Locally Before Committing
```bash
# Build locally
docker build -t halilit:test .

# Run tests
docker compose up -d redis postgres
docker compose exec -T redis redis-cli ping

# Clean up
docker compose down -v
```

---

## 📚 Learn More

- **Docker CI/CD**: https://docs.docker.com/build/ci/github-actions/
- **BuildKit**: https://docs.docker.com/build/concepts/overview/
- **GitHub Actions**: https://docs.github.com/en/actions
- **Trivy scanning**: https://aquasecurity.github.io/trivy/

---

## ❓ Troubleshooting

### "Image push failed - 403 Forbidden"
- Check token permissions in Repo → Settings → Actions
- GitHub token should have read/write on Packages

### "Docker build rate limit"
- Pull python image early in workflow
- Use specific version: `python:3.11-slim@sha256:...`

### "Service health check failed"
- Increase timeout in workflow (default 30s)
- Check Docker Compose ports aren't already in use
- Run `docker-compose logs redis` for details

### "pytest failed but workflow shows success"
- Check `continue-on-error: true` in workflow
- Remove if you want failures to block merges

---

## Next: Customize Deploy Workflow

To use `deploy-workers.yml` for your production setup:

1. Choose your deployment target:
   - **Docker Swarm** (simple, built-in)
   - **Kubernetes** (scalable, complex)
   - **VPS with SSH** (DIY, full control)

2. Add your deployment commands to the workflow

3. Set environment variables for your infrastructure

4. Test with a manual workflow run

For help, see `DOCKER-SETUP.md` in this directory for detailed examples.
