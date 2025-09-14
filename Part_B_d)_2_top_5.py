import pandas as pd
import numpy as np
import os
from pathlib import Path
from sqlalchemy import create_engine

database = "group_5_2024"
user = "group_5_2024"
password = "f9JsjkRlQee4"
host = "dbcourse.cs.aalto.fi"
port = "5432"

engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}')
connection = engine.connect()

volunteer_application_df = pd.read_sql("SELECT * FROM volunteer_application", connection)
volunteer_df = pd.read_sql("SELECT * FROM volunteer", connection)
request_df = pd.read_sql("SELECT * FROM request", connection)
beneficiary_df = pd.read_sql("SELECT * FROM beneficiary", connection)
city_df = pd.read_sql("SELECT * FROM city", connection)
request_skill_df = pd.read_sql("SELECT * FROM request_skill", connection)
skill_assignment_df = pd.read_sql("SELECT * FROM skill_assignment", connection)
interest_assignment_df = pd.read_sql("SELECT * FROM interest_assignment", connection)

max_travel_readiness = 1500  
max_distance = 20000  

# Haversine formula 
def haversine(lon1, lat1, lon2, lat2):
    # Convert latitude and longitude from degrees to radians
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    # Differences in coordinates
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    # Haversine formula
    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    r = 6371  
    return c * r

# Parse geolocation
def parse_geolocation(geolocation):
    lat, lon = map(float, geolocation.split('/'))
    return lat, lon

def calculate_volunteer_range_score(volunteer_city_id, beneficiary_city_id):
    # Get geolocation for volunteer's city
    volunteer_geolocation = city_df[city_df['id'] == volunteer_city_id]['geolocation'].values[0]
    volunteer_lat, volunteer_lon = parse_geolocation(volunteer_geolocation)
    # Get geolocation for beneficiary's city
    beneficiary_geolocation = city_df[city_df['id'] == beneficiary_city_id]['geolocation'].values[0]
    beneficiary_lat, beneficiary_lon = parse_geolocation(beneficiary_geolocation)
    
    distance = haversine(volunteer_lon, volunteer_lat, beneficiary_lon, beneficiary_lat)
    range_score = 10 - (distance / max_distance) * 10
    return max(range_score, 0)  

# Define a mapping between request titles and interest names
interest_mapping = {
    "work in team needed": "WorkInATeam",
    "work with young needed": "WorkWithYoung",
    "organise activities needed": "Organizational",
    "guide and teach needed": "TrainPeople",
    "work with elderly needed": "WorkWithElderly",
    "first aid needed": "HealthCareOrFirstAid",
    "collect donations needed": "CollectDonations",
    "promote wellbeing needed": "PromoteWellbeing",
    "work in multicultural environment needed": "WorkInMulticulturalEnvironment",
    "food help needed": "FoodHelp",
    "help in crisis needed": "HelpInCrisis",
    "immigrant support needed": "ImmigrantSupport"
}

results_list = []
grouped_by_request_df = volunteer_application_df.groupby('request_id')['volunteer_id'].apply(list).reset_index()

# Iterate over each request_id
for index, row in grouped_by_request_df.iterrows():
    request_id = row['request_id']
    volunteer_ids = row['volunteer_id']
    
    # Get the title and priority value for the request
    request_title = request_df[request_df['id'] == request_id]['title'].values[0]
    priority_value = request_df[request_df['id'] == request_id]['priority_value'].values[0]
    
    priority_score = (priority_value / 5) * 10
    
    beneficiary_id = request_df[request_df['id'] == request_id]['beneficiary_id'].values[0]
    beneficiary_city_id = beneficiary_df[beneficiary_df['id'] == beneficiary_id]['city_id'].values[0]
    
    skills_needed = request_skill_df[request_skill_df['request_id'] == request_id]['skill_name'].tolist()
    total_skills_needed = len(skills_needed)
    
    # Iterate over each volunteer_id for this request_id
    for volunteer_id in volunteer_ids:
        if volunteer_id in volunteer_df['id'].values:
            
            volunteer_city_id = volunteer_df[volunteer_df['id'] == volunteer_id]['city_id'].values[0]
            travel_readiness = volunteer_df[volunteer_df['id'] == volunteer_id]['travel_readiness'].values[0]
            
            if volunteer_city_id == beneficiary_city_id:
                travel_score = 20 
            else:
                travel_score = 20 - (travel_readiness / max_travel_readiness) * 20  # Scaled score based on readiness time
            
            volunteer_skills = skill_assignment_df[skill_assignment_df['volunteer_id'] == volunteer_id]['skill_name'].tolist()
            
            skill_matching = set(skills_needed) & set(volunteer_skills)
            skill_match_count = len(skill_matching)
            skill_score = (skill_match_count / total_skills_needed) * 40 if total_skills_needed > 0 else 0
            
            volunteer_interests = interest_assignment_df[interest_assignment_df['volunteer_id'] == volunteer_id]['interest_name'].tolist()
            
            mapped_interest = interest_mapping.get(request_title.lower())
            interest_score = 0
            if mapped_interest and mapped_interest in volunteer_interests:
                interest_score = 20  
            
            range_score = calculate_volunteer_range_score(volunteer_city_id, beneficiary_city_id)
            
            total_score = skill_score + interest_score + priority_score + travel_score + range_score
            
            results_list.append({
                'request_id': request_id,
                'request_title': request_title,
                'volunteer_id': volunteer_id,
                'volunteer_city_id': volunteer_city_id,
                'beneficiary_city_id': beneficiary_city_id,
                'travel_readiness': travel_readiness,
                'travel_score': travel_score,
                'volunteer_skills': volunteer_skills,
                'skills_needed': skills_needed,
                'skill_matching': list(skill_matching),
                'skill_match_count': skill_match_count,
                'skill_score': skill_score,
                'volunteer_interests': volunteer_interests,
                'mapped_interest': mapped_interest,
                'interest_score': interest_score,
                'priority_value': priority_value,
                'priority_score': priority_score,
                'range_score': range_score,
                'total_score': total_score
            })

results_df = pd.DataFrame(results_list)

top_5_volunteers_df = results_df.groupby('request_id').apply(lambda x: x.nlargest(5, 'total_score')).reset_index(drop=True)
# Define the path to the desktop
#desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
desktop_path = str(Path(__file__).parent)
output_file_path = os.path.join(desktop_path, "top_5_volunteers_per_request.xlsx")
# Save the results to the specified path
top_5_volunteers_df.to_excel(output_file_path, index=False)
print(f"File saved to: {output_file_path}")
connection.close()
