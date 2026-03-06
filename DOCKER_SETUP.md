# Docker Installation Guide for SteelWorks Project

## Why Docker?

Docker provides isolated, reproducible test environments that ensure consistency across different machines. It's especially useful for:
- Running test databases without affecting your local PostgreSQL
- Ensuring CI/CD consistency
- Easy setup and teardown of test environments

## Installation Instructions

### Windows 10/11

#### Prerequisites
- Windows 10 64-bit: Pro, Enterprise, or Education (Build 19041 or higher)
- OR Windows 11 64-bit
- Hardware virtualization enabled in BIOS
- At least 4GB RAM

#### Steps

1. **Download Docker Desktop**
   - Visit: https://www.docker.com/products/docker-desktop/
   - Click "Download for Windows"
   - Download the installer (Docker Desktop Installer.exe)

2. **Install Docker Desktop**
   ```powershell
   # Run the installer
   # Accept the license agreement
   # Check "Use WSL 2 instead of Hyper-V" (recommended)
   # Complete installation
   ```

3. **Restart Your Computer**
   After installation, restart is required

4. **Verify Installation**
   ```powershell
   # Open PowerShell
   docker --version
   # Should output: Docker version 24.x.x or higher
   
   docker compose version
   # Should output: Docker Compose version 2.x.x or higher
   ```

5. **Test Docker**
   ```powershell
   docker run hello-world
   # Should download and run a test container
   ```

#### Troubleshooting Windows

**Issue: "WSL 2 installation is incomplete"**
```powershell
# Update WSL
wsl --update

# Set WSL 2 as default
wsl --set-default-version 2

# Install Ubuntu (optional, for Linux environment)
wsl --install -d Ubuntu
```

**Issue: "Docker Desktop failed to start"**
- Enable virtualization in BIOS:
  1. Restart computer
  2. Enter BIOS (usually F2, F10, or DEL key)
  3. Find "Virtualization Technology" or "Intel VT-x/AMD-V"
  4. Enable it
  5. Save and exit

### macOS

#### Prerequisites
- macOS 11 or newer
- Apple Silicon (M1/M2) or Intel processor
- At least 4GB RAM

#### Steps

1. **Download Docker Desktop**
   - Visit: https://www.docker.com/products/docker-desktop/
   - Choose your chip type:
     - Apple Silicon: Docker Desktop for Mac (Apple Silicon)
     - Intel: Docker Desktop for Mac (Intel)

2. **Install Docker Desktop**
   ```bash
   # Open the downloaded .dmg file
   # Drag Docker.app to Applications folder
   # Open Docker from Applications
   # Grant permissions when prompted
   ```

3. **Verify Installation**
   ```bash
   # Open Terminal
   docker --version
   # Should output: Docker version 24.x.x or higher
   
   docker compose version
   # Should output: Docker Compose version 2.x.x or higher
   ```

4. **Test Docker**
   ```bash
   docker run hello-world
   ```

#### Troubleshooting macOS

**Issue: "Docker.app cannot be opened"**
```bash
# Remove quarantine attribute
xattr -d com.apple.quarantine /Applications/Docker.app
```

**Issue: Docker commands require sudo**
```bash
# Add user to docker group
sudo usermod -aG docker $USER
# Log out and back in
```

### Linux (Ubuntu/Debian)

#### Steps

1. **Update Package Index**
   ```bash
   sudo apt-get update
   ```

2. **Install Prerequisites**
   ```bash
   sudo apt-get install \
       ca-certificates \
       curl \
       gnupg \
       lsb-release
   ```

3. **Add Docker's Official GPG Key**
   ```bash
   sudo mkdir -p /etc/apt/keyrings
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
       sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
   ```

4. **Set Up Repository**
   ```bash
   echo \
     "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
     https://download.docker.com/linux/ubuntu \
     $(lsb_release -cs) stable" | \
     sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
   ```

5. **Install Docker Engine**
   ```bash
   sudo apt-get update
   sudo apt-get install docker-ce docker-ce-cli containerd.io \
       docker-buildx-plugin docker-compose-plugin
   ```

6. **Start Docker Service**
   ```bash
   sudo systemctl start docker
   sudo systemctl enable docker
   ```

7. **Add User to Docker Group (Optional)**
   ```bash
   sudo usermod -aG docker $USER
   # Log out and back in for changes to take effect
   ```

8. **Verify Installation**
   ```bash
   docker --version
   docker compose version
   docker run hello-world
   ```

## Using Docker for SteelWorks Testing

### Quick Start: PostgreSQL Test Database

1. **Start PostgreSQL Container**
   ```bash
   docker run -d \
     --name steelworks-test-db \
     -e POSTGRES_USER=postgres \
     -e POSTGRES_PASSWORD=postgres \
     -e POSTGRES_DB=steelworks_test_db \
     -p 5433:5432 \
     postgres:15
   ```

2. **Update .env.test**
   ```bash
   DATABASE_URL=postgresql://postgres:postgres@localhost:5433/steelworks_test_db
   ```

3. **Run Tests**
   ```bash
   pytest tests/test_integration.py -v
   ```

4. **Stop Container**
   ```bash
   docker stop steelworks-test-db
   docker rm steelworks-test-db
   ```

### Using Docker Compose (Recommended)

1. **Create docker-compose.test.yml** (already in project)

2. **Start Services**
   ```bash
   docker-compose -f docker-compose.test.yml up -d
   ```

3. **Run Tests**
   ```bash
   pytest tests/ -v
   ```

4. **Stop Services**
   ```bash
   docker-compose -f docker-compose.test.yml down
   ```

### Useful Docker Commands

```bash
# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# View container logs
docker logs steelworks-test-db

# Execute commands in container
docker exec -it steelworks-test-db psql -U postgres

# Remove all stopped containers
docker container prune

# Remove all unused images
docker image prune -a

# View Docker disk usage
docker system df
```

## Advanced: Containerize the Streamlit App

### Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run Streamlit
CMD ["streamlit", "run", "src/steelworks/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Build and Run

```bash
# Build image
docker build -t steelworks-app .

# Run container
docker run -p 8501:8501 \
  -e DATABASE_URL="postgresql://..." \
  steelworks-app

# Access app at http://localhost:8501
```

## Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Desktop Manual](https://docs.docker.com/desktop/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Docker Hub](https://hub.docker.com/_/postgres)

## Support

If you encounter issues:
1. Check Docker Desktop is running
2. Review logs: `docker logs <container-name>`
3. Restart Docker Desktop
4. Check firewall settings
5. Visit [Docker Community Forums](https://forums.docker.com/)
