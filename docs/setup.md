# ⚙️ VoiceOS Setup Guide

## 📋 System Requirements

### Minimum Requirements
- **Python**: 3.10 or higher
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 10GB free space
- **OS**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 20.04+)

### Optional Dependencies
- **Docker**: For containerized deployment
- **GPU**: NVIDIA GPU with CUDA support for accelerated AI models
- **Microphone**: For voice input functionality

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/VoiceOS.git
cd VoiceOS
```

### 2. Create Virtual Environment

```bash
# Using venv (recommended)
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install core dependencies
pip install -r requirements.txt

# Install optional dependencies for enhanced features
pip install -r requirements-optional.txt
```

### 4. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit configuration
# Set your API keys and preferences in .env
```

---

## 🏃‍♂️ Running VoiceOS

### Local Development

```bash
# Run with default configuration
python main.py

# Run with specific configuration
python main.py --config dev

# Run with voice interface
python main.py --voice

# Run with web interface
python main.py --web
```

### Docker Deployment

```bash
# Build Docker image
docker build -t voiceos .

# Run container
docker run -it --rm \
  -v $(pwd)/workspace:/app/workspace \
  -v $(pwd)/models:/app/models \
  -p 8000:8000 \
  voiceos

# Run with GPU support
docker run -it --rm \
  --gpus all \
  -v $(pwd)/workspace:/app/workspace \
  -v $(pwd)/models:/app/models \
  -p 8000:8000 \
  voiceos
```

---

## 🤖 AI Models Setup

### Automatic Download
VoiceOS will automatically download required models on first run:

```bash
# Models will be downloaded to:
models/
├── whisper/
├── tts/
└── llm/
```

### Manual Model Placement
If you prefer to use custom models:

```bash
# Place your models in the appropriate directories
models/
├── whisper/
│   └── base.pt              # Whisper STT model
├── tts/
│   └── ljspeech/            # TTS model
└── llm/
    └── mistral-7b.gguf     # LLM model
```

### Supported Models
- **STT**: OpenAI Whisper (tiny, base, small, medium, large)
- **TTS**: Coqui TTS, Mozilla TTS
- **LLM**: Mistral, Llama2, CodeLlama (GGUF format)

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Core Configuration
VOICEOS_MODE=local                    # local, cloud, hybrid
VOICEOS_LOG_LEVEL=INFO               # DEBUG, INFO, WARNING, ERROR
VOICEOS_WORKSPACE=./workspace         # Workspace directory

# AI Model Configuration
WHISPER_MODEL=base                   # tiny, base, small, medium, large
TTS_MODEL=ljspeech                   # TTS model to use
LLM_MODEL=mistral-7b.gguf           # LLM model file

# API Configuration (optional)
OPENAI_API_KEY=your_openai_key      # For cloud LLM fallback
ANTHROPIC_API_KEY=your_key          # For Claude integration

# Voice Configuration
MICROPHONE_DEVICE=default            # Microphone device ID
VOICE_ACTIVATION=true                # Enable voice activation
TTS_VOICE_SPEED=1.0                  # TTS speech speed

# Security Configuration
PERMISSION_LEVEL=medium              # low, medium, high
ENABLE_LOGGING=true                  # Enable operation logging
SANDBOX_ENABLED=true                  # Enable code execution sandbox
```

### Configuration Files

```bash
# Main configuration
config/
├── default.yaml          # Default settings
├── development.yaml       # Development overrides
└── production.yaml        # Production settings

# Agent configurations
agents/
├── roles/
│   ├── researcher.yaml
│   ├── developer.yaml
│   └── analyst.yaml
└── core/
    ├── planner.yaml
    └── safety.yaml
```

---

## 🌐 Web Interface

### Accessing the Web UI

```bash
# Start with web interface
python main.py --web --port 8000

# Access in browser
open http://localhost:8000
```

### Web Interface Features
- **Dashboard**: System status and activity monitoring
- **Chat Interface**: Interactive chat with agents
- **File Manager**: Browse and manage workspace files
- **Agent Control**: Configure and control agent behavior
- **Logs Viewer**: View operation logs and debugging info

---

## 🔍 Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Ensure virtual environment is activated
which python

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### 2. Model Download Failures
```bash
# Check internet connection
curl -I https://huggingface.co

# Manual model download
python -c "from model_manager import ModelDownloader; ModelDownloader().download_all()"
```

#### 3. Permission Errors
```bash
# Check workspace permissions
ls -la workspace/

# Set appropriate permissions
chmod 755 workspace/
```

#### 4. Audio Issues
```bash
# List available microphones
python -c "import sounddevice; print(sounddevice.query_devices())"

# Test microphone
python -c "import audio.microphone; audio.microphone.test_microphone()"
```

### Debug Mode

```bash
# Run with debug logging
VOICEOS_LOG_LEVEL=DEBUG python main.py

# Run with verbose output
python main.py --verbose --debug
```

### Log Files

Check these files for troubleshooting:

```bash
# Main application log
logs/voiceos.log

# Agent operation logs
workspace/logs/agent_operations.log

# Tool execution logs
workspace/logs/tool_operations.log

# Error logs
logs/errors.log
```

---

## 📚 Next Steps

After successful installation:

1. **Read the Usage Guide**: `docs/usage.md`
2. **Explore Agent Capabilities**: `docs/agents.md`
3. **Check Architecture Overview**: `docs/architecture.md`
4. **Review Security Guidelines**: `docs/security.md`

---

## 🤝 Getting Help

- **Documentation**: Check the `docs/` directory
- **Issues**: Report bugs on GitHub Issues
- **Discussions**: Join GitHub Discussions for community support
- **Examples**: See `examples/` directory for usage examples

---

## 🔄 Updates

To update VoiceOS to the latest version:

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart VoiceOS
python main.py
```
