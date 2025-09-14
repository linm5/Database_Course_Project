
DROP TABLE IF EXISTS city, volunteer, volunteer_range, skill, skill_assignment, interest, interest_assignment, beneficiary, request, request_skill, request_location, volunteer_application CASCADE;


CREATE TABLE city(
  name TEXT,
  id INT PRIMARY KEY,
  geolocation TEXT
  );


CREATE TABLE volunteer(
  id TEXT PRIMARY KEY,
  name TEXT,
  birthdate DATE,
  city_id INT,
  email TEXT,
  address TEXT,
  travel_readiness INT
  );


CREATE TABLE volunteer_range(
  volunteer_id TEXT REFERENCES volunteer,
  city_id INT REFERENCES city
  );


CREATE TABLE skill(
name TEXT PRIMARY KEY,
description TEXT
);

CREATE TABLE skill_assignment(
  volunteer_id text REFERENCES volunteer,
  skill_name TEXT REFERENCES skill
);

CREATE TABLE interest(
  name TEXT PRIMARY KEY
);


CREATE TABLE interest_assignment(
  interest_name TEXT REFERENCES interest,
  volunteer_id TEXT REFERENCES volunteer
);


CREATE TABLE beneficiary(
  id INT PRIMARY KEY,
  name TEXT,
  address TEXT,
  city_id INT
);



CREATE TABLE request(
  id INT PRIMARY KEY,
  title TEXT,
  beneficiary_id INT,
  number_of_volunteers INT,
  priority_value INT,
  start_date DATE,
  end_date DATE,
  register_by_date DATE
);



CREATE TABLE request_skill(
  request_id INT REFERENCES request,
  skill_name TEXT REFERENCES skill,
  min_need INT,
  value INT
);


CREATE TABLE request_location(
  request_id INT REFERENCES request,
  city_id INT REFERENCES city
);


CREATE TABLE volunteer_application(
  id INT PRIMARY KEY,
  request_id INT REFERENCES request,
  volunteer_id TEXT REFERENCES volunteer,
  modified DATE,
  is_valid BOOLEAN
);



