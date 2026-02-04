# -*- coding: utf-8 -*-
"""LLM 统一管理器"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

from .base import BaseLLMClient, LLMResponse, LLMProvider
from .deepseek import DeepSeekClient
from .glm4 import GLM4Client
from .qwen import QwenClient
from .openai_client import OpenAIClient
from ...utils.constants import LLM_CONFIG_FILE, RESOURCES_ROOT
from ...utils.helpers import load_json, save_json


class LLMManager:
    """LLM 统一管理器 - 支持多模型切换和降级"""
    
    # 客户端类映射
    CLIENT_CLASSES = {
        'deepseek': DeepSeekClient,
        'glm4': GLM4Client,
        'qwen': QwenClient,
        'openai': OpenAIClient,
    }
    
    # 资源目录中的默认配置
    DEFAULT_CONFIG_PATH = RESOURCES_ROOT / "config" / "llm_config.json"
    
    def __init__(self, config_path: Path = None):
        self.config_path = config_path or LLM_CONFIG_FILE
        self.config = self._load_config()
        self.clients: Dict[str, BaseLLMClient] = {}
        self._init_clients()
    
    def _default_config(self) -> Dict[str, Any]:
        """默认配置"""
        return {
            "version": "1.0",
            "active_provider": "deepseek",
            "auto_fallback": True,
            "fallback_order": ["deepseek", "glm4", "qwen", "openai"],
            
            "providers": {
                "deepseek": {
                    "name": "DeepSeek",
                    "enabled": True,
                    "api_key": "",
                    "api_base": "https://api.deepseek.com/v1",
                    "model": "deepseek-chat",
                    "max_tokens": 500,
                    "temperature": 0.7,
                    "key_status": {"valid": False, "checked_at": None}
                },
                "glm4": {
                    "name": "智谱 GLM-4",
                    "enabled": False,
                    "api_key": "",
                    "api_base": "https://open.bigmodel.cn/api/paas/v4",
                    "model": "glm-4",
                    "max_tokens": 500,
                    "temperature": 0.7,
                    "key_status": {"valid": False, "checked_at": None}
                },
                "qwen": {
                    "name": "通义千问",
                    "enabled": False,
                    "api_key": "",
                    "api_base": "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation",
                    "model": "qwen-turbo",
                    "max_tokens": 500,
                    "temperature": 0.7,
                    "key_status": {"valid": False, "checked_at": None}
                },
                "openai": {
                    "name": "OpenAI",
                    "enabled": False,
                    "api_key": "",
                    "api_base": "https://api.openai.com/v1",
                    "model": "gpt-4o-mini",
                    "max_tokens": 500,
                    "temperature": 0.7,
                    "key_status": {"valid": False, "checked_at": None}
                }
            },
            
            "usage_stats": {
                "total_calls": 0,
                "total_tokens": 0,
                "last_call_at": None,
                "daily_stats": {}
            }
        }
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        # 1. 尝试从用户目录加载
        config = load_json(self.config_path, None)
        if config is not None:
            return config
        
        # 2. 尝试从资源目录加载默认配置
        if self.DEFAULT_CONFIG_PATH.exists():
            config = load_json(self.DEFAULT_CONFIG_PATH, None)
            if config is not None:
                # 复制到用户目录
                self.config = config
                self._save_config()
                return config
        
        # 3. 使用内置默认配置
        config = self._default_config()
        self._save_config()
        return config
    
    def _save_config(self) -> bool:
        """保存配置文件"""
        return save_json(self.config_path, self.config)
    
    def _init_clients(self):
        """初始化所有启用的客户端"""
        self.clients = {}
        
        for provider, provider_config in self.config.get('providers', {}).items():
            if provider_config.get('enabled') and provider_config.get('api_key'):
                client_class = self.CLIENT_CLASSES.get(provider)
                if client_class:
                    self.clients[provider] = client_class(provider_config)
    
    def call(self, prompt: str, **kwargs) -> LLMResponse:
        """
        调用 LLM，支持自动降级
        
        Args:
            prompt: 提示词
            **kwargs: 传递给客户端的额外参数
            
        Returns:
            LLMResponse 对象
        """
        # 1. 尝试主模型
        primary = self.config.get('active_provider', 'deepseek')
        
        if primary in self.clients:
            response = self.clients[primary].call(prompt, **kwargs)
            if response.success:
                self._record_usage(primary, response)
                return response
            
            # 检查是否是 Key 问题
            if response.error_code in ['invalid_api_key', 'insufficient_quota', 'missing_api_key']:
                self._mark_key_invalid(primary, response.error_code)
        
        # 2. 自动降级到备用模型
        if self.config.get('auto_fallback', True):
            for fallback in self.config.get('fallback_order', []):
                if fallback != primary and fallback in self.clients:
                    response = self.clients[fallback].call(prompt, **kwargs)
                    if response.success:
                        self._record_usage(fallback, response)
                        return response
        
        # 3. 所有模型都失败
        return LLMResponse(
            success=False,
            content="",
            provider="none",
            model="none",
            tokens_used=0,
            error_message="所有 LLM 提供商均不可用"
        )
    
    def check_all_keys(self) -> Dict[str, Dict]:
        """检查所有 API Key 状态"""
        results = {}
        
        for provider, client in self.clients.items():
            status = client.check_key_status()
            results[provider] = status
            
            # 更新配置
            if provider in self.config['providers']:
                self.config['providers'][provider]['key_status'] = status
        
        self._save_config()
        return results
    
    def check_key(self, provider: str) -> Dict[str, Any]:
        """检查单个提供商的 Key 状态"""
        if provider in self.clients:
            status = self.clients[provider].check_key_status()
            self.config['providers'][provider]['key_status'] = status
            self._save_config()
            return status
        return {"valid": False, "error": "provider_not_found"}
    
    def set_api_key(self, provider: str, api_key: str) -> bool:
        """设置 API Key"""
        if provider in self.config['providers']:
            self.config['providers'][provider]['api_key'] = api_key
            self.config['providers'][provider]['enabled'] = bool(api_key)
            self._save_config()
            self._init_clients()  # 重新初始化客户端
            return True
        return False
    
    def get_provider_config(self, provider: str) -> Optional[Dict[str, Any]]:
        """获取提供商配置"""
        return self.config.get('providers', {}).get(provider)
    
    def update_provider_config(self, provider: str, updates: Dict[str, Any]) -> bool:
        """更新提供商配置"""
        if provider in self.config['providers']:
            self.config['providers'][provider].update(updates)
            self._save_config()
            self._init_clients()
            return True
        return False
    
    def get_active_provider(self) -> str:
        """获取当前活跃的提供商"""
        return self.config.get('active_provider', 'deepseek')
    
    def set_active_provider(self, provider: str) -> bool:
        """设置活跃的提供商"""
        if provider in self.config['providers']:
            self.config['active_provider'] = provider
            self._save_config()
            return True
        return False
    
    def get_available_providers(self) -> List[Dict[str, Any]]:
        """获取所有可用的提供商列表"""
        providers = []
        for provider_id, config in self.config.get('providers', {}).items():
            providers.append({
                'id': provider_id,
                'name': config.get('name', provider_id),
                'enabled': config.get('enabled', False),
                'has_key': bool(config.get('api_key')),
                'key_valid': config.get('key_status', {}).get('valid', False),
                'is_active': provider_id == self.get_active_provider()
            })
        return providers
    
    def _mark_key_invalid(self, provider: str, reason: str):
        """标记 Key 为无效"""
        if provider in self.config['providers']:
            self.config['providers'][provider]['key_status'] = {
                'valid': False,
                'checked_at': datetime.now().isoformat(),
                'error': reason
            }
            self._save_config()
    
    def _record_usage(self, provider: str, response: LLMResponse):
        """记录使用统计"""
        stats = self.config.get('usage_stats', {})
        stats['total_calls'] = stats.get('total_calls', 0) + 1
        stats['total_tokens'] = stats.get('total_tokens', 0) + response.tokens_used
        stats['last_call_at'] = datetime.now().isoformat()
        
        today = datetime.now().strftime('%Y-%m-%d')
        if 'daily_stats' not in stats:
            stats['daily_stats'] = {}
        if today not in stats['daily_stats']:
            stats['daily_stats'][today] = {'calls': 0, 'tokens': 0, 'by_provider': {}}
        
        stats['daily_stats'][today]['calls'] += 1
        stats['daily_stats'][today]['tokens'] += response.tokens_used
        
        if provider not in stats['daily_stats'][today]['by_provider']:
            stats['daily_stats'][today]['by_provider'][provider] = {'calls': 0, 'tokens': 0}
        stats['daily_stats'][today]['by_provider'][provider]['calls'] += 1
        stats['daily_stats'][today]['by_provider'][provider]['tokens'] += response.tokens_used
        
        self.config['usage_stats'] = stats
        self._save_config()
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """获取使用统计"""
        return self.config.get('usage_stats', {})
    
    def get_today_stats(self) -> Dict[str, Any]:
        """获取今日统计"""
        today = datetime.now().strftime('%Y-%m-%d')
        return self.config.get('usage_stats', {}).get('daily_stats', {}).get(today, {
            'calls': 0,
            'tokens': 0
        })
