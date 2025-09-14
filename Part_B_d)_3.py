# just run this .py directly to visualize the data, no need to run main.py
# there are 3 visualization and 1 correlation matrix
# the visualization will show up one by one, close the window to see the next visualization

import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine

def display_dataframe(name, dataframe):
    print(f"Dataframe: {name}")
    print(dataframe)

DATABASE = "group_5_2024"
USER = "group_5_2024"
PASSWORD = "f9JsjkRlQee4"
HOST = "dbcourse.cs.aalto.fi"
PORT = "5432"

engine = create_engine(f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}/{DATABASE}")

# Load the relevant tables into dataframes
volunteer_df = pd.read_sql_table('volunteer', engine)
request_df = pd.read_sql_table('request', engine)
volunteer_application_df = pd.read_sql_table('volunteer_application', engine)
# Filter for only valid applications
valid_applications_df = volunteer_application_df[volunteer_application_df['is_valid'] == True]
# Extract the year and month from the 'modified' column for grouping
valid_applications_df['year_month'] = pd.to_datetime(valid_applications_df['modified']).dt.to_period('M')
request_df['year_month'] = pd.to_datetime(request_df['start_date']).dt.to_period('M')
# Group by year_month and count the number of valid applications and requests
valid_applications_count = valid_applications_df.groupby('year_month').size().reset_index(name='valid_applications')
request_count = request_df.groupby('year_month').size().reset_index(name='requests')
# Merge the two dataframes on year_month
merged_df = pd.merge(valid_applications_count, request_count, on='year_month', how='outer').fillna(0)
# Calculate the difference between requests and valid applications
merged_df['difference'] = merged_df['requests'] - merged_df['valid_applications']
# Determine the months with the most and least valid applications and requests
most_valid_applications = merged_df.loc[merged_df['valid_applications'].idxmax()]
least_valid_applications = merged_df.loc[merged_df['valid_applications'].idxmin()]
most_requests = merged_df.loc[merged_df['requests'].idxmax()]
least_requests = merged_df.loc[merged_df['requests'].idxmin()]
display_dataframe("Merged Data", merged_df)

print("Most Valid Applications:", most_valid_applications)
print("Least Valid Applications:", least_valid_applications)
print("Most Requests:", most_requests)
print("Least Requests:", least_requests)
print(merged_df.describe())

merged_df['year_month'] = merged_df['year_month'].dt.to_timestamp()

# 1. Monthly Trends Visualization
# For matplotlib, when click close button, the next visualization will show up, etc. 
plt.figure(figsize=(12, 6))
plt.plot(merged_df['year_month'], merged_df['valid_applications'], marker='o', label='Valid Applications')
plt.plot(merged_df['year_month'], merged_df['requests'], marker='o', label='Requests')
plt.xlabel('Month')
plt.ylabel('Count')
plt.title('Monthly Trends of Valid Volunteer Applications and Requests')
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.show()
# 2. Difference Analysis Visualization
plt.figure(figsize=(12, 6))
bars = plt.bar(merged_df['year_month'], merged_df['difference'], color='skyblue', width=20)
plt.xlabel('Month')
plt.ylabel('Difference')
plt.title('Difference Between Valid Applications and Requests per Month')
plt.grid(True)

for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval, int(yval), va='bottom', ha='center', color='black', fontsize=8)

plt.xticks(ticks=merged_df['year_month'][::3], labels=merged_df['year_month'][::3].dt.strftime('%Y-%m'), rotation=45)
plt.show()
# 3. Correlation Analysis
plt.figure(figsize=(8, 6))
plt.scatter(merged_df['requests'], merged_df['valid_applications'], color='blue', alpha=0.5)
plt.xlabel('Number of Requests')
plt.ylabel('Number of Valid Applications')
plt.title('Correlation Between Requests and Valid Applications')
plt.grid(True)
plt.show()
# 4. Correlation Matrix (no visualization, only the matrix/table in the terminal)
correlation_matrix = merged_df.corr(numeric_only=True)
print("\nCorrelation Matrix:")
print(correlation_matrix)
