# -*- coding: utf-8 -*-
"""API Key 状态监控"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from .manager import LLMManager


class KeyStatusMonitor:
    """API Key 状态监控器"""
    
    # 提醒阈值
    EXPIRY_WARNING_DAYS = 7  # Key 过期前 7 天提醒
    LOW_BALANCE_THRESHOLD = 10.0  # 余额低于 10 元提醒
    
    def __init__(self, llm_manager: LLMManager):
        self.llm_manager = llm_manager
    
    def check_on_startup(self) -> List[str]:
        """
        启动时检查所有 Key 状态
        
        Returns:
            警告消息列表
        """
        warnings = []
        
        for provider in self.llm_manager.get_available_providers():
            if provider['enabled'] and provider['has_key']:
                status = self.llm_manager.check_key(provider['id'])
                
                if not status.get('valid'):
                    provider_name = provider['name']
                    error = status.get('error', '未知错误')
                    warnings.append(f"{provider_name} API Key 无效：{error}")
        
        return warnings
    
    def should_remind_expiry(self, provider: str) -> bool:
        """
        检查是否需要提醒 Key 即将过期
        
        Args:
            provider: 提供商 ID
            
        Returns:
            是否需要提醒
        """
        config = self.llm_manager.get_provider_config(provider)
        if not config:
            return False
        
        key_status = config.get('key_status', {})
        
        # 检查过期时间
        expires_at = key_status.get('expires_at')
        if expires_at:
            try:
                expiry_date = datetime.fromisoformat(expires_at)
                days_until_expiry = (expiry_date - datetime.now()).days
                if days_until_expiry <= self.EXPIRY_WARNING_DAYS:
                    return True
            except (ValueError, TypeError):
                pass
        
        # 检查余额
        balance = key_status.get('balance')
        if balance is not None and balance < self.LOW_BALANCE_THRESHOLD:
            return True
        
        return False
    
    def get_status_summary(self) -> str:
        """
        获取当前状态摘要
        
        Returns:
            状态描述文字
        """
        active = self.llm_manager.get_active_provider()
        config = self.llm_manager.get_provider_config(active)
        
        if not config:
            return "⚠️ 未配置任何 AI 模型"
        
        key_status = config.get('key_status', {})
        provider_name = config.get('name', active)
        
        if key_status.get('valid'):
            balance = key_status.get('balance')
            if balance is not None:
                return f"✓ {provider_name} 正常（余额 ¥{balance:.2f}）"
            return f"✓ {provider_name} 正常"
        else:
            error = key_status.get('error', '未知错误')
            return f"⚠️ {provider_name} 不可用：{error}"
    
    def get_all_status(self) -> List[Dict[str, Any]]:
        """
        获取所有提供商的状态
        
        Returns:
            状态列表
        """
        statuses = []
        
        for provider in self.llm_manager.get_available_providers():
            config = self.llm_manager.get_provider_config(provider['id'])
            if not config:
                continue
            
            key_status = config.get('key_status', {})
            
            status_info = {
                'id': provider['id'],
                'name': provider['name'],
                'enabled': provider['enabled'],
                'has_key': provider['has_key'],
                'is_active': provider['is_active'],
                'valid': key_status.get('valid', False),
                'error': key_status.get('error'),
                'checked_at': key_status.get('checked_at'),
                'needs_attention': False
            }
            
            # 判断是否需要关注
            if provider['enabled'] and provider['has_key']:
                if not key_status.get('valid'):
                    status_info['needs_attention'] = True
                elif self.should_remind_expiry(provider['id']):
                    status_info['needs_attention'] = True
            
            statuses.append(status_info)
        
        return statuses
    
    def get_recommendations(self) -> List[str]:
        """
        获取优化建议
        
        Returns:
            建议列表
        """
        recommendations = []
        providers = self.llm_manager.get_available_providers()
        
        # 检查是否有可用的提供商
        valid_providers = [p for p in providers if p['enabled'] and p['has_key'] and p['key_valid']]
        
        if not valid_providers:
            recommendations.append("💡 建议配置至少一个 AI 模型的 API Key")
        elif len(valid_providers) == 1:
            recommendations.append("💡 建议配置备用 AI 模型，以防主模型不可用")
        
        # 检查活跃提供商是否有效
        active = self.llm_manager.get_active_provider()
        active_config = self.llm_manager.get_provider_config(active)
        if active_config:
            key_status = active_config.get('key_status', {})
            if not key_status.get('valid') and valid_providers:
                # 推荐切换到可用的提供商
                valid_names = [p['name'] for p in valid_providers]
                recommendations.append(
                    f"💡 当前模型不可用，建议切换到：{', '.join(valid_names)}"
                )
        
        return recommendations
