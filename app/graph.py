from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session, jsonify
)
from werkzeug.exceptions import abort

from app.auth import login_required
from app.models import db, SavedGraph, DefaultGraph, DefaultField, SavedField
from app.models import get_connection
from base64 import b64encode
import pandas as pd
import json
import plotly
import plotly.express as px
import sys
import os

bp = Blueprint('graph', __name__)


@bp.route('/<int:report_id>/graphs', methods=['GET', 'POST'])
def index(report_id):
    graphs = SavedGraph.query.filter_by(report_id=report_id)
    graphs = list([x for x in graphs])
    for i, graph in enumerate(graphs):
        data = run_query(graph, graph.fields)
        geojson = None
        if graph.geojson:
            geojson = load_geojson(graph.geojson)
        fig = generate_graph(data, geojson, graph.graph_options, graph.type)
        graphs[i].image = display_graph(fig, "image")

    return render_template('graphs.html', graphs=graphs, report_id=report_id)


@bp.route('/graph/<int:graph_id>/', methods=['GET', 'POST'])
def get_graph_by(graph_id):
    graph = SavedGraph.query.filter_by(id=graph_id).first()
    data = run_query(graph, graph.fields)
    geojson = None
    if graph.geojson:
        geojson = load_geojson(graph.geojson)
    fig = generate_graph(data, geojson, graph.graph_options, graph.type)
    graph.image = display_graph(fig, "Graph")

    return render_template('notdash.html', graphJSON=graph.image["data"])


@bp.route('/graph/preview', methods=['POST'])
def preview():
    default_graph_id = request.form['graph_id']
    name = request.form['name']
    graph_options = request.form['graph_options']
    geojson = request.form['geojson']
    graph_type = request.form['type']
    order = request.form['order']
    user_id = session.get('user_id')
    keys = request.form.keys()
    fkeys = filter(lambda x: "field" in x, keys)

    default_graph = DefaultGraph.query.filter_by(id=default_graph_id).first()
    graph = SavedGraph()
    graph.name = name
    graph.query_text = default_graph.query_text
    graph.type = graph_type
    graph.order = order
    graph.graph_options = json.loads(graph_options)
    graph.geojson = geojson
    graph.user_id = user_id

    fields = []
    for k in fkeys:
        value = request.form.get(k)
        if value != '':
            fid = k.replace("field_", "")
            fid = int(fid)
            default_field = DefaultField.query.filter_by(id=fid).first()
            field = SavedField()
            field.name = default_field.name
            field.graph_id = graph.id
            field.value = value
            field.default_field_id = fid
            fields.append(field)
    data = run_query(graph, fields)
    geojson = None
    if graph.geojson:
        geojson = load_geojson(graph.geojson)
    fig = generate_graph(data, geojson, graph.graph_options, graph.type)
    graph.image = display_graph(fig, "Graph")

    return graph.image["data"]


@bp.route('/<int:report_id>/graphs/create', methods=['GET', 'POST'])
@login_required
def create(report_id):
    if request.method == 'POST':
        default_graph_id = request.form['graph_id']
        name = request.form['name']
        graph_options = request.form['graph_options']
        geojson = request.form['geojson']
        graph_type = request.form['type']
        order = request.form['order']
        user_id = session.get('user_id')
        keys = request.form.keys()
        fkeys = filter(lambda x: "field" in x, keys)

        default_graph = DefaultGraph.query.filter_by(id=default_graph_id).first()
        graph = SavedGraph()
        graph.name = name
        graph.query_text = default_graph.query_text
        graph.type = graph_type
        graph.order = order
        graph.report_id = report_id
        graph.graph_options = json.loads(graph_options)
        graph.geojson = geojson
        graph.user_id = user_id
        db.session.add(graph)
        db.session.commit()

        for k in fkeys:
            value = request.form.get(k)
            if value != '':
                fid = k.replace("field_", "")
                fid = int(fid)
                default_field = DefaultField.query.filter_by(id=fid).first()
                field = SavedField()
                field.name = default_field.name
                field.graph_id = graph.id
                field.value = value
                field.default_field_id = fid
                db.session.add(field)
        db.session.commit()

        return redirect(url_for("graph.index", report_id=report_id))
    default_graphs = DefaultGraph.query.all()
    graphs_json = json.dumps([o.serialize for o in default_graphs])
    fields = []
    f_ids = {}
    for graph in default_graphs:
        for field in graph.fields:
            if field.id not in f_ids:
                f_ids[field.id] = set()
            f_ids[field.id].add(graph.id)
            fields.append(field)
    for field in fields:
        field.graph_ids = f_ids[field.id]
    fields_json = json.dumps([o.serialize for o in fields])
    return render_template('addgraph.html',
                           graphs=default_graphs,
                           graphs_json=graphs_json,
                           fields_json=fields_json)


def load_geojson(file_name):
    result = None
    root = os.path.realpath(os.path.dirname(__file__))
    json_path = os.path.join(root, "static", file_name)
    with open(json_path, encoding="utf-8") as file:
        result = json.load(file)
    return result


def run_query(graph: SavedGraph, fields: list[SavedField]):
    if graph.cache:
        cache = json.loads(graph.cache)
        data = pd.DataFrame.from_dict(cache)
        print("cached")
        return data

    connection = get_connection()
    clean_query = graph.query_text
    for field in fields:
        clean_query = clean_query.replace(f"{{{field.name}}}", f"{field.value}")
    print(clean_query, file=sys.stderr)
    df1 = pd.read_sql(clean_query, connection)
    print(df1.size, file=sys.stderr)
    graph.cache = df1.to_json()
    db.session.add(graph)
    db.session.commit()
    return df1


def generate_graph(data, geojson, graph_options, graph_type):
    if graph_type == "bar":
        fig = px.bar(data, **graph_options)
        return fig
    elif graph_type == "map.choropleth":
        fig = px.choropleth_mapbox(data, geojson=geojson, **graph_options)
        return fig
    return None


def display_graph(fig, render_option):
    if render_option == 'image':
        img_bytes = fig.to_image(format='png')
        encoding = b64encode(img_bytes).decode()
        img_b64 = "data:image/png;base64," + encoding
        return {"data": img_b64, "type": "image"}
    else:
        data = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return {"data": data, "type": "json"}

