import os.path

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()


def init_app(app):
    db.init_app(app)
    app.app_context().push()
    db.create_all()
    return db


def load_data():
    data = None
    root = os.path.realpath(os.path.dirname(__file__))
    json_path = os.path.join(root,"static","data.json")
    with open(json_path) as f:
        data = json.load(f)
    if data is not None:
        for row in data["Users"]:
            user1 = User(id=row["id"], username=row["username"], password=row["password"])
            db.session.add(user1)
        for row in data["Reports"]:
            new_entry = Report(id=row["id"], name=row["name"], user_id=row["user_id"])
            db.session.add(new_entry)
        for row in data["DefaultGraphs"]:
            new_entry = DefaultGraph(id=row["id"], name=row["name"])
            new_entry.query = row["query"]
            new_entry.type = row["type"]
            db.session.add(new_entry)
        for row in data["DefaultFields"]:
            new_entry = DefaultField(id=row["id"], name=row["name"])
            new_entry.description = row["description"]
            new_entry.type = row["type"]
            db.session.add(new_entry)
        for row in data["DefaultGraphFields"]:
            new_entry = default_graph_default_fields.insert().values(default_graph_id=row["default_graph_id"],
                                                                     default_field_id=row["default_field_id"])
            db.session.execute(new_entry)
        for row in data["SavedField"]:
            new_entry = SavedField(id=row["id"], name=row["name"])
            new_entry.value = row["value"]
            new_entry.default_field_id = row["default_field_id"]
            new_entry.graph_id = row["graph_id"]
            db.session.add(new_entry)
        for row in data["SavedGraph"]:
            new_entry = SavedGraph(id=row["id"], name=row["name"])
            new_entry.query = row["query"]
            new_entry.order = row["order"]
            new_entry.type = row["type"]
            new_entry.user_id = row["user_id"]
            new_entry.report_id = row["report_id"]
            db.session.add(new_entry)
    db.session.commit()
    print("data loaded successfully")


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.TEXT, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_by = db.relationship('User', backref=db.backref('reports', lazy=True))
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow())

    def __repr__(self):
        return '<Report %r>' % self.name


class SavedGraph(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    query = db.Column(db.Text, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(150), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_by = db.relationship('User', backref=db.backref('graphs', lazy=True))
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow())
    report_id = db.Column(db.Integer, db.ForeignKey('report.id'), nullable=False)
    report = db.relationship('Report', backref=db.backref('graphs', lazy=True))
    fields = db.relationship('SavedField', back_populates='graphs')

    def __repr__(self):
        return '<SavedGraph %r>' % self.name


class SavedField(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    value = db.Column(db.String(200), nullable=False)
    graph_id = db.Column(db.Integer, db.ForeignKey('saved_graph.id'))
    graphs = db.relationship('SavedGraph', back_populates='fields')
    default_field_id = db.Column(db.Integer, db.ForeignKey('default_field.id'))
    default_field = db.relationship('DefaultField', back_populates='saved_fields')

    def __repr__(self):
        return '<SavedField %r>' % self.name


default_graph_default_fields = db.Table('default_graph_default_fields', db.metadata,
                                        db.Column('default_graph_id', db.ForeignKey('default_graph.id'), primary_key=True),
                                        db.Column('default_field_id', db.ForeignKey('default_field.id'), primary_key=True))


class DefaultGraph(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    query = db.Column(db.Text, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(150), nullable=False)
    fields = db.relationship('DefaultField', default_graph_default_fields, back_populates='graphs')

    def __repr__(self):
        return '<DefaultGraph %r>' % self.name


class DefaultField(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(400), nullable=False)
    graphs = db.relationship('DefaultGraph', default_graph_default_fields, back_populates='fields')
    saved_fields = db.relationship('SavedField', back_populates='default_field')

    def __repr__(self):
        return '<DefaultField %r>' % self.name

