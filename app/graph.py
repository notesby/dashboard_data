from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from app.auth import login_required
from app.models import db, SavedGraph
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
        data = run_query(graph.query_text, graph.fields)
        geojson = None
        if graph.geojson:
            geojson = load_geojson(graph.geojson)
        fig = generate_graph(data, geojson, graph.graph_options, graph.type)
        graphs[i].image = display_graph(fig, "image")

    return render_template('graphs.html', graphs=graphs)


@bp.route('/graph/<int:graph_id>/', methods=['GET', 'POST'])
def get_graph_by(graph_id):
    graph = SavedGraph.query.filter_by(id=graph_id).first()
    data = run_query(graph.query_text, graph.fields)
    geojson = None
    if graph.geojson:
        geojson = load_geojson(graph.geojson)
    fig = generate_graph(data, geojson, graph.graph_options, graph.type)
    graph.image = display_graph(fig, "Graph")

    return render_template('notdash.html', graphJSON=graph.image["data"])


def load_geojson(file_name):
    result = None
    root = os.path.realpath(os.path.dirname(__file__))
    json_path = os.path.join(root, "static", file_name)
    with open(json_path, encoding="utf-8") as file:
        result = json.load(file)
    return result


def run_query(query, fields):
    connection = get_connection()
    clean_query = query
    for field in fields:
        print(field.name, file=sys.stderr)
        print(field.value, file=sys.stderr)
        clean_query = clean_query.replace(f"{{{field.name}}}", f"{field.value}")
    print(clean_query, file=sys.stderr)
    df1 = pd.read_sql(clean_query, connection)
    print(df1.size, file=sys.stderr)
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

