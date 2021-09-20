from flask import Flask, render_template
import pyodbc
import pandas as pd
import json
import plotly
import plotly.express as px

app = Flask(__name__)
server = 'DESKTOP-VLGTJDQ\MSSQLSERVER2019' 
database = 'Sedesa' 
username = 'dash' 
password = 'dash92' 
cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chart1')
def chart1():
    query1 = "SELECT COUNT(CI.LETRA) AS NumeroDeCasosEfermedadesRespiratorias,CI.Letra,DI.CalendarYear as Year,CL.Asentamiento AS Colonia,CL.Nombre_De_La_Localidad FROM [SEDESA].[SAEH].[Defunciones] AS DE INNER JOIN [Catalogos].[DimDate] AS DI ON DE.Id_DimDate=DI.DateKey INNER JOIN [Catalogos].[Cat_CLUES] AS CL ON DE.[Id_CLUE]=CL.Id_CLUE INNER JOIN [Catalogos].[Cat_CIE] AS CI ON DE.Id_CIE=CI.Id_CIE WHERE CI.Letra='J' GROUP BY CL.Asentamiento,CI.Letra,DI.CalendarYear,CL.Nombre_De_La_Localidad order by 3,1 desc"
    df1 = pd.read_sql(query1, cnxn)

    fig = px.bar(df1, x="Nombre_De_La_Localidad", y="NumeroDeCasosEfermedadesRespiratorias", color="Year", barmode="group")

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    header="No. de casos de enfermedades respiratorios por año"
    description = """
    Numeros de casos de enfermedades respiratorios por año en las distintas localidades de la ciudad de México.
    """
    return render_template('notdash2.html', graphJSON=graphJSON, header=header,description=description)

@app.route('/chart2')
def chart2():
    query2 = "SELECT COUNT(CI.LETRA) AS NumeroDeCasosEfermedadesDiabetis,CI.Letra,DI.CalendarYear as Year,CL.Asentamiento AS Colonia,CL.Nombre_De_La_Localidad FROM [SEDESA].[SAEH].[Defunciones] AS DE INNER JOIN [Catalogos].[DimDate] AS DI ON DE.Id_DimDate=DI.DateKey INNER JOIN [Catalogos].[Cat_CLUES] AS CL ON DE.[Id_CLUE]=CL.Id_CLUE INNER JOIN [Catalogos].[Cat_CIE] AS CI ON DE.Id_CIE=CI.Id_CIE WHERE CI.Letra='E' GROUP BY CL.Asentamiento,CI.Letra,DI.CalendarYear,CL.Nombre_De_La_Localidad order by 3,1 desc"
    df2 = pd.read_sql(query2, cnxn)

    fig = px.bar(df2, x="Nombre_De_La_Localidad", y="NumeroDeCasosEfermedadesDiabetis", color="Year", barmode="group")

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    header="No. de casos de diabetis por año"
    description = """
    Numeros de casos de diabetis por año en las distintas localidades de la ciudad de México.
    """
    return render_template('notdash2.html', graphJSON=graphJSON, header=header,description=description)


    