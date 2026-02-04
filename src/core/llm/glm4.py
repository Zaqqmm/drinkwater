# -*- coding: utf-8 -*-
"""智谱 GLM-4 API 客户端"""

import httpx
import time
from datetime import datetime
from typing import Dict, Any

from .base import BaseLLMClient, LLMResponse


class GLM4Client(BaseLLMClient):
    """智谱 GLM-4 API 客户端"""
    
    DEFAULT_API_BASE = "https://open.bigmodel.cn/api/paas/v4"
    DEFAULT_MODEL = "glm-4"
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        if not self._api_base:
            self._api_base = self.DEFAULT_API_BASE
        if not self._model:
            self._model = self.DEFAULT_MODEL
    
    def _generate_token(self) -> str:
        """
        生成 JWT Token
        
        GLM-4 使用 JWT 认证，API Key 格式为 "id.secret"
        """
        try:
            import jwt
        except ImportError:
            raise ImportError("需要安装 PyJWT: pip install PyJWT")
        
        api_key_parts = self._api_key.split(".")
        if len(api_key_parts) != 2:
            raise ValueError("Invalid API Key format, expected 'id.secret'")
        
        api_key_id, api_key_secret = api_key_parts
        
        payload = {
            "api_key": api_key_id,
            "exp": int(time.time()) + 3600,  # 1 小时过期
            "timestamp": int(time.time() * 1000)
        }
        
        return jwt.encode(payload, api_key_secret, algorithm="HS256")
    
    def call(self, prompt: str, **kwargs) -> LLMResponse:
        """调用 GLM-4 API"""
        if not self._api_key:
            return self._create_error_response(
                "API Key 未配置",
                "missing_api_key"
            )
        
        try:
            token = self._generate_token()
        except Exception as e:
            return self._create_error_response(
                f"生成 Token 失败: {e}",
                "token_generation_failed"
            )
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self._model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": kwargs.get('max_tokens', self._max_tokens),
            "temperature": kwargs.get('temperature', self._temperature)
        }
        
        try:
            with httpx.Client(timeout=60) as client:
                response = client.post(
                    f"{self._api_base}/chat/completions",
                    json=payload,
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data['choices'][0]['message']['content']
                    tokens = data.get('usage', {}).get('total_tokens', 0)
                    return self._create_success_response(content, tokens)
                
                # 处理错误
                try:
                    error_data = response.json()
                    error_code = error_data.get('error', {}).get('code', 'unknown')
                    error_msg = error_data.get('error', {}).get('message', '未知错误')
                except:
                    error_code = f"http_{response.status_code}"
                    error_msg = f"HTTP 错误: {response.status_code}"
                
                return LLMResponse(
                    success=False,
                    content="",
                    provider="GLM-4",
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
        
        # 检查 Key 格式
        if "." not in self._api_key:
            return {
                "valid": False,
                "checked_at": datetime.now().isoformat(),
                "error": "invalid_format",
                "message": "API Key 格式不正确，应为 'id.secret'"
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
        
        return {
            "valid": False,
            "checked_at": datetime.now().isoformat(),
            "error": test_response.error_code,
            "message": test_response.error_message
        }
