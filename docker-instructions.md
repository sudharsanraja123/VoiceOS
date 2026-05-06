# VoiceOS Docker Setup Instructions

## Quick Start

### 1. Build and Run with Docker Compose (Recommended)

```bash
# Clone and navigate to project
cd VoiceOS

# Build and start all services
docker-compose up --build

# Run in detached mode
docker-compose up -d --build

# Stop services
docker-compose down
```

### 2. Build and Run with Docker Only

```bash
# Build the image
docker build -t voiceos .

# Run the container
docker run -it --rm \
  -v $(pwd)/workspace:/app/workspace \
  -v $(pwd)/memory:/app/memory \
  -v $(pwd)/logs:/app/logs \
  voiceos
```

## Configuration

### Environment Variables

- `VOICEOS_ENV`: Set to `development`, `production`, or `testing`
- `PYTHONPATH`: Set to `/app`
- `DISPLAY`: Set to `:99` for virtual display

### Volume Mounts

- `./workspace`: Agent workspace files
- `./memory`: Agent memory and persistence
- `./logs`: System logs
- `./models`: AI model files
- `./config`: Configuration files

### Port Mappings

- `8000`: Potential web interface
- `3000`: Web interface (if frontend enabled)

## Services

### VoiceOS Main Service
- Multi-agent operating system
- Voice + CLI interface
- Safe system control
- Dynamic agent creation

### Optional Services

#### Database (PostgreSQL)
- Persistent storage for agent data
- Configuration and user data
- Metrics and logs

#### Cache (Redis)
- Fast caching for LLM responses
- Session management
- Performance optimization

#### Web Interface
- React-based frontend
- Real-time dashboard
- Agent management UI

## Usage Examples

### Voice Interaction
```bash
# Start voice mode
docker-compose exec voiceos python main.py

# Voice commands:
"open chrome"
"research machine learning"
"write python function"
"analyze sales data.csv"
```

### CLI Interaction
```bash
# Interactive CLI
docker-compose exec voiceos python main.py

# CLI commands:
help          - Show available commands
status        - Show system status
voice         - Switch to voice mode
cli           - Switch to CLI mode
hybrid        - Switch to hybrid mode
```

### System Control
```bash
# Safe system operations (with permission)
"open notepad"
"type hello world"
"switch window"
"close chrome"
```

## Development

### Building for Development
```bash
# Development build
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

### Debugging
```bash
# View logs
docker-compose logs voiceos

# Interactive shell
docker-compose exec voiceos bash

# Monitor resources
docker stats voiceos
```

### Testing
```bash
# Run tests
docker-compose exec voiceos python -m pytest tests/

# Performance benchmarks
docker-compose exec voiceos python tests/test_framework.py
```

## Security

### Container Security
- Runs as non-root user (`voiceos`)
- Limited system capabilities
- Resource limits enforced
- No new privileges

### System Access
- All operations require permission
- File access restricted to workspace
- Network access controlled
- Audio device access only

### Data Protection
- Local models only (no external APIs)
- Data stays within container
- Encrypted storage options
- Audit logging enabled

## Troubleshooting

### Common Issues

#### Audio Not Working
```bash
# Check audio devices
docker-compose exec voiceos ls -la /dev/snd

# Install audio dependencies
docker-compose exec voiceos apt-get update && apt-get install -y alsa-utils
```

#### GUI Applications Not Working
```bash
# Check X11 display
docker-compose exec voiceos echo $DISPLAY

# Install GUI dependencies
docker-compose exec voiceos apt-get install -y xvfb x11-utils
```

#### Permission Issues
```bash
# Check user permissions
docker-compose exec voiceos id

# Fix file permissions
sudo chown -R $USER:$USER workspace memory logs
```

#### Memory Issues
```bash
# Check memory usage
docker stats voiceos

# Increase memory limit
# Edit docker-compose.yml and update memory: 4G to memory: 8G
```

### Logs and Debugging

#### View System Logs
```bash
# Real-time logs
docker-compose logs -f voiceos

# Application logs
docker-compose exec voiceos tail -f logs/voiceos.log

# Error logs
docker-compose exec voiceos grep ERROR logs/voiceos.log
```

#### Health Checks
```bash
# Check container health
docker-compose ps

# Manual health check
docker-compose exec voiceos python -c "import core.orchestrator; print('OK')"
```

## Performance Optimization

### Resource Allocation
```yaml
# In docker-compose.yml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 4G
    reservations:
      cpus: '0.5'
      memory: 1G
```

### Volume Optimization
```yaml
# Use local volumes for better performance
volumes:
  voiceos_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /path/to/fast/storage
```

### Network Optimization
```yaml
# Use dedicated network
networks:
  voiceos-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

## Production Deployment

### Security Hardening
```yaml
# Production security settings
security_opt:
  - no-new-privileges:true
  - apparmor:voiceos-profile
  - seccomp:default
```

### Monitoring
```yaml
# Add monitoring
labels:
  - "monitoring.prometheus.scrape=true"
  - "monitoring.prometheus.port=8000"
```

### Backup Strategy
```bash
# Backup volumes
docker run --rm -v voiceos_data:/data -v $(pwd)/backup:/backup \
  alpine tar czf /backup/voiceos-backup-$(date +%Y%m%d).tar.gz -C /data .

# Restore from backup
docker run --rm -v voiceos_data:/data -v $(pwd)/backup:/backup \
  alpine tar xzf /backup/voiceos-backup-20231201.tar.gz -C /data
```

## Advanced Configuration

### Custom Models
```bash
# Copy models to container
docker cp ./models/mistral-7b.ggml voiceos:/app/models/

# Set model path
echo "MODEL_PATH=/app/models/mistral-7b.ggml" >> .env
```

### Custom Tools
```bash
# Add custom tools
docker cp ./custom_tools voiceos:/app/tools/

# Rebuild with new tools
docker-compose build voiceos
```

### Environment-Specific Configs
```bash
# Development environment
VOICEOS_ENV=development docker-compose up

# Production environment
VOICEOS_ENV=production docker-compose -f docker-compose.prod.yml up
```

## Support

### Getting Help
- Check logs: `docker-compose logs voiceos`
- Health check: `docker-compose exec voiceos python main.py --status`
- Documentation: Check README.md and inline help

### Reporting Issues
Include:
- Docker version: `docker --version`
- System info: `docker-compose exec voiceos uname -a`
- Logs: `docker-compose logs --tail=50 voiceos`
- Configuration: `docker-compose config`

### Community
- GitHub Issues: Report bugs and request features
- Discussions: Share configurations and use cases
- Wiki: Advanced setup and troubleshooting
