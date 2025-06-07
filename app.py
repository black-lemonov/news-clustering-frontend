from flask import Flask, render_template, request, redirect, url_for, session
import requests
import math

app = Flask(__name__)
app.secret_key = 'your_secret_key'
BASE_API_URL = "http://localhost:8000"


def init_reactions():
    if 'reactions' not in session:
        session['reactions'] = {}
        

@app.route('/')
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
            total_pages=pagination["total"]
        )
    else:
        return f"Ошибка: {response.status_code}", 500

@app.route('/summary/<int:id>')
def summary_detail(id):
    init_reactions()
    response = requests.get(f"{BASE_API_URL}/summaries/{id}")
    
    if response.status_code == 200:
        summary = response.json()
        # Используем строковый ID для ключа
        str_id = str(id)
        reaction_state = session['reactions'].get(str_id, {
            'like': False,
            'dislike': False
        })
        return render_template('detail.html', 
                              summary=summary,
                              reaction_state=reaction_state,
                              summary_id=str_id)  # Передаем ID как строку
    else:
        return f"Реферат не найден", 404


@app.route('/reaction/<int:id>/<action>/<state>')
def handle_reaction(id, action, state):
    init_reactions()
    # Используем строковый ID для ключа
    str_id = str(id)
    if str_id not in session['reactions']:
        session['reactions'][str_id] = {'like': False, 'dislike': False}
    
    # Обработка лайков
    if action == 'like':
        if state == 'add':
            # Снимаем дизлайк если он был
            if session['reactions'][str_id]['dislike']:
                requests.patch(f"{BASE_API_URL}/cluster/{id}/dislike/remove")
                session['reactions'][str_id]['dislike'] = False
            # Ставим лайк
            requests.patch(f"{BASE_API_URL}/cluster/{id}/like/add")
            session['reactions'][str_id]['like'] = True
        else:  # remove
            requests.patch(f"{BASE_API_URL}/cluster/{id}/like/remove")
            session['reactions'][str_id]['like'] = False
    
    # Обработка дизлайков
    elif action == 'dislike':
        if state == 'add':
            # Снимаем лайк если он был
            if session['reactions'][str_id]['like']:
                requests.patch(f"{BASE_API_URL}/cluster/{id}/like/remove")
                session['reactions'][str_id]['like'] = False
            # Ставим дизлайк
            requests.patch(f"{BASE_API_URL}/cluster/{id}/dislike/add")
            session['reactions'][str_id]['dislike'] = True
        else:  # remove
            requests.patch(f"{BASE_API_URL}/cluster/{id}/dislike/remove")
            session['reactions'][str_id]['dislike'] = False
    
    session.modified = True
    return redirect(url_for('summary_detail', id=id))


if __name__ == '__main__':
    app.run(port=5000, debug=True)