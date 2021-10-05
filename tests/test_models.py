import pytest
from app.models import *
from app.models import db


def test_add_user(app):
    user1 = User(username="test1", password="test1")
    db.session.add(user1)
    db.session.commit()

    assert User.query.filter_by(username='test1').first() == user1


def test_add_user_with_report(app):
    user1 = User(username="test2", password="test2")
    report1 = Report(name="report1", created_by=user1)
    db.session.add(user1)
    db.session.commit()

    assert User.query.filter_by(username='test2').first().reports[0] == report1


def test_load_data(app):
    load_data()
    user = User.query.filter_by(username='admin').first()

    assert user.username == "admin"
    assert user.reports[0].id == 1
    assert user.reports[0].graphs[0].id == 1
    assert user.reports[0].graphs[0].fields[0].default_field_id == 3

