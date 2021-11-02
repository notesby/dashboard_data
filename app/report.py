from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)

from app.auth import login_required
from app.models import db, Report


bp = Blueprint('reports', __name__)


@bp.route('/')
def index():
    reports = Report.query.all()
    return render_template('reports.html', reports=reports)


@bp.route('/report/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        name = request.form['name']
        user_id = session.get('user_id')
        report = Report(name=name, user_id=user_id)
        db.session.add(report)
        db.session.commit()
        return redirect(url_for("reports.index"))

    return render_template('addreport.html')


