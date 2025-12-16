import numpy as np
import pandas as pd
import os
import dotenv
import psycopg
from sqlalchemy import create_engine

import dash
from dash import dcc
from dash import html
from dash import dash_table
from dash.dependencies import Input, Output

import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go

dotenv.load_dotenv()
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')

dbms = 'postgresql'
package = 'psycopg'
user = 'postgres'
password = POSTGRES_PASSWORD
host = 'postgres'
port = '5432'
db = 'arxiv'

engine = create_engine(f'{dbms}+{package}://{user}:{password}@{host}:{port}/{db}')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Define the Dash app
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    [
        html.H1("ArXiv Papers Dashboard"),

        html.Div([
            dcc.Markdown('''Welcome to the ArXiv Papers Dashboard. 
                         This dashboard provides insights into research papers 
                         available on arXiv.'''),
        ], style={'width':'100%', 'float':'left'}),
    ]
)

app.layout = html.Div([

    html.H1("ArXiv Papers Dashboard"),

    html.Div([
        dcc.Markdown('''Welcome to the ArXiv Papers Dashboard. 
                     This dashboard provides insights into research papers available on arXiv.'''),
        html.Br(), html.Br()
    ], style={'width':'100%', 'float':'left'}),

    html.Div([
        html.Label("Search by Author Name"),
        dcc.Input(
            id='author-input',
            type='text',
            placeholder='e.g., Noah A. Smith',
            style={'width': '100%'}
        )
    ], style={'width': '20%', 'float': 'left', 'padding': '10px'}),

    html.Div([
        dcc.Tabs([
            dcc.Tab(label='Time Series', children=[
                dcc.Graph(id='timeseries-graph')
            ]),

            dcc.Tab(label='Category Distribution', children=[
                dcc.Graph(id='category-graph')
            ]),

            dcc.Tab(label='Paper Metadata', children=[
                html.H5(id='table-title', style={'textAlign': 'left', 'marginBottom': '10px'}),
                dash_table.DataTable(
                    id='metadata-table',
                    columns=[],
                    data=[],
                    page_size=15,
                    style_table={'overflowX': 'auto'},
                    style_header={'backgroundColor': '#f1f1f1', 'fontWeight': 'bold'},
                    style_cell={'padding': '8px', 'fontFamily': 'Arial', 'textAlign': 'left'},
                    style_data_conditional=[
                        {'if': {'row_index': 'odd'}, 'backgroundColor': '#fafafa'}
                    ],
                )
            ]),

            dcc.Tab(label='Interesting Trends', children=[
                html.Br(),
                html.H5("1. Top ArXiv Categories All-Time", style={'textAlign': 'left'}),
                dcc.Graph(id='all-time-trends'),
                html.Br(),
                html.H5("2. Abstract Length Trends", style={'textAlign': 'left'}),
                dcc.Graph(id='abstract-trends'),
                html.Br(),
                html.H5("3. Trends of Select Keywords", style={'textAlign': 'left'}),
                dcc.Graph(id='combined-trends'),
                html.Br(),
                html.H5("4. Multicategory Share Over Time", style={'textAlign': 'left'}),
                dcc.Graph(id='multicategory-trends')
            ]),
        ])
    ], style={'width': '78%', 'float': 'right'})
])


@app.callback([Output('timeseries-graph', 'figure')],
              [Input('author-input', 'value')])

def timeseries(author):

    if author:
        query = """
            SELECT year, paper_count AS count
            FROM author_counts
            WHERE author ILIKE %s
            ORDER BY year
        """
        df = pd.read_sql_query(query, con=engine, params=(author,))
        title = f"ArXiv Papers per Year by {author}"
            
        if df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text=f"No papers found for author: {author}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            fig.update_layout(title=title)
            return [fig]

    else:
        query = f"""
            SELECT *
            FROM homepage
        """
        df = pd.read_sql(query, con=engine)
        title = f"ArXiv Papers per Year"

    fig = px.line(df, x='year', y='count', markers=True, template="plotly", title=title)
    fig.update_xaxes(dtick=1)
    return [fig]


@app.callback([Output("metadata-table", "data"), Output("metadata-table", "columns"), Output("table-title", "children")],
              [Input("author-input", "value")])

def update_metadata_table(author):

    if author:
        query = """
            SELECT
                id,
                title,
                authors_raw AS authors,
                categories,
                submitted_year AS year,
                comments
            FROM papers2
            WHERE authors_raw ILIKE %s
            ORDER BY submitted_year DESC
            LIMIT 100
        """

        df = pd.read_sql(query, engine, params=(f'%{author}%',))
        columns = [{"name": col, "id": col} for col in df.columns]

        if df.empty:
            return [], [{"name": "No results found", "id": "none"}], ""

        return df.to_dict("records"), columns, f"ArXiv Papers by {author}"
    
    else:
        query = f"""
            SELECT *
            FROM default_table
        """
        df = pd.read_sql(query, engine)
        columns = [{"name": col, "id": col} for col in df.columns]

        return df.to_dict("records"), columns, "ArXiv Papers (Recent)"


@app.callback([Output('category-graph', 'figure')],
              [Input('author-input', 'value')])

def update_category_graph(author):
    
    if author:
        # Get papers for the specific author
        query = """
            SELECT categories
            FROM papers2
            WHERE authors_raw ILIKE %s
        """
        df = pd.read_sql(query, engine, params=(f'%{author}%',))
        title = f"Category Distribution for {author}"
        
        if df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text=f"No papers found for author: {author}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            fig.update_layout(title=title)
            return [fig]
    else:
        # Get all papers
        query = """
            SELECT *
            FROM recent
        """
        df = pd.read_sql(query, engine)
        title = "Category Distribution (Recent Papers)"
    
    all_categories = []
    for categories_str in df['categories'].dropna():
        cats = categories_str.split()
        all_categories.extend(cats)
    
    category_counts = pd.Series(all_categories).value_counts().reset_index()
    category_counts.columns = ['category_code', 'count']
    
    # Get category names from database
    query_map = """
        SELECT *
        FROM category_map
    """
    category_map = pd.read_sql(query_map, engine)
    
    # Merge to get full names
    category_counts = category_counts.merge(
        category_map, 
        on='category_code', 
        how='left'
    )

    # Fill in missing names
    category_counts['category_name'] = category_counts['category_name'].fillna(category_counts['category_code'])

    category_counts = category_counts.groupby('category_name')['count'].sum().reset_index()
    category_counts = category_counts.sort_values('count', ascending=False)

    # Create bar chart
    fig = px.bar(
        category_counts.head(15),
        x='category_name',
        y='count',
        title=title,
        labels={'category_name': 'Category', 'count': 'Number of Papers'},
        color='count',
        color_continuous_scale='viridis'
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        showlegend=False
    )
    
    return [fig]


@app.callback([Output('all-time-trends', 'figure')],
              [Input('author-input', 'value')])

def all_time_trends(author):

    myquery = """
        SELECT * 
        FROM category_counts_alltime 
        ORDER BY count DESC
    """
    category_counts = pd.read_sql_query(myquery, con=engine)

    query_map = """
        SELECT *
        FROM category_map
    """
    category_map = pd.read_sql(query_map, engine)

    category_counts = category_counts.merge(
        category_map, 
        on='category_code', 
        how='left'
    )

    category_counts['category_name'] = category_counts['category_name'].fillna(category_counts['category_code'])

    category_counts = category_counts.groupby('category_name')['count'].sum().reset_index()
    category_counts = category_counts.sort_values('count', ascending=False)

    fig = px.bar(
        category_counts.head(15),
        x='category_name',
        y='count',
        title='Most Popular ArXiv Categories (All-Time)',
        labels={'category_name': 'Category', 'count': 'Total Papers'},
        template="plotly", 
        color='count',
        color_continuous_scale='plasma'
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        showlegend=False
    )
    
    return [fig]
    

@app.callback([Output('abstract-trends', 'figure')],
              [Input('author-input', 'value')])

def abstract_trends(author):
    myquery = """
        SELECT *
        FROM abstract_length_by_year
        WHERE year >= 1989
        ORDER BY year
    """
    df = pd.read_sql_query(myquery, con=engine)

    df_melted = df.melt(
        id_vars=['year'], 
        value_vars=['avg_length', 'median_length'],
        var_name='Metric', 
        value_name='Word Count'
    )

    df_melted['Metric'] = df_melted['Metric'].replace({
        'avg_length': 'Average Length',
        'median_length': 'Median Length'
    })

    fig = px.line(
        df_melted,
        x='year',
        y='Word Count',
        color='Metric',
        markers=True,
        title='Abstract Length Trends Over Time',
        labels={'year': 'Year'}
    )

    fig.update_xaxes(dtick=1)
    return [fig]


@app.callback([Output('multicategory-trends', 'figure')],
              [Input('author-input', 'value')])

def multicategory_trends(author):
    myquery = """
        SELECT *
        FROM multicategory_by_year
        WHERE year >= 1991
        ORDER BY year
    """
    df = pd.read_sql_query(myquery, con=engine)

    fig = px.line(
        df,
        x='year',
        y='share',
        markers=True,
        template="plotly",
        title='% of papers with more than one category per year',
        labels={'year': 'Year', 'share': '% of Papers'}
    )

    fig.update_xaxes(dtick=1)
    return [fig]


@app.callback([Output('combined-trends', 'figure')],
              [Input('author-input', 'value')])

def combined_trends(author):

    llm_query = "SELECT * FROM llm WHERE year >= 2010 ORDER BY year"
    df_llm = pd.read_sql_query(llm_query, con=engine)
    df_llm['category'] = 'LLM Papers'
    
    dl_query = "SELECT * FROM dl WHERE year >= 2010 ORDER BY year"
    df_dl = pd.read_sql_query(dl_query, con=engine)
    df_dl['category'] = 'Deep Learning Papers'

    ml_query = "SELECT * FROM ml WHERE year >= 2010 ORDER BY year"
    df_ml = pd.read_sql_query(ml_query, con=engine)
    df_ml['category'] = 'Machine Learning Papers'

    rl_query = "SELECT * FROM rl WHERE year >= 2010 ORDER BY year"
    df_rl = pd.read_sql_query(rl_query, con=engine)
    df_rl['category'] = 'Reinforcement Learning Papers'
    
    df_combined = pd.concat([df_llm, df_dl, df_ml, df_rl], ignore_index=True)
    
    fig = px.line(
        df_combined,
        x='year',
        y='count',
        color='category',
        markers=True,
        template="plotly",
        title= 'LLM, Deep Learning, Machine Learning, and Reinforcement Learning Trends Over Time',
        labels={'year': 'Year', 'count': 'Number of Papers', 'category': 'Category'}
    )
    
    fig.update_xaxes(dtick=1)
    return [fig]


# Run the dashboard
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)