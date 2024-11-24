from django import template
from django.utils.timezone import now

register = template.Library()

@register.filter
def elapsed_time(value):
    """
    経過時間を人間が読みやすい形式で返す。
    """
    if not value:
        return "日時不明"

    delta = now() - value
    seconds = delta.total_seconds()

    if seconds < 60:
        return f"{int(seconds)}秒前"
    elif seconds < 3600:
        return f"{int(seconds // 60)}分前"
    elif seconds < 86400:
        return f"{int(seconds // 3600)}時間前"
    else:
        return f"{int(seconds // 86400)}日前"
