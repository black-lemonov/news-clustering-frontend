import json
from flask import Blueprint, render_template, request, session
import requests

from app import BASE_API_URL, redis_conn, CACHE_EXPIRE_SECONDS
from app.utils import init_reactions, format_date, get_cache_key, get_cache_key_by_id

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 10, type=int)
    
    cache_key = get_cache_key(page, size)
    
    cached_data = redis_conn.get(cache_key)
    if cached_data:
        data = json.loads(cached_data)
        summaries = data['data']
        pagination = data['pagination']
        
        return render_template(
            'index.html',
            summaries=summaries,
            pagination=pagination,
            current_page=page,
            total_pages=max(pagination["total"]-1, 0),
            date_formatter=format_date
        )
    
    response = requests.get(
        f"{BASE_API_URL}/summaries",
        params={'page': page, 'size': size}
    )
    
    if response.status_code == 200:
        data = response.json()
        summaries = data['data']
        pagination = data['pagination']
        
        redis_conn.setex(
            cache_key, 
            CACHE_EXPIRE_SECONDS, 
            json.dumps(data)
        )
        
        return render_template(
            'index.html',
            summaries=summaries,
            pagination=pagination,
            current_page=page,
            total_pages=max(pagination["total"]-1, 0),
            date_formatter=format_date
        )
    
    if response.status_code == 404:
        return render_template('errors/404.html'), 404
        
    return render_template('errors/500.html'), 500

@bp.route('/summaries/<int:id>')
def summary_detail(id):
    init_reactions()
    
    cache_key = get_cache_key_by_id(id)
    
    cached_data = redis_conn.get(cache_key)
    if cached_data:
        summary = json.loads(cached_data)
        str_id = str(id)
        reaction_state = session['reactions'].get(
            str_id,
            {
                'like': False,
                'dislike': False
            }
        )
        return render_template(
            'detail.html', 
            summary=summary,
            reaction_state=reaction_state,
            summary_id=str_id,
            date_formatter=format_date
        )
    
    response = requests.get(f"{BASE_API_URL}/summaries/{id}")
    
    if response.status_code == 200:
        summary = response.json()
        str_id = str(id)
        reaction_state = session['reactions'].get(
            str_id,
            {
                'like': False,
                'dislike': False
            }
        )
        
        redis_conn.setex(
            cache_key, 
            CACHE_EXPIRE_SECONDS, 
            json.dumps(summary)
        )
        
        return render_template(
            'detail.html', 
            summary=summary,
            reaction_state=reaction_state,
            summary_id=str_id,
            date_formatter=format_date
        )
    
    if response.status_code == 404:
        return render_template('errors/404.html'), 404
        
    return render_template('errors/500.html'), 500