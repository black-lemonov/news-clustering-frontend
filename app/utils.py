from flask import session

def init_reactions():
    if 'reactions' not in session:
        session['reactions'] = {}