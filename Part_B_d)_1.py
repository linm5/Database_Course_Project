# this file can be run alone to visualize the data, no need to run main.py
# create_engine creates a new connection to a database to run queries and make pandas work
# pd.read_sql_query reads the query and returns a DataFrame

import pandas as pd
import plotly.graph_objects as go # Dynamic visualization library
from sqlalchemy import create_engine 

database = "group_5_2024"
user = "group_5_2024"
password = "f9JsjkRlQee4"
host = "dbcourse.cs.aalto.fi"
port = "5432"

# create a SQLAlchemy engine
db_uri = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
engine = create_engine(db_uri)

# SQL query to fetch the data
query = """
SELECT c.name AS city_name, 
       COUNT(DISTINCT vr.volunteer_id) AS available_volunteers,
       COUNT(DISTINCT va.volunteer_id) AS applied_volunteers
FROM city c
LEFT JOIN volunteer_range vr ON c.id = vr.city_id
LEFT JOIN request_location rl ON c.id = rl.city_id
LEFT JOIN volunteer_application va ON rl.request_id = va.request_id
GROUP BY c.name;
"""

data = pd.read_sql_query(query, engine)

def visualize_volunteers_by_city(data):
    width = 0.4  
    indices = list(range(len(data)))

    # create traces
    trace1 = go.Bar(
        x=indices,
        y=data['available_volunteers'],
        width=width,
        name='Available Volunteers',
        marker_color='blue'
    )
    trace2 = go.Bar(
        x=[i + width for i in indices],
        y=data['applied_volunteers'],
        width=width,
        name='Applied Volunteers',
        marker_color='orange'
    )

    # create the layout
    layout = go.Layout(
        title='Comparison of Available vs. Applied Volunteers by City',
        xaxis=dict(
            title='City',
            tickvals=[i + width / 2 for i in indices],
            ticktext=data['city_name']
        ),
        yaxis=dict(
            title='Number of Volunteers'
        ),
        barmode='group'
    )

    # create the figure
    fig = go.Figure(data=[trace1, trace2], layout=layout)

    # add annotations for bar values
    for i, val in enumerate(data['available_volunteers']):
        fig.add_annotation(
            x=i,
            y=val,
            text=str(val),
            showarrow=False,
            yshift=10,
            font=dict(color="blue")
        )
    for i, val in enumerate(data['applied_volunteers']):
        fig.add_annotation(
            x=i + width,
            y=val,
            text=str(val),
            showarrow=False,
            yshift=10,
            font=dict(color="orange")
        )

    # highlight top and bottom cities
    top_2_cities = data.nlargest(2, 'available_volunteers')[['city_name', 'available_volunteers']]
    bottom_2_cities = data.nsmallest(2, 'available_volunteers')[['city_name', 'available_volunteers']]
    
    for idx, row in top_2_cities.iterrows():
        fig.add_annotation(
            x=indices[row.name],
            y=row['available_volunteers'],
            text='Top',
            showarrow=False,
            yshift=20,
            font=dict(color="green", size=12, family="Arial"),
            align="center"
        )
    
    for idx, row in bottom_2_cities.iterrows():
        fig.add_annotation(
            x=indices[row.name],
            y=row['available_volunteers'],
            text='Bottom',
            showarrow=False,
            yshift=20,
            font=dict(color="red", size=12, family="Arial"),
            align="center"
        )

    fig.show()

    print("Top 2 cities with most available volunteers:")
    print(top_2_cities)
    print("\nBottom 2 cities with least available volunteers:")
    print(bottom_2_cities)

visualize_volunteers_by_city(data)
