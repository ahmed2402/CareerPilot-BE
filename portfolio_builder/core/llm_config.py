"""
LLM Configuration for Portfolio Builder.

Configures ChatGroq models for different agent tasks:
- Complex reasoning (planner, code generator): openai/gpt-oss-120b"
- Simple tasks (section content): llama-3.1-8b-instant
"""

import os
from functools import lru_cache
from typing import Optional
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.language_models.chat_models import BaseChatModel

load_dotenv()


class LLMConfig:
    """Configuration and factory for LLM instances."""
    
    REASONING_MODEL = "openai/gpt-oss-120b"
    FAST_MODEL = "llama-3.1-8b-instant"
    CODE_MODEL = "openai/gpt-oss-120b"
    
    DEFAULT_TEMPERATURE = 0.7
    CODE_TEMPERATURE = 0.2  
    
    def __init__(self):
        self.api_key = os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GROQ_API_KEY not found in environment variables. "
                "Please set it in your .env file."
            )
    
    @lru_cache(maxsize=10)
    def get_llm(
        self,
        model_type: str = "reasoning",
        temperature: Optional[float] = None
    ) -> BaseChatModel:
        """
        Get a configured LLM instance.
        
        Args:
            model_type: Type of model - "reasoning", "fast", or "code"
            temperature: Optional temperature override
            
        Returns:
            Configured ChatGroq instance
        """
        model_map = {
            "reasoning": (self.REASONING_MODEL, self.DEFAULT_TEMPERATURE),
            "fast": (self.FAST_MODEL, self.DEFAULT_TEMPERATURE),
            "code": (self.CODE_MODEL, self.CODE_TEMPERATURE),
        }
        
        if model_type not in model_map:
            raise ValueError(f"Unknown model type: {model_type}")
        
        model_name, default_temp = model_map[model_type]
        temp = temperature if temperature is not None else default_temp
        
        return ChatGroq(
            groq_api_key=self.api_key,
            model_name=model_name,
            temperature=temp,
            max_tokens=8192,
            max_retries=3,
        )
    
    def get_reasoning_llm(self, temperature: Optional[float] = None) -> BaseChatModel:
        return self.get_llm("reasoning", temperature)
    
    def get_fast_llm(self, temperature: Optional[float] = None) -> BaseChatModel:
        return self.get_llm("fast", temperature)
    
    def get_code_llm(self, temperature: Optional[float] = None) -> BaseChatModel:
        return self.get_llm("code", temperature)


# Singleton instance
_llm_config: Optional[LLMConfig] = None


def get_llm_config() -> LLMConfig:
    """Get the singleton LLMConfig instance."""
    global _llm_config
    if _llm_config is None:
        _llm_config = LLMConfig()
    return _llm_config


def get_reasoning_llm(temperature: Optional[float] = None) -> BaseChatModel:
    """Convenience function to get reasoning LLM."""
    return get_llm_config().get_reasoning_llm(temperature)


def get_fast_llm(temperature: Optional[float] = None) -> BaseChatModel:
    """Convenience function to get fast LLM."""
    return get_llm_config().get_fast_llm(temperature)


def get_code_llm(temperature: Optional[float] = None) -> BaseChatModel:
    """Convenience function to get code generation LLM."""
    return get_llm_config().get_code_llm(temperature)
