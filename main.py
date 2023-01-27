import plotly.express as px
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from skimage import data
import json
from PIL import Image, ImageEnhance, ImageFilter
import plotly.graph_objects as go
from dash import dash_table
import pandas as pd
import pytesseract
from io import StringIO
import cv2
from pytesseract import Output as Output1
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

fileName="/Users/nicolasasparriayara/Desktop/Admin1.jpg"

img = cv2.imread(fileName)

pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'
#img = data.chelsea()
columns = ['type','left','top', 'width', 'height', 'scaleX', 'strokeWidth']

d = pytesseract.image_to_data(img, output_type=Output1.DICT)
dfCoord=pd.DataFrame.from_dict(d)
print(dfCoord)
dfCoord = dfCoord[(dfCoord['text'] == "77487-5029")]
dfCoord=dfCoord.iloc[0]
print(dfCoord)
yCoor = dfCoord['top']
xCoor = dfCoord['left']
print (xCoor, yCoor)

fig = Image.open(fileName)
fig = px.imshow(fig)
shapes=pd.read_csv("/Users/nicolasasparriayara/Desktop/shapeSugarLand1.csv")
row_1=shapes.iloc[0]
print(row_1)
yCoor = yCoor-row_1['y0']
xCoor = xCoor-row_1['x0']
print (xCoor, yCoor)
for index, row in shapes.iterrows():
    fig.add_shape(
        type='rect', xref='x', yref='y',
        x0=row['x0']+xCoor, x1=row['x1']+xCoor, y0=row['y0']+yCoor, y1=row['y1']+yCoor, line=dict(color="red", width=1)
    )

fig.update_layout(dragmode="drawrect",
                  #newshape=dict(fillcolor="cyan", opacity=0.3, line=dict(color="red", width=1)),)
                  newshape=dict(line=dict(color="red", width=1)),)
fig.update_layout( margin={'l': 0, 'r': 0, 't': 0, 'b': 0})
config = {
    "modeBarButtonsToAdd": [
        #"drawline",
        #"drawopenpath",
        #"drawclosedpath",
        #"drawcircle",
        "drawrect",
        "eraseshape",
    ]
}

# Build App
app = dash.Dash(__name__)
app.layout = html.Div(
    [
        html.H4("Draw a shape, then modify it"),
        dcc.Graph(id="fig-image", figure=fig, config=config,style={'width': '150vh', 'height': '150vh',"border":"1px black solid"}),
        dcc.Markdown("Characteristics of shapes"),
        html.Pre(id="annotations-pre"),
        dash_table.DataTable(id='canvaas-table',
                             style_cell={'textAlign': 'left'},
                             columns=[{"name": i, "id": i} for i in columns]),
    ]
)


@app.callback(
    Output('canvaas-table', 'data'),
    [Input("fig-image", "relayoutData")],
    prevent_initial_call=True
)
def update_table(relayout_data):
    if 'shapes' in relayout_data:
        shapes = relayout_data['shapes']
        data = []
        for shape in shapes:
            shape_data = {}
            shape_data['type'] = shape['type']
            shape_data['left'] = shape['x0']
            shape_data['top'] = shape['y0']
            shape_data['width'] = shape['x1'] - shape['x0']
            shape_data['height'] = shape['y1'] - shape['y0']
            shape_data['scaleX'] = shape.get('scaleX', None)
            shape_data['strokeWidth'] = shape.get('strokeWidth', None)
            data.append(shape_data)
        return data
    return dash.no_update




if __name__ == "__main__":
    app.run_server(debug=True)