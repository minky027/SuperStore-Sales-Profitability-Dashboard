import pandas as pd
import numpy as np

import plotly.express as px
import plotly.graph_objects as go

from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc

import matplotlib.pyplot as plt
import seaborn as sns

import io
import base64

# Load dataset
df = pd.read_csv(
    "Sample - Superstore.csv",
    encoding='latin1'
)

# Convert date columns
df['Order Date'] = pd.to_datetime(df['Order Date'])
df['Ship Date'] = pd.to_datetime(df['Ship Date'])

# Create additional columns
df['Shipping_Days'] = (df['Ship Date'] - df['Order Date']).dt.days

df['Profit_Margin'] = (df['Profit'] / df['Sales']) * 100

df['Year_Month'] = df['Order Date'].dt.to_period('M').astype(str)

# Initialize app
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY]
)

# KPI Calculations
total_sales = round(df['Sales'].sum(), 2)

total_profit = round(df['Profit'].sum(), 2)

average_profit_margin = round(df['Profit_Margin'].mean(), 2)

number_of_orders = df['Order ID'].nunique()

# Dashboard Layout
app.layout = dbc.Container([

    # Title
    html.H1(
        "SuperStore Sales & Profitability Dashboard",
        className='text-center text-primary mb-4'
    ),

    # KPI Cards
    dbc.Row([

        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H4("Total Sales"),
                    html.H2(f"${total_sales:,.0f}")
                ])
            ], color='primary', inverse=True),
            width=3
        ),

        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H4("Total Profit"),
                    html.H2(f"${total_profit:,.0f}")
                ])
            ], color='success', inverse=True),
            width=3
        ),

        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H4("Average Profit Margin"),
                    html.H2(f"{average_profit_margin:.2f}%")
                ])
            ], color='warning', inverse=True),
            width=3
        ),

        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H4("Number of Orders"),
                    html.H2(f"{number_of_orders}")
                ])
            ], color='dark', inverse=True),
            width=3
        )

    ], className='mb-4'),

    # Filters
    dbc.Row([

        dbc.Col([
            html.Label("Select Region"),

            dcc.Dropdown(
                id='region_dropdown',
                options=[
                    {'label': region, 'value': region}
                    for region in df['Region'].unique()
                ],
                value='West',
                clearable=False
            )
        ], width=4),

        dbc.Col([
            html.Label("Select Category"),

            dcc.Dropdown(
                id='category_dropdown',
                options=[
                    {'label': category, 'value': category}
                    for category in df['Category'].unique()
                ],
                value='Technology',
                clearable=False
            )
        ], width=4)

    ], className='mb-4'),

        # Charts Row 1
    dbc.Row([

        dbc.Col([
            dcc.Graph(id='sales_category_chart')
        ], width=6),

        dbc.Col([
            dcc.Graph(id='profit_subcategory_chart')
        ], width=6)

    ], className='mb-4'),

    # Charts Row 2
    dbc.Row([

        dbc.Col([
            dcc.Graph(id='monthly_sales_chart')
        ], width=6),

        dbc.Col([
            dcc.Graph(id='discount_profit_chart')
        ], width=6)

    ], className='mb-4'),


])

# Callback Function
@app.callback(

    [
        Output('sales_category_chart', 'figure'),
        Output('profit_subcategory_chart', 'figure'),
        Output('monthly_sales_chart', 'figure'),
        Output('discount_profit_chart', 'figure')
    ],

    [
        Input('region_dropdown', 'value'),
        Input('category_dropdown', 'value')
    ]

)

def update_dashboard(selected_region, selected_category):

    # Filter data
    filtered_df = df[
        (df['Region'] == selected_region) &
        (df['Category'] == selected_category)
    ]

    # Sales by Category
    sales_chart = px.bar(
        filtered_df.groupby('Sub-Category')['Sales']
        .sum()
        .reset_index(),

        x='Sub-Category',
        y='Sales',

        title='Sales by Sub-Category',

        color='Sales'
    )

    # Profit by Sub-Category
    profit_chart = px.bar(
        filtered_df.groupby('Sub-Category')['Profit']
        .sum()
        .reset_index(),

        x='Sub-Category',
        y='Profit',

        title='Profit by Sub-Category',

        color='Profit'
    )

    # Monthly Sales Trend
    monthly_chart = px.line(
        filtered_df.groupby('Year_Month')['Sales']
        .sum()
        .reset_index(),

        x='Year_Month',
        y='Sales',

        title='Monthly Sales Trend'
    )

    # Discount vs Profit Scatter Plot
    scatter_chart = px.scatter(
        filtered_df,

        x='Discount',
        y='Profit',

        color='Sub-Category',

        title='Discount vs Profit'
    )

    return (
        sales_chart,
        profit_chart,
        monthly_chart,
        scatter_chart
    )

# Run App
if __name__ == '__main__':
    app.run(debug=True)
