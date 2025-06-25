import io
import json

import requests
from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file
from flask_login import login_required

from app import BASE_API_URL, ADMIN_USERNAME, ADMIN_PASSWORD
from app.utils import format_date

admin_bp = Blueprint('admin', __name__, url_prefix="/admin")


@admin_bp.route('/')
@login_required
def admin_dashboard():
    return render_template('admin/dashboard.html')


@admin_bp.route('/models', methods=['GET', 'POST'])
@login_required
def admin_models():
    response = requests.get(
        f"{BASE_API_URL}/admin/models",
        auth=(ADMIN_USERNAME, ADMIN_PASSWORD)
    )
    models = response.json()['available_models'] if response.status_code == 200 else []

    response_selected = requests.get(
        f"{BASE_API_URL}/admin/models/selected",
        auth=(ADMIN_USERNAME, ADMIN_PASSWORD)
    )
    selected_model = response_selected.json()['selected_model'] if response_selected.status_code == 200 else ''

    if request.method == 'POST':
        model_name = request.form['model_name']
        response = requests.post(
            f"{BASE_API_URL}/admin/models/selected",
            params={"model_name": model_name},
            auth=(ADMIN_USERNAME, ADMIN_PASSWORD)
        )
        if response.status_code == 200:
            flash('Модель успешно изменена', 'success')
            return redirect(url_for('admin.admin_models'))
        else:
            flash('Ошибка при изменении модели', 'danger')

    return render_template('admin/models.html',
                           models=models,
                           selected_model=selected_model)


@admin_bp.route('/parsers', methods=['GET', 'POST'])
@login_required
def admin_parsers():
    response = requests.get(
        f"{BASE_API_URL}/admin/parsers/sites",
        auth=(ADMIN_USERNAME, ADMIN_PASSWORD)
    )
    sites = response.json()['sites_urls'] if response.status_code == 200 else []

    if 'delete' in request.form:
        site_url = request.form['site_url']
        response = requests.delete(
            f"{BASE_API_URL}/admin/parsers/sites",
            params={"site_url": site_url},
            auth=(ADMIN_USERNAME, ADMIN_PASSWORD)
        )
        if response.status_code == 200:
            flash('Парсер успешно удален', 'success')
            return redirect(url_for('admin.admin_parsers'))
        else:
            flash('Ошибка при удалении парсера', 'danger')

    if 'file' in request.files:
        file = request.files['file']
        if file.filename != '':
            response = requests.post(
                f"{BASE_API_URL}/admin/parsers",
                files={'file': (file.filename, file.stream, file.mimetype)},
                auth=(ADMIN_USERNAME, ADMIN_PASSWORD)
            )
            if response.status_code == 200:
                flash('Парсер успешно загружен', 'success')
                return redirect(url_for('admin.admin_parsers'))
            else:
                flash('Ошибка при загрузке парсера', 'danger')

    return render_template('admin/parsers.html', sites=sites)


@admin_bp.route('/parsers/template')
@login_required
def admin_parsers_template():
    response = requests.get(
        f"{BASE_API_URL}/admin/parsers/template",
        auth=(ADMIN_USERNAME, ADMIN_PASSWORD)
    )

    if response.status_code == 200:
        mem = io.BytesIO()
        mem.write(json.dumps(response.json(), indent=2).encode('utf-8'))
        mem.seek(0)
        return send_file(
            mem,
            as_attachment=True,
            download_name='parser_template.json',
            mimetype='application/json'
        )
    else:
        flash('Ошибка при получении шаблона', 'danger')
        return redirect(url_for('admin.admin_parsers'))


@admin_bp.route('/system', methods=['GET', 'POST'])
@login_required
def admin_system():
    response = requests.get(
        f"{BASE_API_URL}/admin/system/timestamp",
        auth=(ADMIN_USERNAME, ADMIN_PASSWORD)
    )
    last_parsing_time = response.json().get('last_parsing_time',
                                            'неизвестно') if response.status_code == 200 else 'ошибка'

    if request.method == 'POST' and 'run_parsing' in request.form:
        response = requests.get(
            f"{BASE_API_URL}/admin/system",
            auth=(ADMIN_USERNAME, ADMIN_PASSWORD)
        )
        if response.status_code == 200:
            flash('Парсинг и кластеризация запущены', 'success')
            return redirect(url_for('admin.admin_system'))
        else:
            flash('Ошибка при запуске парсинга', 'danger')

    if request.method == 'POST' and 'generate_summary' in request.form:
        news_url = request.form['news_url']
        response = requests.post(
            f"{BASE_API_URL}/admin/summaries/",
            params={'news_url': news_url},
            auth=(ADMIN_USERNAME, ADMIN_PASSWORD)
        )
        if response.status_code == 200:
            flash('Реферат успешно создан', 'success')
            return redirect(url_for('admin.admin_system'))
        else:
            flash('Ошибка при создании реферата', 'danger')

    return render_template('admin/system.html', last_parsing_time=last_parsing_time, format_date=format_date)
