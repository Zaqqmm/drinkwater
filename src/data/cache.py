# -*- coding: utf-8 -*-
"""API 响应缓存管理"""

from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional
from pathlib import Path

from ..utils.constants import CACHE_FILE
from ..utils.helpers import load_json, save_json


class AIContentCache:
    """AI 生成内容的智能缓存"""
    
    # 缓存规则：content_type -> {ttl_days, group_by}
    CACHE_RULES = {
        'nutrition': {'ttl_days': 7, 'group_by': 'week'},      # 按周缓存
        'relaxation': {'ttl_days': 0, 'group_by': None},       # 不缓存
        'stand_up': {'ttl_days': 1, 'group_by': 'date'},       # 按天缓存
        'posture': {'ttl_days': 7, 'group_by': 'week'},        # 按周缓存
        'daily_tips': {'ttl_days': 1, 'group_by': 'date'},     # 按天缓存
        'diet_analysis': {'ttl_days': 1, 'group_by': 'date'},  # 按天缓存
    }
    
    def __init__(self):
        self._cache: Dict[str, Any] = load_json(CACHE_FILE, {})
    
    def _save_cache(self) -> bool:
        """保存缓存到文件"""
        return save_json(CACHE_FILE, self._cache)
    
    def get_cache_key(self, content_type: str, context: Dict[str, Any]) -> Optional[str]:
        """
        生成缓存键
        
        Args:
            content_type: 内容类型
            context: 上下文信息，包含 week（孕周）或 date（日期）
            
        Returns:
            缓存键，如果不需要缓存则返回 None
        """
        rule = self.CACHE_RULES.get(content_type)
        if not rule:
            return None
        
        group_by = rule.get('group_by')
        if group_by == 'week':
            week = context.get('week', 0)
            return f"{content_type}_week_{week}"
        elif group_by == 'date':
            cache_date = context.get('date', date.today().isoformat())
            return f"{content_type}_{cache_date}"
        else:
            return None  # 不缓存
    
    def _is_expired(self, cached_data: Dict[str, Any], content_type: str) -> bool:
        """检查缓存是否过期"""
        rule = self.CACHE_RULES.get(content_type)
        if not rule or rule['ttl_days'] == 0:
            return True
        
        created_at = cached_data.get('created_at')
        if not created_at:
            return True
        
        try:
            created_time = datetime.fromisoformat(created_at)
            expires_at = created_time + timedelta(days=rule['ttl_days'])
            return datetime.now() > expires_at
        except (ValueError, TypeError):
            return True
    
    def get(self, content_type: str, context: Dict[str, Any]) -> Optional[Any]:
        """
        获取缓存内容
        
        Args:
            content_type: 内容类型
            context: 上下文信息
            
        Returns:
            缓存的内容，如果不存在或已过期则返回 None
        """
        cache_key = self.get_cache_key(content_type, context)
        if not cache_key:
            return None
        
        cached = self._cache.get(cache_key)
        if not cached:
            return None
        
        if self._is_expired(cached, content_type):
            # 清除过期缓存
            del self._cache[cache_key]
            self._save_cache()
            return None
        
        return cached.get('content')
    
    def set(self, content_type: str, context: Dict[str, Any], content: Any) -> bool:
        """
        设置缓存内容
        
        Args:
            content_type: 内容类型
            context: 上下文信息
            content: 要缓存的内容
            
        Returns:
            是否成功保存
        """
        cache_key = self.get_cache_key(content_type, context)
        if not cache_key:
            return False  # 不需要缓存
        
        self._cache[cache_key] = {
            'content': content,
            'created_at': datetime.now().isoformat(),
            'context': context
        }
        return self._save_cache()
    
    def clear(self, content_type: Optional[str] = None) -> bool:
        """
        清除缓存
        
        Args:
            content_type: 如果指定，只清除该类型的缓存；否则清除所有
        """
        if content_type:
            keys_to_delete = [
                k for k in self._cache.keys() 
                if k.startswith(content_type)
            ]
            for key in keys_to_delete:
                del self._cache[key]
        else:
            self._cache = {}
        
        return self._save_cache()
    
    def clear_expired(self) -> int:
        """清除所有过期缓存，返回清除的数量"""
        expired_keys = []
        
        for key, cached in self._cache.items():
            # 从 key 中提取 content_type
            content_type = key.split('_')[0]
            if self._is_expired(cached, content_type):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            self._save_cache()
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        stats = {
            'total_items': len(self._cache),
            'by_type': {}
        }
        
        for key in self._cache.keys():
            content_type = key.split('_')[0]
            if content_type not in stats['by_type']:
                stats['by_type'][content_type] = 0
            stats['by_type'][content_type] += 1
        
        return stats
