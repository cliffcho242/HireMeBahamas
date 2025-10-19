# Advanced AI System Configuration
# 100x Enhanced AI Platform - Complete Configuration

import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class AIModelType(Enum):
    """AI Model Types for the enhanced system"""
    NLP = "nlp"
    COMPUTER_VISION = "computer_vision"
    RECOMMENDATION = "recommendation"
    PREDICTIVE = "predictive"
    GENERATIVE = "generative"
    EMBEDDING = "embedding"


class AIServiceProvider(Enum):
    """AI Service Providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    HUGGINGFACE = "huggingface"
    LOCAL = "local"


@dataclass
class AIModelConfig:
    """Configuration for individual AI models"""
    name: str
    provider: AIServiceProvider
    model_type: AIModelType
    model_id: str
    api_key_env: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    cache_dir: Optional[str] = None
    enabled: bool = True
    priority: int = 1


@dataclass
class AIServiceConfig:
    """Configuration for AI services"""
    name: str
    endpoint: str
    timeout: int = 30
    retries: int = 3
    rate_limit: int = 100
    enabled: bool = True

@dataclass
class AIOrchestratorConfig:
    """Main AI Orchestrator Configuration"""
    # System Settings
    enable_gpu: bool = True
    max_workers: int = 8
    batch_size: int = 32
    cache_enabled: bool = True
    monitoring_enabled: bool = True

    # Model Configurations
    models: List[AIModelConfig] = field(default_factory=list)

    # Service Configurations
    services: List[AIServiceConfig] = field(default_factory=list)

    # Performance Settings
    embedding_dim: int = 768
    max_sequence_length: int = 512
    similarity_threshold: float = 0.7

    # Feature Flags
    enable_real_time_processing: bool = True
    enable_predictive_analytics: bool = True
    enable_automated_content: bool = True
    enable_computer_vision: bool = True

    def __post_init__(self):
        """Initialize default configurations"""
        self._load_default_models()
        self._load_default_services()

    def _load_default_models(self):
        """Load default AI model configurations"""
        default_models = [
            # NLP Models
            AIModelConfig(
                name="GPT-4",
                provider=AIServiceProvider.OPENAI,
                model_type=AIModelType.GENERATIVE,
                model_id="gpt-4",
                api_key_env="OPENAI_API_KEY",
                parameters={"temperature": 0.7, "max_tokens": 2000}
            ),
            AIModelConfig(
                name="Claude-3",
                provider=AIServiceProvider.ANTHROPIC,
                model_type=AIModelType.GENERATIVE,
                model_id="claude-3-sonnet-20240229",
                api_key_env="ANTHROPIC_API_KEY",
                parameters={"temperature": 0.7, "max_tokens": 2000}
            ),
            AIModelConfig(
                name="Gemini Pro",
                provider=AIServiceProvider.GOOGLE,
                model_type=AIModelType.GENERATIVE,
                model_id="gemini-pro",
                api_key_env="GOOGLE_API_KEY",
                parameters={"temperature": 0.7}
            ),

            # Embedding Models
            AIModelConfig(
                name="MiniLM Embedding",
                provider=AIServiceProvider.HUGGINGFACE,
                model_type=AIModelType.EMBEDDING,
                model_id="sentence-transformers/all-MiniLM-L6-v2",
                api_key_env="",
                cache_dir="./ai_models/embeddings"
            ),

            # Computer Vision Models
            AIModelConfig(
                name="Face Recognition",
                provider=AIServiceProvider.LOCAL,
                model_type=AIModelType.COMPUTER_VISION,
                model_id="face_recognition",
                api_key_env="",
                parameters={"model": "cnn"}
            ),

            # Recommendation Models
            AIModelConfig(
                name="Job Matching",
                provider=AIServiceProvider.LOCAL,
                model_type=AIModelType.RECOMMENDATION,
                model_id="job_matching_v1",
                api_key_env="",
                parameters={"algorithm": "cosine_similarity"}
            )
        ]
        self.models.extend(default_models)

    def _load_default_services(self):
        """Load default AI service configurations"""
        default_services = [
            AIServiceConfig(
                name="OpenAI API",
                endpoint="https://api.openai.com/v1",
                timeout=30,
                retries=3,
                rate_limit=100
            ),
            AIServiceConfig(
                name="Anthropic API",
                endpoint="https://api.anthropic.com",
                timeout=30,
                retries=3,
                rate_limit=50
            ),
            AIServiceConfig(
                name="Google AI API",
                endpoint="https://generativelanguage.googleapis.com",
                timeout=30,
                retries=3,
                rate_limit=60
            ),
            AIServiceConfig(
                name="AI API Server",
                endpoint="http://localhost:8009",
                timeout=10,
                retries=2,
                rate_limit=1000
            )
        ]
        self.services.extend(default_services)

@dataclass
class AIPerformanceConfig:
    """AI System Performance Configuration"""
    # Processing Limits
    max_concurrent_requests: int = 50
    max_queue_size: int = 1000
    request_timeout: int = 60

    # Resource Limits
    max_memory_usage: str = "4GB"
    max_cpu_usage: float = 0.8
    max_gpu_memory: str = "8GB"

    # Caching
    cache_ttl: int = 3600  # 1 hour
    cache_max_size: str = "1GB"

    # Monitoring
    metrics_interval: int = 30
    health_check_interval: int = 60

@dataclass
class AIIntegrationConfig:
    """AI System Integration Configuration"""
    # Database Integration
    vector_db_enabled: bool = True
    vector_db_url: str = "http://localhost:6333"

    # Cache Integration
    redis_enabled: bool = True
    redis_url: str = "redis://localhost:6379"

    # Search Integration
    elasticsearch_enabled: bool = True
    elasticsearch_url: str = "http://localhost:9200"

    # Monitoring Integration
    mlflow_enabled: bool = False
    mlflow_url: str = "http://localhost:5000"

    wandb_enabled: bool = False
    wandb_project: str = "hirebahamas-ai"

@dataclass
class AIAdvancedConfig:
    """Advanced AI Configuration"""
    # Multi-modal Processing
    enable_multi_modal: bool = True
    supported_modalities: List[str] = field(default_factory=lambda: ["text", "image", "audio"])

    # Advanced Features
    enable_federated_learning: bool = False
    enable_edge_computing: bool = False
    enable_quantum_acceleration: bool = False

    # Security
    enable_model_encryption: bool = False
    enable_differential_privacy: bool = False

    # Experimental
    enable_neural_architecture_search: bool = False
    enable_auto_ml: bool = True

class AIConfigManager:
    """Central AI Configuration Manager"""

    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or ".env.ai"
        self.orchestrator_config = AIOrchestratorConfig()
        self.performance_config = AIPerformanceConfig()
        self.integration_config = AIIntegrationConfig()
        self.advanced_config = AIAdvancedConfig()

        self._load_from_env()

    def _load_from_env(self):
        """Load configuration from environment variables"""
        # Load API keys and basic settings
        for model in self.orchestrator_config.models:
            if model.api_key_env:
                api_key = os.getenv(model.api_key_env)
                if api_key:
                    model.parameters['api_key'] = api_key

        # Load performance settings
        self.performance_config.max_concurrent_requests = int(os.getenv("AI_MAX_WORKERS", 8))
        self.performance_config.request_timeout = int(os.getenv("AI_REQUEST_TIMEOUT", 60))

        # Load integration settings
        self.integration_config.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.integration_config.elasticsearch_url = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")

        # Load advanced settings
        self.orchestrator_config.enable_gpu = os.getenv("AI_ENABLE_GPU", "true").lower() == "true"
        self.advanced_config.enable_multi_modal = os.getenv("AI_ENABLE_MULTI_MODAL", "true").lower() == "true"

    def get_model_config(self, model_name: str) -> Optional[AIModelConfig]:
        """Get configuration for a specific model"""
        for model in self.orchestrator_config.models:
            if model.name == model_name:
                return model
        return None

    def get_service_config(self, service_name: str) -> Optional[AIServiceConfig]:
        """Get configuration for a specific service"""
        for service in self.orchestrator_config.services:
            if service.name == service_name:
                return service
        return None

    def enable_model(self, model_name: str, enabled: bool = True):
        """Enable or disable a specific model"""
        model = self.get_model_config(model_name)
        if model:
            model.enabled = enabled

    def enable_service(self, service_name: str, enabled: bool = True):
        """Enable or disable a specific service"""
        service = self.get_service_config(service_name)
        if service:
            service.enabled = enabled

    def save_config(self, file_path: str = None):
        """Save current configuration to file"""
        import json
        config_path = file_path or self.config_file

        config_data = {
            "orchestrator": self.orchestrator_config.__dict__,
            "performance": self.performance_config.__dict__,
            "integration": self.integration_config.__dict__,
            "advanced": self.advanced_config.__dict__
        }

        # Convert enums to strings for JSON serialization
        for model in config_data["orchestrator"]["models"]:
            model["provider"] = model["provider"].value
            model["model_type"] = model["model_type"].value

        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=2, default=str)

    def load_config(self, file_path: str = None):
        """Load configuration from file"""
        import json
        config_path = file_path or self.config_file

        if not Path(config_path).exists():
            return

        with open(config_path, 'r') as f:
            config_data = json.load(f)

        # Update configurations
        if "orchestrator" in config_data:
            for key, value in config_data["orchestrator"].items():
                if hasattr(self.orchestrator_config, key):
                    setattr(self.orchestrator_config, key, value)

        if "performance" in config_data:
            for key, value in config_data["performance"].items():
                if hasattr(self.performance_config, key):
                    setattr(self.performance_config, key, value)

        if "integration" in config_data:
            for key, value in config_data["integration"].items():
                if hasattr(self.integration_config, key):
                    setattr(self.integration_config, key, value)

        if "advanced" in config_data:
            for key, value in config_data["advanced"].items():
                if hasattr(self.advanced_config, key):
                    setattr(self.advanced_config, key, value)

# Global configuration instance
ai_config = AIConfigManager()

def get_ai_config() -> AIConfigManager:
    """Get the global AI configuration instance"""
    return ai_config

def reload_ai_config():
    """Reload AI configuration from environment and files"""
    global ai_config
    ai_config = AIConfigManager()

# Export configurations
__all__ = [
    'AIConfigManager',
    'AIOrchestratorConfig',
    'AIPerformanceConfig',
    'AIIntegrationConfig',
    'AIAdvancedConfig',
    'AIModelType',
    'AIServiceProvider',
    'get_ai_config',
    'reload_ai_config'
]