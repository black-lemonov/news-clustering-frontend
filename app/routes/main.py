
from flask import Blueprint, render_template, request, session
import requests

from app import BASE_API_URL, login_manager
from app.utils import init_reactions, format_date

bp = Blueprint('main', __name__)

@bp.route('/')
@login_manager.user_loader
def index():
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 10, type=int)

    response = requests.get(
        f"{BASE_API_URL}/summaries",
        params={'page': page, 'size': size}
    )
    
    if response.status_code == 200:
        data = response.json()
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
    
    if response.status_code == 404:
        return render_template('errors/404.html'), 404
        
    return render_template('errors/500.html'), 500

@bp.route('/summaries/<int:id>')
@login_manager.user_loader
def summary_detail(id):
    init_reactions()
    
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