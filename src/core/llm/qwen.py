# -*- coding: utf-8 -*-
"""通义千问 API 客户端"""

import httpx
from datetime import datetime
from typing import Dict, Any

from .base import BaseLLMClient, LLMResponse


class QwenClient(BaseLLMClient):
    """通义千问 API 客户端"""
    
    DEFAULT_API_BASE = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation"
    DEFAULT_MODEL = "qwen-turbo"
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        if not self._api_base:
            self._api_base = self.DEFAULT_API_BASE
        if not self._model:
            self._model = self.DEFAULT_MODEL
    
    def call(self, prompt: str, **kwargs) -> LLMResponse:
        """调用通义千问 API"""
        if not self._api_key:
            return self._create_error_response(
                "API Key 未配置",
                "missing_api_key"
            )
        
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json"
        }
        
        # 通义千问的请求格式略有不同
        payload = {
            "model": self._model,
            "input": {
                "messages": [{"role": "user", "content": prompt}]
            },
            "parameters": {
                "max_tokens": kwargs.get('max_tokens', self._max_tokens),
                "temperature": kwargs.get('temperature', self._temperature)
            }
        }
        
        try:
            with httpx.Client(timeout=60) as client:
                response = client.post(
                    f"{self._api_base}/generation",
                    json=payload,
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # 检查是否有错误
                    if data.get('code'):
                        return LLMResponse(
                            success=False,
                            content="",
                            provider="通义千问",
                            model=self._model,
                            tokens_used=0,
                            error_message=data.get('message', '未知错误'),
                            error_code=data.get('code')
                        )
                    
                    output = data.get('output', {})
                    content = output.get('text', '')
                    usage = data.get('usage', {})
                    tokens = usage.get('total_tokens', 0)
                    
                    return self._create_success_response(content, tokens)
                
                # 处理 HTTP 错误
                try:
                    error_data = response.json()
                    error_code = error_data.get('code', 'unknown')
                    error_msg = error_data.get('message', '未知错误')
                except:
                    error_code = f"http_{response.status_code}"
                    error_msg = f"HTTP 错误: {response.status_code}"
                
                return LLMResponse(
                    success=False,
                    content="",
                    provider="通义千问",
                    model=self._model,
                    tokens_used=0,
                    error_message=error_msg,
                    error_code=error_code
                )
                
        except httpx.TimeoutException:
            return self._create_error_response("请求超时", "timeout")
        except httpx.ConnectError:
            return self._create_error_response("网络连接失败", "network_error")
        except Exception as e:
            return self._create_error_response(str(e), "unknown_error")
    
    def check_key_status(self) -> Dict[str, Any]:
        """检查 API Key 是否有效"""
        if not self._api_key:
            return {
                "valid": False,
                "checked_at": datetime.now().isoformat(),
                "error": "missing_api_key",
                "message": "API Key 未配置"
            }
        
        # 发送测试请求
        test_response = self.call("你好", max_tokens=5)
        
        if test_response.success:
            return {
                "valid": True,
                "checked_at": datetime.now().isoformat(),
                "error": None,
                "message": "API Key 有效"
            }
        
        # 判断是否是认证错误
        is_key_error = test_response.error_code in [
            "InvalidApiKey",
            "Arrearage",
            "InvalidParameter"
        ]
        
        return {
            "valid": not is_key_error,
            "checked_at": datetime.now().isoformat(),
            "error": test_response.error_code,
            "message": test_response.error_message
        }
