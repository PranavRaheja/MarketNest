import dash
from dash import html, dcc, Input, Output, State
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc

# Load and prepare the data
data = pd.read_csv('C:\\Users\\iampr\\Desktop\\mlh\\dataset.TSV000', sep='\t')
data['period_begin'] = pd.to_datetime(data['period_begin'])

# Initialize the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

# Define the layout
app.layout = dbc.Container([
    html.H1("MarketNest", className="text-white text-center", style={'background-color': '#004DE1', 'padding': '10px'}),
    dbc.Row([
        dbc.Col(html.Label("Select your city:", className="text-white"), width=3),
        dbc.Col(html.Label("Select the property type:", className="text-white"), width=3),
    ]),
    dbc.Row([
        dbc.Col(dcc.Dropdown(
            id='city-dropdown',
            options=[{'label': city, 'value': city} for city in data['city'].unique()],
            placeholder="Select City",
            style={'color': 'black', 'height': '50px', 'fontSize': '20px'}
        ), width=3),
        dbc.Col(dcc.Dropdown(
            id='property-type-dropdown',
            options=[{'label': ptype, 'value': ptype} for ptype in data['property_type'].unique()],
            placeholder="Select Property Type",
            style={'color': 'black', 'height': '50px', 'fontSize': '20px'}
        ), width=3),
    ]),
    dbc.Row([
        dbc.Col(html.Button("Predict Price", id='predict-button', n_clicks=0, className="btn mt-3", style={'background-color': '#004DE1', 'color': 'white', 'width': '200px'}), width={'size': 6, 'offset': 3}),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col(dcc.Graph(id='median-sale-price-graph'), width=6),
        dbc.Col(html.Div(id='median-sale-price-summary', className="text-white"), width=6),
    ]),
    html.Hr(),
    dbc.Row([
        dbc.Col(dcc.Graph(id='homes-sold-graph'), width=6),
        dbc.Col(html.Div(id='homes-sold-summary', className="text-white", style={'fontSize': '16px'}), width=6),
    ]),
    html.Hr(),
    dbc.Row([
        dbc.Col(dcc.Graph(id='price-drops-graph'), width=6),
        dbc.Col(html.Div(id='price-drops-summary', className="text-white", style={'fontSize': '16px'}), width=6),
    ]),
    html.Hr(),
    dbc.Row([
        dbc.Col(dcc.Graph(id='inventory-levels-graph'), width=6),
        dbc.Col(html.Div(id='inventory-levels-summary', className="text-white", style={'fontSize': '16px'}), width=6),
    ]),
], fluid=True)

# Define callback for updating graphs and summaries
@app.callback(
    [Output(f"{graph}-graph", 'figure') for graph in ["median-sale-price", "homes-sold", "price-drops", "inventory-levels"]] +
    [Output(f"{graph}-summary", 'children') for graph in ["median-sale-price", "homes-sold", "price-drops", "inventory-levels"]],
    [Input('predict-button', 'n_clicks')],
    [State('city-dropdown', 'value'),
     State('property-type-dropdown', 'value')]
)
def update_output(n_clicks, selected_city, selected_property_type):
    if n_clicks > 0 and selected_city and selected_property_type:
        filtered_data = data[(data['city'] == selected_city) & (data['property_type'] == selected_property_type)]
        filtered_data['year'] = filtered_data['period_begin'].dt.year
        annual_data = filtered_data.groupby('year').agg({
            'median_sale_price': 'mean',
            'homes_sold': 'sum',
            'price_drops': 'mean',
            'inventory': 'mean'
        }).reset_index()
        
        # Create plot figures
        figures = [
            px.line(annual_data, x='year', y=metric, title=f"{metric.replace('_', ' ').title()} Over Time", template='plotly_dark')
            for metric in ['median_sale_price', 'homes_sold', 'price_drops', 'inventory']
        ]
        
        # Create summaries
        summaries = [
            html.Div([
                html.H5(f"Summary for {metric.replace('_', ' ').title()}"),
                html.P(f"Current {metric.replace('_', ' ')}: {annual_data[metric].iloc[-1]:,.2f}"),
                html.P(f"Suggested average {metric.replace('_', ' ')}: {annual_data[metric].mean():,.2f}"),
                html.P(f"Negotiation Margin: ${(annual_data[metric].iloc[-1] - annual_data[metric].mean()):,.2f} can be used for negotiations.")
            ]) for metric in ['median_sale_price', 'homes_sold', 'price_drops', 'inventory']
        ]
        
        return (*figures, *summaries)
    
    empty_fig = px.line(title='Select options and click "Predict Price" to see data', template='plotly_dark')
    return (*[empty_fig] * 4, *["No data available"] * 4)

if __name__ == '__main__':
    app.run_server(debug=True)
