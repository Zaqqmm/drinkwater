# -*- coding: utf-8 -*-
"""孕期计算与智能提醒"""

from datetime import date, datetime, timedelta
from typing import Dict, Any, Optional, List

from ..data.models import PregnancyConfig
from ..data.cache import AIContentCache
from ..utils.helpers import calculate_pregnancy_week, calculate_due_date, get_current_season


class PregnancyCalculator:
    """孕期计算器"""
    
    # 孕期阶段划分
    TRIMESTER_WEEKS = {
        1: (1, 13),   # 孕早期
        2: (14, 27),  # 孕中期
        3: (28, 40),  # 孕晚期
    }
    
    def __init__(self, config: PregnancyConfig):
        self._config = config
    
    @property
    def last_period_date(self) -> Optional[date]:
        """末次月经日期"""
        return self._config.last_period_date
    
    @property
    def current_week(self) -> Optional[int]:
        """当前孕周"""
        if not self.last_period_date:
            return None
        weeks, _ = calculate_pregnancy_week(self.last_period_date)
        return weeks
    
    @property
    def current_week_day(self) -> Optional[tuple]:
        """当前孕周和天数 (周, 天)"""
        if not self.last_period_date:
            return None
        return calculate_pregnancy_week(self.last_period_date)
    
    @property
    def due_date(self) -> Optional[date]:
        """预产期"""
        if not self.last_period_date:
            return None
        return calculate_due_date(self.last_period_date)
    
    @property
    def days_until_due(self) -> Optional[int]:
        """距离预产期天数"""
        if not self.due_date:
            return None
        return (self.due_date - date.today()).days
    
    @property
    def trimester(self) -> Optional[int]:
        """当前孕期阶段 (1, 2, 3)"""
        week = self.current_week
        if not week:
            return None
        for tri, (start, end) in self.TRIMESTER_WEEKS.items():
            if start <= week <= end:
                return tri
        return 3 if week > 40 else None
    
    @property
    def trimester_name(self) -> Optional[str]:
        """孕期阶段名称"""
        tri = self.trimester
        if tri == 1:
            return "孕早期"
        elif tri == 2:
            return "孕中期"
        elif tri == 3:
            return "孕晚期"
        return None
    
    def get_week_info(self) -> Dict[str, Any]:
        """获取当前孕周详细信息"""
        week_day = self.current_week_day
        if not week_day:
            return {}
        
        weeks, days = week_day
        
        return {
            'week': weeks,
            'day': days,
            'display': f"{weeks}周{'+' + str(days) + '天' if days > 0 else ''}",
            'trimester': self.trimester,
            'trimester_name': self.trimester_name,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'days_until_due': self.days_until_due,
        }
    
    def get_baby_development_stage(self) -> str:
        """获取宝宝发育阶段描述"""
        week = self.current_week
        if not week:
            return ""
        
        stages = {
            (1, 4): "受精卵正在分裂，准备着床",
            (5, 8): "胚胎期，心脏开始跳动",
            (9, 12): "胎儿期开始，各器官正在形成",
            (13, 16): "胎儿快速生长，可能开始感受到胎动",
            (17, 20): "宝宝活动增多，胎动更明显",
            (21, 24): "宝宝听力发育，可以听到外界声音",
            (25, 28): "宝宝眼睛可以睁开了",
            (29, 32): "宝宝体重快速增加",
            (33, 36): "宝宝各器官基本成熟",
            (37, 40): "足月期，随时可能出生",
        }
        
        for (start, end), desc in stages.items():
            if start <= week <= end:
                return desc
        
        if week > 40:
            return "已过预产期，请注意产检"
        return ""


class PregnancyTipsGenerator:
    """孕期建议生成器"""
    
    def __init__(self, cache: AIContentCache):
        self._cache = cache
        self._llm_manager = None  # 延迟初始化
    
    def set_llm_manager(self, llm_manager):
        """设置 LLM 管理器"""
        self._llm_manager = llm_manager
    
    def get_daily_tips(self, week: int, use_ai: bool = True) -> Dict[str, Any]:
        """
        获取每日孕期建议
        
        Args:
            week: 当前孕周
            use_ai: 是否使用 AI 生成
            
        Returns:
            包含各类建议的字典
        """
        context = {
            'week': week,
            'date': date.today().isoformat(),
            'season': get_current_season()
        }
        
        # 尝试从缓存获取
        cached = self._cache.get('daily_tips', context)
        if cached:
            return cached
        
        # 生成新内容
        if use_ai and self._llm_manager:
            tips = self._generate_ai_tips(week, context)
        else:
            tips = self._get_static_tips(week)
        
        # 保存到缓存
        self._cache.set('daily_tips', context, tips)
        
        return tips
    
    def _generate_ai_tips(self, week: int, context: Dict) -> Dict[str, Any]:
        """使用 AI 生成建议"""
        prompt = f"""
你是一位专业的孕期顾问。请为孕 {week} 周的准妈妈生成今日建议。

当前信息：
- 孕周：{week} 周
- 季节：{context.get('season', '春季')}
- 日期：{context.get('date')}

请生成以下内容，JSON 格式返回：
{{
    "precautions": "今日注意事项（50字内）",
    "activities": "今日可做的事情（50字内）",
    "diet_tips": "饮食建议（50字内）",
    "exercise": "运动建议（30字内）",
    "mood": "情绪调节建议（30字内）",
    "baby_update": "宝宝发育小知识（50字内）"
}}

要求：
1. 内容要针对具体孕周
2. 语气温柔亲切
3. 建议要具体可执行
4. 考虑当前季节特点
"""
        
        try:
            if self._llm_manager:
                response = self._llm_manager.call(prompt)
                if response.success:
                    import json
                    return json.loads(response.content)
        except Exception as e:
            print(f"AI 生成建议失败: {e}")
        
        return self._get_static_tips(week)
    
    def _get_static_tips(self, week: int) -> Dict[str, Any]:
        """获取静态建议（降级方案）"""
        # 根据孕期阶段返回通用建议
        if week <= 13:
            return {
                "precautions": "孕早期注意休息，避免剧烈运动，远离烟酒和有害物质",
                "activities": "可以进行轻度散步，保持心情愉悦",
                "diet_tips": "少量多餐，补充叶酸，多吃新鲜蔬果",
                "exercise": "适度散步，避免剧烈运动",
                "mood": "保持好心情，适当放松",
                "baby_update": "宝宝正在快速发育，各器官开始形成"
            }
        elif week <= 27:
            return {
                "precautions": "孕中期相对稳定，但仍需注意定期产检",
                "activities": "可以适当增加活动量，进行孕妇瑜伽",
                "diet_tips": "注意补充钙、铁，保持均衡饮食",
                "exercise": "孕妇瑜伽、游泳都是不错的选择",
                "mood": "享受孕期，和宝宝互动",
                "baby_update": "宝宝活动增多，可能感受到明显胎动"
            }
        else:
            return {
                "precautions": "孕晚期注意胎动，准备待产包",
                "activities": "适当活动有助于顺产，但避免过度劳累",
                "diet_tips": "少食多餐，控制体重，补充蛋白质",
                "exercise": "散步为主，避免剧烈运动",
                "mood": "放松心情，为分娩做准备",
                "baby_update": "宝宝已经基本发育成熟，随时准备出生"
            }
    
    def get_nutrition_advice(self, week: int, time_period: str = "上午") -> Dict[str, Any]:
        """获取营养建议"""
        context = {
            'week': week,
            'date': date.today().isoformat(),
            'time_period': time_period
        }
        
        cached = self._cache.get('nutrition', context)
        if cached:
            return cached
        
        # 默认营养建议
        advice = {
            "foods": [
                {"name": "坚果", "benefit": "补充 DHA 和蛋白质", "amount": "10-15 颗"},
                {"name": "水果", "benefit": "补充维生素", "amount": "1 份"},
                {"name": "酸奶", "benefit": "补充钙质和益生菌", "amount": "1 杯"}
            ],
            "tip": f"孕 {week} 周，注意均衡营养，保持少量多餐～"
        }
        
        self._cache.set('nutrition', context, advice)
        return advice
