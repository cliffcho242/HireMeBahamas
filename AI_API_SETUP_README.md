# 🤖 HireBahamas AI System - API Key Configuration Guide

## 🚀 Quick Start - Automated Setup

### Option 1: One-Click Launch (Recommended)
```bash
# Windows
AUTO_LAUNCH_HIREBAHAMAS.bat

# PowerShell
.\setup_api_keys.ps1
```

### Option 2: Manual Configuration
```bash
# Interactive setup
python configure_api_keys.py

# Auto-configure from environment variables
python configure_api_keys.py --auto

# Skip validation (faster)
python configure_api_keys.py --no-validate
```

## 🔑 API Keys Required

Your AI system needs these API keys for full functionality:

### 1. OpenAI API Key
- **Purpose**: GPT-4, GPT-3.5 for text generation and analysis
- **Get it**: https://platform.openai.com/api-keys
- **Environment Variable**: `OPENAI_API_KEY`

### 2. Anthropic API Key
- **Purpose**: Claude-3 for advanced reasoning and analysis
- **Get it**: https://console.anthropic.com/
- **Environment Variable**: `ANTHROPIC_API_KEY`

### 3. Google AI API Key
- **Purpose**: Gemini for multimodal AI capabilities
- **Get it**: https://makersuite.google.com/app/apikey
- **Environment Variable**: `GOOGLE_API_KEY`

### 4. Weights & Biases (Optional)
- **Purpose**: ML experiment tracking and monitoring
- **Get it**: https://wandb.ai/
- **Environment Variable**: `WANDB_API_KEY`

## ⚙️ Configuration Methods

### Method 1: Environment Variables (Recommended)
```bash
# Windows Command Prompt
set OPENAI_API_KEY=your_openai_key_here
set ANTHROPIC_API_KEY=your_anthropic_key_here
set GOOGLE_API_KEY=your_google_key_here

# Then run auto-configuration
python configure_api_keys.py --auto
```

### Method 2: Direct File Edit
Edit `.env.ai` file:
```bash
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GOOGLE_API_KEY=your_google_key_here
```

### Method 3: Interactive Setup
```bash
python configure_api_keys.py
```
Follow the prompts to enter your keys interactively.

## 🔍 Validation

The system automatically validates your API keys:
- ✅ **Green checkmark**: Key is valid and working
- ❌ **Red X**: Key is invalid or has issues

You can skip validation with `--no-validate` for faster setup.

## 🎯 What Each AI Service Does

### 🤖 OpenAI (GPT-4)
- Job description analysis
- Resume optimization
- Interview question generation
- Career advice

### 🧠 Anthropic (Claude-3)
- Complex reasoning tasks
- Ethical AI responses
- Advanced content analysis
- Multi-step problem solving

### 🌟 Google (Gemini)
- Image analysis for resumes
- Multimodal content processing
- Advanced search capabilities
- Real-time recommendations

## 🚨 Troubleshooting

### "No API keys found in environment"
- Set environment variables first, then run with `--auto`
- Or use interactive mode: `python configure_api_keys.py`

### "API key validation failed"
- Check your internet connection
- Verify the API key is correct and active
- Some services may have temporary outages

### "Module not found" errors
- Run: `pip install requests`
- Ensure Python 3.8+ is installed

## 📊 System Architecture

```
API Keys → .env.ai → AI Config Manager → AI Orchestrator
                                      ↓
                               AI API Server (Port 8009)
                                      ↓
                            React Frontend (Port 3000)
```

## 🎮 Advanced Usage

### Custom Configuration File
```bash
python configure_api_keys.py --env-file custom.env
```

### Batch Processing
```bash
# Configure multiple systems
for /L %i in (1,1,5) do python configure_api_keys.py --auto
```

### CI/CD Integration
```yaml
# GitHub Actions example
- name: Configure AI Keys
  run: python configure_api_keys.py --auto --no-validate
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_KEY }}
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_KEY }}
    GOOGLE_API_KEY: ${{ secrets.GOOGLE_KEY }}
```

## 🔐 Security Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** in production
3. **Rotate keys regularly** for security
4. **Monitor API usage** to avoid unexpected charges
5. **Use restricted keys** when possible (limited permissions)

## 📞 Support

If you encounter issues:
1. Check the console output for error messages
2. Verify your API keys are active and have credits
3. Ensure stable internet connection
4. Try running with `--no-validate` to bypass validation

## 🎉 Next Steps

After configuration:
1. **Launch AI System**: `python advanced_ai_launcher.py`
2. **Access Dashboard**: http://localhost:3000/ai
3. **Test Features**: Try job matching, resume analysis, chat
4. **Monitor Performance**: Check system health and metrics

---

**🎯 Your AI system is now 100x more powerful with automated configuration!**