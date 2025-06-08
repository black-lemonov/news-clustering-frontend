from datetime import datetime, timedelta, timezone

from flask import session


def init_reactions():
    if 'reactions' not in session:
        session['reactions'] = {}
        

def format_date(date_str: str) -> str:
    dt = datetime.fromisoformat(date_str)
    now = datetime.now(timezone.utc)

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    dt = dt.astimezone(timezone.utc)
    now = now.astimezone(timezone.utc)
    
    today = now.date()
    yesterday = today - timedelta(days=1)
    source_date = dt.date()
    
    if source_date == today:
        return f"Сегодня {dt.strftime('%H:%M')}"
    
    if source_date == yesterday:
        return f"Вчера {dt.strftime('%H:%M')}"
    
    return dt.strftime("%d.%m.%Y %H:%M")


def get_cache_key(page, size):
    return f"summaries:{page}:{size}"


def get_cache_key_by_id(id):
    return f"cluster:{id}"