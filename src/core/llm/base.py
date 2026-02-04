# -*- coding: utf-8 -*-
"""LLM 客户端基类"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum


class LLMProvider(Enum):
    """LLM 提供商枚举"""
    DEEPSEEK = "deepseek"
    GLM4 = "glm4"
    QWEN = "qwen"
    OPENAI = "openai"
    OLLAMA = "ollama"


@dataclass
class LLMResponse:
    """统一的 LLM 响应格式"""
    success: bool
    content: str
    provider: str
    model: str
    tokens_used: int
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'success': self.success,
            'content': self.content,
            'provider': self.provider,
            'model': self.model,
            'tokens_used': self.tokens_used,
            'error_message': self.error_message,
            'error_code': self.error_code
        }


class BaseLLMClient(ABC):
    """LLM 客户端基类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化客户端
        
        Args:
            config: 提供商配置，包含 api_key, api_base, model 等
        """
        self._config = config
        self._api_key = config.get('api_key', '')
        self._api_base = config.get('api_base', '')
        self._model = config.get('model', '')
        self._max_tokens = config.get('max_tokens', 500)
        self._temperature = config.get('temperature', 0.7)
    
    @property
    def provider_name(self) -> str:
        """获取提供商名称"""
        return self._config.get('name', 'Unknown')
    
    @property
    def is_configured(self) -> bool:
        """检查是否已配置"""
        return bool(self._api_key and self._api_base)
    
    @abstractmethod
    def call(self, prompt: str, **kwargs) -> LLMResponse:
        """
        调用 LLM API
        
        Args:
            prompt: 提示词
            **kwargs: 额外参数（max_tokens, temperature 等）
            
        Returns:
            LLMResponse 对象
        """
        pass
    
    @abstractmethod
    def check_key_status(self) -> Dict[str, Any]:
        """
        检查 API Key 状态
        
        Returns:
            包含 valid, checked_at, error 等字段的字典
        """
        pass
    
    def get_balance(self) -> Optional[float]:
        """
        获取账户余额（如果支持）
        
        Returns:
            余额金额，不支持则返回 None
        """
        return None
    
    def _create_error_response(self, error_message: str, error_code: str = "unknown") -> LLMResponse:
        """创建错误响应"""
        return LLMResponse(
            success=False,
            content="",
            provider=self._config.get('name', 'unknown'),
            model=self._model,
            tokens_used=0,
            error_message=error_message,
            error_code=error_code
        )
    
    def _create_success_response(self, content: str, tokens_used: int = 0) -> LLMResponse:
        """创建成功响应"""
        return LLMResponse(
            success=True,
            content=content,
            provider=self._config.get('name', 'unknown'),
            model=self._model,
            tokens_used=tokens_used
        )
