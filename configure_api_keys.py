#!/usr/bin/env python3
"""
Automated API Key Configuration for Advanced AI System
Configures OpenAI, Anthropic, and Google AI API keys automatically
"""

import os
import sys
import requests
from pathlib import Path
from typing import Dict, Tuple
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class APIKeyConfigurator:
    """Automated API key configuration manager"""

    def __init__(self, env_file: str = ".env.ai"):
        self.env_file = Path(env_file)
        self.api_keys = {}
        self.validation_results = {}

    def load_current_config(self) -> Dict[str, str]:
        """Load current environment configuration"""
        config = {}
        if self.env_file.exists():
            with open(self.env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        config[key] = value
        return config

    def save_config(self, config: Dict[str, str]):
        """Save configuration to .env.ai file"""
        # Read existing content
        existing_content = ""
        if self.env_file.exists():
            with open(self.env_file, 'r') as f:
                existing_content = f.read()

        # Update API keys in the content
        lines = existing_content.split('\n')
        updated_lines = []

        for line in lines:
            if line.strip().startswith('OPENAI_API_KEY='):
                key = config.get("OPENAI_API_KEY", "")
                updated_lines.append(f'OPENAI_API_KEY={key}')
            elif line.strip().startswith('ANTHROPIC_API_KEY='):
                key = config.get("ANTHROPIC_API_KEY", "")
                updated_lines.append(f'ANTHROPIC_API_KEY={key}')
            elif line.strip().startswith('GOOGLE_API_KEY='):
                key = config.get("GOOGLE_API_KEY", "")
                updated_lines.append(f'GOOGLE_API_KEY={key}')
            elif line.strip().startswith('WANDB_API_KEY='):
                key = config.get("WANDB_API_KEY", "")
                updated_lines.append(f'WANDB_API_KEY={key}')
            else:
                updated_lines.append(line)

        # Write back to file
        with open(self.env_file, 'w') as f:
            f.write('\n'.join(updated_lines))

        logger.info(f"✅ Configuration saved to {self.env_file}")

    def validate_openai_key(self, api_key: str) -> Tuple[bool, str]:
        """Validate OpenAI API key"""
        try:
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            response = requests.get(
                'https://api.openai.com/v1/models',
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                return True, "✅ OpenAI API key is valid"
            else:
                msg = f"❌ OpenAI API key invalid: {response.status_code}"
                return False, msg
        except Exception as e:
            return False, f"❌ OpenAI API validation failed: {str(e)}"

    def validate_anthropic_key(self, api_key: str) -> Tuple[bool, str]:
        """Validate Anthropic API key"""
        try:
            headers = {
                'x-api-key': api_key,
                'Content-Type': 'application/json'
            }
            response = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers=headers,
                json={
                    "model": "claude-3-haiku-20240307",
                    "max_tokens": 1,
                    "messages": [{"role": "user", "content": "test"}]
                },
                timeout=10
            )
            # 400 is expected for invalid request but valid key
            if response.status_code in [200, 400]:
                return True, "✅ Anthropic API key is valid"
            else:
                msg = f"❌ Anthropic API key invalid: {response.status_code}"
                return False, msg
        except Exception as e:
            return False, f"❌ Anthropic API validation failed: {str(e)}"

    def validate_google_key(self, api_key: str) -> Tuple[bool, str]:
        """Validate Google AI API key"""
        try:
            base_url = 'https://generativelanguage.googleapis.com'
            full_url = f'{base_url}/v1beta/models?key={api_key}'
            response = requests.get(full_url, timeout=10)
            if response.status_code == 200:
                return True, "✅ Google AI API key is valid"
            else:
                msg = f"❌ Google AI API key invalid: {response.status_code}"
                return False, msg
        except Exception as e:
            return False, f"❌ Google AI validation failed: {str(e)}"

    def validate_api_keys(self, api_keys):
        """Validate all API keys"""
        results = {}

        if 'OPENAI_API_KEY' in api_keys and api_keys['OPENAI_API_KEY']:
            results['OPENAI'] = self.validate_openai_key(
                api_keys['OPENAI_API_KEY']
            )

        if 'ANTHROPIC_API_KEY' in api_keys and api_keys['ANTHROPIC_API_KEY']:
            results['ANTHROPIC'] = self.validate_anthropic_key(
                api_keys['ANTHROPIC_API_KEY']
            )

        if 'GOOGLE_API_KEY' in api_keys and api_keys['GOOGLE_API_KEY']:
            results['GOOGLE'] = self.validate_google_key(
                api_keys['GOOGLE_API_KEY']
            )

        return results

    def prompt_for_api_keys(self) -> Dict[str, str]:
        """Prompt user for API keys"""
        print("\n🤖 Advanced AI System - API Key Configuration")
        print("=" * 50)

        api_keys = {}

        print("\n📝 Enter your API keys (press Enter to skip):")

        # OpenAI
        openai_key = input("🔑 OpenAI API Key: ").strip()
        if openai_key:
            api_keys['OPENAI_API_KEY'] = openai_key

        # Anthropic
        anthropic_key = input("🔑 Anthropic API Key: ").strip()
        if anthropic_key:
            api_keys['ANTHROPIC_API_KEY'] = anthropic_key

        # Google AI
        google_key = input("🔑 Google AI API Key: ").strip()
        if google_key:
            api_keys['GOOGLE_API_KEY'] = google_key

        # Weights & Biases (optional)
        wandb_key = input("🔑 Weights & Biases API Key (optional): ").strip()
        if wandb_key:
            api_keys['WANDB_API_KEY'] = wandb_key

        return api_keys

    def auto_configure_from_env(self) -> Dict[str, str]:
        """Auto-configure from environment variables"""
        api_keys = {}

        # Check environment variables
        env_vars = [
            'OPENAI_API_KEY',
            'ANTHROPIC_API_KEY',
            'GOOGLE_API_KEY',
            'WANDB_API_KEY'
        ]
        for var in env_vars:
            value = os.getenv(var)
            if value:
                api_keys[var] = value
                logger.info(f"✅ Found {var} in environment")

        return api_keys

    def configure_api_keys(self, auto_mode=False, validate=True):
        """Main configuration method"""
        print("🚀 Starting AI API Key Configuration...")

        # Load current config
        current_config = self.load_current_config()

        # Get API keys
        if auto_mode:
            # Try to auto-configure from environment
            api_keys = self.auto_configure_from_env()
            if not api_keys:
                logger.warning("⚠️ No API keys found in environment variables")
                return False
        else:
            # Prompt user for keys
            api_keys = self.prompt_for_api_keys()

        if not api_keys:
            logger.warning("⚠️ No API keys provided")
            return False

        # Validate keys if requested
        if validate:
            print("\n🔍 Validating API keys...")
            validation_results = self.validate_api_keys(api_keys)

            # Display results
            for provider, (valid, message) in validation_results.items():
                print(f"   {message}")

            # Check if any keys are invalid
            invalid_keys = [
                k for k, (v, _) in validation_results.items() if not v
            ]
            if invalid_keys:
                logger.error(f"❌ Invalid API keys: {', '.join(invalid_keys)}")
                return False

        # Merge with current config
        updated_config = {**current_config, **api_keys}

        # Save configuration
        self.save_config(updated_config)

        print("\n✅ API Key Configuration Complete!")
        print("🎯 Your AI system is now ready with full capabilities!")

        return True


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Configure AI API Keys")
    parser.add_argument(
        '--auto',
        action='store_true',
        help='Auto-configure from environment variables'
    )
    parser.add_argument(
        '--no-validate',
        action='store_true',
        help='Skip API key validation'
    )
    parser.add_argument(
        '--env-file',
        default='.env.ai',
        help='Environment file path'
    )

    args = parser.parse_args()

    # Create configurator
    configurator = APIKeyConfigurator(args.env_file)

    # Configure API keys
    success = configurator.configure_api_keys(
        auto_mode=args.auto,
        validate=not args.no_validate
    )

    if success:
        print("\n🎉 AI System Ready!")
        print("Run 'python advanced_ai_launcher.py' to start")
        print("your enhanced AI platform!")
        sys.exit(0)
    else:
        print("\n❌ Configuration failed.")
        print("Please check your API keys and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()
