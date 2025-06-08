from flask import Blueprint, session, redirect, url_for
import requests
from app import BASE_API_URL
from app.utils import init_reactions


bp = Blueprint('reactions', __name__)


@bp.route('/reaction/<int:id>/<action>/<state>')
def handle_reaction(id, action, state):
    init_reactions()
    str_id = str(id)
    if str_id not in session['reactions']:
        session['reactions'][str_id] = {'like': False, 'dislike': False}
    
    if action == 'like':
        if state == 'add':
            if session['reactions'][str_id]['dislike']:
                requests.patch(f"{BASE_API_URL}/summaries/{id}/dislike/remove")
                session['reactions'][str_id]['dislike'] = False
            requests.patch(f"{BASE_API_URL}/summaries/{id}/like/add")
            session['reactions'][str_id]['like'] = True
        else:
            requests.patch(f"{BASE_API_URL}/summaries/{id}/like/remove")
            session['reactions'][str_id]['like'] = False
    
    elif action == 'dislike':
        if state == 'add':
            if session['reactions'][str_id]['like']:
                requests.patch(f"{BASE_API_URL}/summaries/{id}/like/remove")
                session['reactions'][str_id]['like'] = False
            requests.patch(f"{BASE_API_URL}/summaries/{id}/dislike/add")
            session['reactions'][str_id]['dislike'] = True
        else:
            requests.patch(f"{BASE_API_URL}/summaries/{id}/dislike/remove")
            session['reactions'][str_id]['dislike'] = False
    
    session.modified = True
    return redirect(url_for('main.summary_detail', id=id))