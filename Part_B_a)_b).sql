--B
--a1
create or replace view beneficiary_spread as
with ageCalculation as (
       select v.id as volunteer_id,
              v.birthdate,
              date_part('year', AGE(v.birthdate)) as age
       from volunteer v
),
applicationStats as (
       select r.beneficiary_id,
              count(va.volunteer_id) as number_of_volunteers_that_applied,
              AVG(ac.age) as avg_age_applied
       from request r
       left join volunteer_application va on r.id = va.request_id
       left join ageCalculation ac on va.volunteer_id = ac.volunteer_id
       group by r.beneficiary_id
),
requestStats as (
       select beneficiary_id,
              AVG(number_of_volunteers) as avg_volunteers_needed
       from request
       group by beneficiary_id
)
select b.id as beneficiary_id,
       b.name as beneficiary,
       coalesce(app_stats.number_of_volunteers_that_applied, 0) as avg_num_volunteers_applied,
       coalesce(app_stats.avg_age_applied, 0) as avg_age_applied,
       coalesce(req_stats.avg_volunteers_needed, 0) as avg_volunteers_needed
from beneficiary b
left join applicationStats app_stats on b.id = app_stats.beneficiary_id
left join requestStats req_stats on b.id = req_stats.beneficiary_id;

--Test view
SELECT * from beneficiary_spread;

--a2
--3rd view option.

create or replace view volunteer_skill_details as
select 
  v.id as volunteer_id,
  v.name as volunteer_name,
  v.email,
  v.city_id,
  c.name as city_name,
  string_agg(s.name, ', ') as skills,
  count(s.name) as skill_count
from 
  volunteer v
left join 
  skill_assignment sa on v.id = sa.volunteer_id
left join 
  skill s on sa.skill_name = s.name
left join 
  city c on v.city_id = c.id
group by 
  v.id, v.name, v.email, v.city_id, c.name
order by 
  v.name;

--Test view
SELECT * from volunteer_skill_details;

--b1
create or replace function finnish_id_checker(volunteer_id TEXT)
returns boolean as $$
declare birth_date INT;
        character_in_the_middle CHAR;
        individual_string TEXT;
        Control_character CHAR;
        remainder INT;
        expected_control_char CHAR;
        coontrol_chars TEXT = '0123456789ABCDEFHJKLMNPRSTUVWXY';
begin
	if length(volunteer_id) != 11 then
       return false;
    end if;

birth_date = SUBSTRING(volunteer_id from 1 for 6);
character_in_the_middle = SUBSTRING(volunteer_id from 7 for 1);
individual_string = SUBSTRING(volunteer_id FROM 8 FOR 3);
Control_character = SUBSTRING(volunteer_id FROM 11 FOR 1);
if character_in_the_middle not in ('+', '-', 'A', 'B', 'C', 'D', 'E', 'F', 'X', 'Y', 'W', 'V', 'U') then
       return false;
end if;
remainder = (birth_date::int * 1000 + individual_string::int) % 31;
expected_control_char = SUBSTRING(coontrol_chars from remainder+1 for 1);
if
  Control_character != expected_control_char then
  return false;
end if;
return true;
end;
$$ language plpgsql;

--constraint
ALTER TABLE volunteer
ADD CONSTRAINT valid_finnish_id
CHECK (finnish_id_checker(id));

--B trigger 2
create or replace view unskilled_volunteers_count as
select count(*) as count
from volunteer v
where not exists (
  select 1
  from skill_assignment sa
  where sa.volunteer_id = v.id
);

create or replace function update_number_of_volunteers()
returns trigger as $$
declare
  total_skilled_volunteers int;
  total_unskilled_volunteers int;
begin
  select coalesce(sum(min_need), 0)
  into total_skilled_volunteers
  from request_skill
  where request_id = new.request_id;

  select count
  into total_unskilled_volunteers
  from unskilled_volunteers_count;

  update request
  set number_of_volunteers = total_unskilled_volunteers + total_skilled_volunteers
  where id = new.request_id;

  return new;
end;
$$ language plpgsql;

drop trigger if exists trg_update_number_of_volunteers on request_skill;

create trigger trg_update_number_of_volunteers
after insert or update of min_need on request_skill
for each row
execute function update_number_of_volunteers();
