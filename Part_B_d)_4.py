# for this free choice part, analyze the request fulfillment rate 
# and volunteer retention rate are chosen, 2 visualizations are created.

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine

database = "group_5_2024"
user = "group_5_2024"
password = "f9JsjkRlQee4"
host = "dbcourse.cs.aalto.fi"
port = "5432"

DIALECT = "postgresql+psycopg2://"
db_uri = f"{DIALECT}{user}:{password}@{host}/{database}"
engine = create_engine(db_uri)
psql_conn = engine.connect()

city_df = pd.read_sql_query("SELECT * FROM city", psql_conn)
volunteer_df = pd.read_sql_query("SELECT * FROM volunteer", psql_conn)
volunteer_range_df = pd.read_sql_query("SELECT * FROM volunteer_range", psql_conn)
skill_df = pd.read_sql_query("SELECT * FROM skill", psql_conn)
skill_assignment_df = pd.read_sql_query("SELECT * FROM skill_assignment", psql_conn)
interest_df = pd.read_sql_query("SELECT * FROM interest", psql_conn)
interest_assignment_df = pd.read_sql_query("SELECT * FROM interest_assignment", psql_conn)
beneficiary_df = pd.read_sql_query("SELECT * FROM beneficiary", psql_conn)
request_df = pd.read_sql_query("SELECT * FROM request", psql_conn)
request_skill_df = pd.read_sql_query("SELECT * FROM request_skill", psql_conn)
request_location_df = pd.read_sql_query("SELECT * FROM request_location", psql_conn)
volunteer_application_df = pd.read_sql_query("SELECT * FROM volunteer_application", psql_conn)

# part 1: Request Fulfillment Rate Analysis

# Aggregate the number of volunteers needed for each request
request_volunteers_needed = request_df[['id', 'number_of_volunteers', 'title']]
# Count the number of valid applications for each request
valid_applications = volunteer_application_df[volunteer_application_df['is_valid']]
applications_count = valid_applications.groupby('request_id').size().reset_index(name='applications_count')
# Merge the data to calculate the fulfillment rate
fulfillment_data = pd.merge(request_volunteers_needed, applications_count, left_on='id', right_on='request_id', how='left')
fulfillment_data['applications_count'].fillna(0, inplace=True)
fulfillment_data['fulfillment_rate'] = fulfillment_data['applications_count'] / fulfillment_data['number_of_volunteers']
# Group by title and calculate total number of volunteers needed and total valid applications
grouped_fulfillment_data = fulfillment_data.groupby('title').sum().reset_index()
# Plotting the number of volunteers needed and valid applications for each unique request title using Plotly
fig = go.Figure()

fig.add_trace(go.Bar(
    x=grouped_fulfillment_data['title'],
    y=grouped_fulfillment_data['number_of_volunteers'],
    name='Volunteers Needed',
    marker_color='indianred'
))

fig.add_trace(go.Bar(
    x=grouped_fulfillment_data['title'],
    y=grouped_fulfillment_data['applications_count'],
    name='Valid Applications',
    marker_color='lightsalmon'
))

# Adding a horizontal line for the average number of valid applications
average_applications = grouped_fulfillment_data['applications_count'].mean()
fig.add_trace(go.Scatter(
    x=grouped_fulfillment_data['title'],
    y=[average_applications] * len(grouped_fulfillment_data['title']),
    name=f'Average Valid Applications ({average_applications:.2f})',
    mode='lines',
    line=dict(color='red', dash='dash')
))

fig.update_layout(
    title='Volunteers Needed vs. Valid Applications for Each Unique Request Title',
    xaxis_tickangle=-45,
    barmode='group',
    xaxis_title='Request Title',
    yaxis_title='Number of Volunteers',
    legend_title_text='Legend'
)

fig.show()

# part 2: Volunteer Retention Analysis

# convert the 'modified' column to datetime format for easier analysis
volunteer_application_df['modified'] = pd.to_datetime(volunteer_application_df['modified'])
# extract the year and month from the 'modified' column
volunteer_application_df['year'] = volunteer_application_df['modified'].dt.year
volunteer_application_df['month'] = volunteer_application_df['modified'].dt.month
# count the number of unique active volunteers per month
active_volunteers_per_month = volunteer_application_df.groupby(['year', 'month'])['volunteer_id'].nunique().reset_index()
active_volunteers_per_month.rename(columns={'volunteer_id': 'active_volunteers'}, inplace=True)
# plotting the active volunteers over time using Plotly
fig2 = px.line(active_volunteers_per_month, 
               x=active_volunteers_per_month['year'].astype(str) + '-' + active_volunteers_per_month['month'].astype(str), 
               y='active_volunteers', 
               labels={'x': 'Month', 'active_volunteers': 'Number of Active Volunteers'},
               title='Active Volunteers Over Time')

fig2.update_layout(xaxis_tickangle=-45)
fig2.show()
