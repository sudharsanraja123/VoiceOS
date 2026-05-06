# 📖 VoiceOS Usage Guide

VoiceOS is a sophisticated voice + CLI driven multi-agent operating system with autonomous AI capabilities and native VoiceOS tools integration.

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/VoiceOS.git
cd VoiceOS

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Run VoiceOS
python main.py
```

### Docker Setup

```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d

# Run with GPU support
docker-compose --profile gpu up
```

### Web Interface

```bash
# Start with web interface
python main.py --web --port 8000

# Access at http://localhost:8000
```

## 🎤 Voice Interaction

### Basic Voice Commands

```bash
"Open Chrome"
"Search for latest AI research"
"Type hello world"
"Switch window"
"Take screenshot"
```

### Complex Voice Commands

```bash
"Research machine learning trends"
"Analyze this dataset"
"Write a Python script to scrape data"
"Automate this workflow"
```

### Autonomous Voice Commands

```bash
"Build a Python script to scrape product prices and analyze trends"
"Create a web scraper for news articles"
"Develop a complete solution for data analysis"
"Automate the daily sales report generation"
```

## 💻 CLI Interaction

### Basic CLI Commands

```bash
# Start VoiceOS
python main.py

# Check status
python main.py --status

# Run tests
python main.py --test

# Show help
python main.py --help
```

### CLI Modes

```bash
# Voice mode
python main.py --mode voice

# CLI mode
python main.py --mode cli

# Hybrid mode (default)
python main.py --mode hybrid
```

## 🤖 Multi-Agent System

### Agent Types

1. **Core Agents** - Always active, low latency
   - Planner: Task classification
   - Router: Execution path selection
   - Safety: Permission validation

2. **Dynamic Agents** - Role-based, created on demand
   - Researcher: Web research and analysis
   - Developer: Code development and review
   - Analyst: Data processing and insights

3. **Autonomous Agents** - Goal-driven, iterative execution
   - Tool generation
   - Code execution
   - Workflow automation

### Agent Workflows

#### Simple Tasks (<0.5s)
```
User: "Open Chrome"
→ Direct tool execution
→ Immediate response
```

#### Complex Tasks (1-10s)
```
User: "Research AI trends"
→ Dynamic agent creation
→ Multi-step execution
```

#### Autonomous Tasks (2-5min)
```
User: "Build a web scraper"
→ Autonomous agent loop
→ Tool generation and execution
```

## 🛠️ Tools and Capabilities

### System Control

```bash
# Application control
"Open notepad"
"Switch to chrome"
"Close current window"

# File operations
"Read config.json"
"Edit settings.txt"
"Create backup"

# OS automation
"Type hello world"
"Press enter"
"Take screenshot"
```

### Web Research

```bash
# Search and research
"Search for Python tutorials"
"Research latest AI news"
"Find information about quantum computing"

# Content analysis
"Summarize this article"
"Extract key points from this page"
"Compare different sources"
```

### Code Development

```bash
# Code generation
"Write a Python function for fibonacci"
"Create a web scraper with BeautifulSoup"
"Generate a REST API with Flask"

# Code analysis
"Debug this Python code"
"Review this JavaScript"
"Optimize this algorithm"
```

### Data Analysis

```bash
# Data processing
"Analyze sales_data.csv"
"Process this dataset"
"Find patterns in user behavior"

# Visualization
"Create a chart from this data"
"Generate a report with graphs"
"Visualize trends over time"
```

## 🔐 Safety and Permissions

### Permission System

All system operations require explicit permission:

```bash
VoiceOS: "I need to open Chrome. Allow? [y/N]"
User: "y"
VoiceOS: "Opening Chrome..."
```

### Safety Levels

- **Low**: File reading, basic operations
- **Medium**: File writing, application control
- **High**: System-level operations, code execution

### Workspace Isolation

Autonomous tasks run in isolated workspaces:

```
workspace/
├── task_abc123/
│   ├── code/          # Generated source code
│   ├── tools/         # Executable tools
│   ├── outputs/       # Results and reports
│   └── logs/          # Execution logs
```

## 📊 Monitoring and Status

### System Status

```bash
# Check overall system health
python main.py --status

# View performance metrics
python main.py --metrics

# Show active tasks
"Show autonomous tasks"
```

### Task Monitoring

```bash
# View task progress
"Show task progress"

# Check workspace
"Show workspace task_abc123"

# View execution logs
"Show logs for latest task"
```

## Advanced Usage

### Custom Agent Creation

```bash
# Create custom agent role
"Create a custom agent for data analysis"
"Build a specialized agent for web scraping"
```

### Workflow Automation

```bash
# Create automation workflows
"Automate daily report generation"
"Build a pipeline for data processing"
"Create a monitoring system"
```

### Integration with External Tools

```bash
# Git operations
"Commit changes with message 'Update'"
"Create new branch feature-x"
"Push changes to remote"

# Email integration
"Send email to team@company.com"
"Check inbox for new messages"
```

## 🔧 Configuration

### Environment Variables

```bash
# Set environment
export VOICEOS_ENV=production
export VOICEOS_MODE=hybrid
export VOICEOS_LOG_LEVEL=info
```

### Configuration Files

```yaml
# config/voiceos.yaml
voiceos:
  mode: hybrid
  safety_level: strict
  workspace_dir: workspace
  log_level: info

agents:
  timeout: 300
  max_iterations: 20
  enable_autonomous: true
```

## 🚨 Troubleshooting

### Common Issues

#### Voice Recognition Not Working
```bash
# Check audio devices
python -c "import sounddevice; print(sounddevice.query_devices())"

# Test microphone
python -c "import sounddevice; sounddevice.rec(1, 44100)"
```

#### Permission Issues
```bash
# Check workspace permissions
ls -la workspace/

# Fix permissions
sudo chown -R $USER:$USER workspace/
```

#### Memory Issues
```bash
# Check memory usage
python main.py --status

# Clear workspace
"Clear workspace"
```

### Debug Mode

```bash
# Enable debug logging
export VOICEOS_LOG_LEVEL=debug
python main.py

# View detailed logs
tail -f logs/voiceos.log
```

## 📈 Performance Tips

### Optimization

1. **Use simple commands** for faster response
2. **Specify clear goals** for autonomous tasks
3. **Monitor resource usage** regularly
4. **Clean up workspaces** periodically

### Best Practices

```bash
# Good: Specific commands
"Open Chrome and search for Python tutorials"

# Avoid: Vague commands
"Do something with Python"

# Good: Clear goals
"Build a web scraper to extract product prices from Amazon"

# Avoid: Unclear goals
"Make something for prices"
```

## 🎯 Examples

### Complete Workflows

#### Research Workflow
```bash
User: "Research latest developments in quantum computing"

VoiceOS: "I'll research quantum computing developments for you."
[Autonomous agent creates research tools]
VoiceOS: "Found 15 recent papers. Key developments include..."
```

#### Development Workflow
```bash
User: "Write a Python script to analyze stock data"

VoiceOS: "I'll create a stock analysis script for you."
[Autonomous agent generates and tests code]
VoiceOS: "Created stock_analyzer.py with data visualization."
```

#### Automation Workflow
```bash
User: "Automate daily sales report generation"

VoiceOS: "I'll build an automation system for daily reports."
[Autonomous agent creates workflow]
VoiceOS: "Automation pipeline ready. Reports will be generated daily."
```

## 📚 Additional Resources

### Documentation

- [Agent Configuration](agents.md)
- [Autonomous System](autonomous_usage_examples.md)
- [API Reference](api.md)
- [Development Guide](development.md)

### Examples

- [Usage Flows](examples/usage_flows.md)
- [Autonomous Examples](examples/autonomous_usage_examples.md)
- [Demo Commands](examples/demo_commands.md)

### Support

- GitHub Issues: Report bugs and request features
- Documentation: Check guides and tutorials
- Community: Join discussions and share experiences

---

**VoiceOS is continuously evolving. Check for updates and new features regularly!**