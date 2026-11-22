"""
自定义模板过滤器
"""
from django import template

register = template.Library()


@register.filter
def get_item(mapping, key):
    """从字典中按键取值，供模板按角色 ID 取统计数量"""
    if mapping is None:
        return None
    return mapping.get(key)
