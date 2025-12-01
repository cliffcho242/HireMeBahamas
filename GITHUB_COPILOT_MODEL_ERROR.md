# GitHub Copilot Model Endpoint Error - Troubleshooting Guide

## Error Description

If you encounter the following error when using GitHub Copilot Workspace or related services:

```
HTTP error 400: bad request: no endpoints available for this model under your current plan and policies
```

This indicates that the AI service is attempting to use a model that is not available under your current GitHub subscription plan.

## Root Cause

This error occurs when:

1. **Model Availability**: The requested AI model (e.g., GPT-4, Claude 3 Sonnet, Gemini Pro, or other premium models) is not included in your GitHub plan
2. **Plan Restrictions**: Your GitHub subscription (Free, Pro, Team, or Enterprise) has specific model access policies
3. **API Rate Limits**: You've exceeded the rate limits for model API calls
4. **Policy Constraints**: Organizational policies restrict access to certain AI models
5. **Missing API Keys**: For application code, API keys may not be configured for the requested models

**Note**: This repository uses the following premium models in its AI features:
- `gpt-4` (OpenAI)
- `claude-3-sonnet-20240229` (Anthropic)
- `gemini-pro` (Google)

These are optional features and require valid API keys to function.

## Available Solutions

### Option 1: Use Standard Models (Recommended)

GitHub Copilot automatically uses models that are available in your plan. Most issues resolve themselves by:

1. Allowing the service to use default model selection
2. Not explicitly requesting premium models in configurations
3. Using standard GitHub Copilot features without custom model specifications

### Option 2: Upgrade GitHub Plan

If you need access to premium AI models:

1. **GitHub Copilot Individual** - Provides access to standard models
2. **GitHub Copilot Business** - Provides organization-wide access with additional models
3. **GitHub Copilot Enterprise** - Provides full access to all available models and features

Visit [GitHub Copilot Plans](https://github.com/features/copilot) for current pricing and features.

### Option 3: Configure Model Fallback

For applications using GitHub Models API, implement fallback logic:

```python
# Example: Python fallback pattern
from requests.exceptions import HTTPError, RequestException

try:
    response = call_premium_model()
except HTTPError as e:
    if e.response.status_code == 400:
        error_data = e.response.json()
        # Check for model availability error
        if 'endpoints' in error_data.get('message', '').lower():
            # Fall back to standard model
            response = call_standard_model()
        else:
            raise
    else:
        raise
except RequestException as e:
    # Handle network errors
    logger.error(f"Network error calling model: {e}")
    response = call_standard_model()
```

```javascript
// Example: JavaScript fallback pattern
try {
  const response = await callPremiumModel();
} catch (error) {
  if (error.response?.status === 400) {
    const errorData = error.response.data;
    // Check for model availability error
    if (errorData.error?.includes('endpoints') || errorData.message?.includes('endpoints')) {
      // Fall back to standard model
      const response = await callStandardModel();
    } else {
      throw error;
    }
  } else {
    throw error;
  }
}
```

## Repository-Specific Guidance

For this repository (HireMeBahamas), the error can occur in multiple contexts:

1. **GitHub Copilot Workspace**: When running automated coding tasks
2. **AI Services in Codebase**: The repository contains AI features with hardcoded model references
3. **GitHub Actions**: If using AI-powered analysis or code generation
4. **CodeRabbit**: If configured with unavailable models

### Current Configuration

This repository contains the following AI-related configurations:

#### GitHub Configuration
- `.github/copilot-instructions.md` - Contains development guidelines for Copilot
- `.coderabbit.yaml` - CodeRabbit configuration (review status disabled)

#### AI Service Files (Contains Hardcoded Model References)
The repository includes AI features that reference premium models:

**Files with hardcoded model names:**
- `ai_config.py` - Configures GPT-4, Claude-3 Sonnet, and Gemini Pro models
- `ai_api_server.py` - Uses GPT-4 and Claude-3 for AI endpoints
- `advanced_ai_orchestrator.py` - References multiple premium models

**Models referenced:**
- `gpt-4` (OpenAI GPT-4)
- `claude-3-sonnet-20240229` (Anthropic Claude 3 Sonnet)
- `gemini-pro` (Google Gemini Pro)

### Impact on Repository Features

These AI features are **optional** and the core application works without them:

1. **Core Features (No AI Required)**: Job posting, user profiles, authentication, messaging
2. **AI-Enhanced Features (Require API Keys)**: Profile analysis, job matching AI, resume analysis

To use AI features, you need valid API keys in your `.env` file:
```bash
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key
```

### Handling the Error in This Repository

If you encounter the HTTP 400 model error while working on this repository:

1. **For GitHub Copilot Workspace**: The error is plan-related, not code-related. Follow the general solutions above.
2. **For AI Services**: These are optional features. If you don't have API keys, they will gracefully fail without breaking the app.
3. **For Development**: You can disable AI features by not setting the API keys in your `.env` file.

## Prevention

To avoid this error in the future:

### For GitHub Copilot Usage
1. **Avoid Requesting Specific Models**: Don't specify premium models when using Copilot
2. **Use Default Settings**: Let GitHub Copilot automatically select appropriate models
3. **Document Requirements**: Clearly state if certain features require premium models

### For Application Code (Like This Repository)
1. **Make AI Features Optional**: Don't require AI services for core functionality
2. **Implement Fallback Logic**: Add try-catch blocks for AI API calls
3. **Use Environment Variables**: Store API keys in `.env` files, not in code
4. **Handle Missing Keys Gracefully**: Don't crash if API keys aren't provided
5. **Consider Model Alternatives**: Use open-source models when possible

### Example: Graceful AI Feature Handling

```python
# Good: Optional AI with fallback and specific exception handling
from requests.exceptions import HTTPError, RequestException
import logging

logger = logging.getLogger(__name__)

def get_job_recommendations(user_id):
    """Get job recommendations with AI fallback to simple algorithm"""
    try:
        if os.getenv('OPENAI_API_KEY'):
            return ai_powered_recommendations(user_id)
    except (HTTPError, RequestException) as e:
        logger.warning(f"AI recommendations failed: {e}")
    except ValueError as e:
        logger.error(f"Invalid configuration for AI recommendations: {e}")
    
    # Fallback to simple algorithm
    return simple_recommendations(user_id)

# Bad: Required AI that raises unhandled errors
def get_job_recommendations(user_id):
    """This will raise an authentication or API error without proper API key"""
    return openai.complete(model="gpt-4", ...)  # Raises error if no key or model unavailable
```

## Verification

To verify your current GitHub Copilot access:

1. Check your GitHub plan at: `https://github.com/settings/billing`
2. View Copilot status at: `https://github.com/settings/copilot`
3. Review organization settings if applicable

## Support

If the error persists after trying these solutions:

1. Check [GitHub Copilot Status](https://www.githubstatus.com/)
2. Review [GitHub Copilot Documentation](https://docs.github.com/en/copilot)
3. Contact [GitHub Support](https://support.github.com/) with the error request ID

**Error Request ID from this instance**: `B818:26DE1C:1A9F477:1E1CC7F:692DCBCC`

## Related Documentation

- [GitHub Copilot Instructions](.github/copilot-instructions.md) - Development guidelines
- [CodeRabbit Configuration](.coderabbit.yaml) - Code review settings

## Summary

This error is typically **not a repository code issue** but rather a limitation of the GitHub subscription plan being used. The repository code itself does not need modification unless you're explicitly calling AI model APIs with hardcoded model names.

For development work on this repository, standard GitHub Copilot access is sufficient for all tasks.
