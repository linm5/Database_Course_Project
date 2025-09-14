--A
--1
SELECT
  REPLACE(title, ' needed', '') AS request,
  start_date AS "start date",
  end_date AS "end date"
FROM
  request;

--2
SELECT
  request_id,
  volunteer_id,
  SUM(matching_skills) AS m
FROM
  (
    SELECT
      rs.request_id AS request_id,
      sa.volunteer_id AS volunteer_id,
      COUNT(DISTINCT sa.skill_name) AS matching_skills
    FROM
      skill_assignment sa
      JOIN request_skill rs
        ON rs.skill_name = sa.skill_name
      JOIN volunteer_application va
        ON rs.request_id = va.request_id AND va.volunteer_id = sa.volunteer_id
    WHERE
      va.is_valid
    GROUP BY
      rs.request_id,
      sa.volunteer_id
    UNION
    SELECT
      r.id AS request_id,
      va.volunteer_id AS volunteer_id,
      0 AS matching_skills
    FROM
      request r
      JOIN volunteer_application va
        ON r.id = va.request_id
    WHERE
      va.is_valid
  ) rv
GROUP BY
  request_id,
  volunteer_id
ORDER BY
  request_id,
  m DESC,
  volunteer_id;

--3
SELECT
  rs.request_id,
  rs.skill_name,
  rs.min_need - COUNT(va.volunteer_id) AS missing_volunteers
FROM
  request_skill rs
  JOIN volunteer_application va
    ON rs.request_id = va.request_id
  JOIN skill_assignment sa
    ON va.volunteer_id = sa.volunteer_id AND rs.skill_name = sa.skill_name
WHERE
  va.is_valid
GROUP BY
  rs.request_id,
  rs.skill_name,
  rs.min_need
HAVING
  rs.min_need - COUNT(va.volunteer_id) > 0
ORDER BY
  rs.request_id,
  rs.skill_name;

--4
SELECT
  id,
  beneficiary_id,
  priority_value,
  register_by_date
FROM
  request r
ORDER BY
  r.priority_value DESC,
  r.register_by_date ASC;

--5
SELECT
  rv.volunteer_id,
  rv.request_id,
  SUM(matching_skills) AS m
FROM
  (
    SELECT DISTINCT
      rv.volunteer_id,
      rv.request_id,
      rv.matching_skills
    FROM
      ((
        SELECT
          rs.request_id AS request_id,
          sa.volunteer_id AS volunteer_id,
          COUNT(DISTINCT sa.skill_name) AS matching_skills
        FROM
          skill_assignment sa
          JOIN request_skill rs
            ON rs.skill_name = sa.skill_name
        GROUP BY
          rs.request_id, sa.volunteer_id
        HAVING
          COUNT(DISTINCT sa.skill_name) >= 2 )
        UNION
        SELECT
          s.request_id AS request_id,
          v.id AS volunteer_id,
          0 AS matching_skills
        FROM
          volunteer v,
          (
            SELECT
              r.id AS request_id
            FROM
              request r
            EXCEPT
            SELECT
              rs.request_id AS request_id
            FROM
              request_skill rs
          ) s
      ) rv,
      volunteer_range vr,
      request_location rl
    WHERE
      rv.request_id = rl.request_id
      AND vr.volunteer_id = rv.volunteer_id
      AND rl.city_id = vr.city_id
  ) rv
GROUP BY
  rv.request_id,
  rv.volunteer_id
ORDER BY
  rv.volunteer_id,
  m DESC,
  rv.request_id;

--6
SELECT
  v.id AS volunteer_id,
  v.name AS volunteer_name,
  r.id AS request_id,
  r.title AS request_title
FROM
  volunteer v
  JOIN interest_assignment ia
    ON v.id = ia.volunteer_id
  JOIN request r
    ON replace(r.title, ' ', '') ILIKE '%%' || ia.interest_name || '%%'
WHERE
  r.register_by_date > CURRENT_DATE;

--7
SELECT
  va.request_id,
  v.name,
  v.email
FROM
  volunteer_application va
  JOIN volunteer v
    ON va.volunteer_id = v.id
  JOIN request_location rl
    ON va.request_id = rl.request_id
WHERE
  NOT EXISTS
  (
    SELECT
      1
    FROM
      volunteer_range vr
    WHERE
      vr.volunteer_id = v.id
      AND vr.city_id = rl.city_id
  )
ORDER BY
  travel_readiness DESC;

--8
SELECT
  rs.skill_name,
  AVG(r.priority_value) AS average_value
FROM
  request_skill rs
  JOIN request r
    ON r.id = rs.request_id
GROUP BY
  rs.skill_name
ORDER BY
  average_value DESC;

--9
SELECT
  t1.city_name,
  volunteer_supply,
  volunteer_demand
FROM (
  SELECT
    c."name" AS city_name,
    COUNT(DISTINCT vr.volunteer_id) AS volunteer_supply
  FROM
    city c
    JOIN volunteer_range vr
      ON vr.city_id = c.id
  GROUP BY
    c.id
  ) t1
  JOIN (
    SELECT
      c."name" AS city_name,
      SUM(r.number_of_volunteers::FLOAT / lc.COUNT) AS volunteer_demand
    FROM
      city c
      JOIN request_location rl
        ON rl.city_id = c.id
      JOIN request r
        ON r.id = rl.request_id
      JOIN (
        SELECT
          rl.request_id,
          COUNT(rl.city_id)
        FROM
          request_location rl
        GROUP BY
          rl.request_id
      )
      lc
      ON lc.request_id = rl.request_id
    GROUP BY
      c.id
  ) t2
    ON t1.city_name = t2.city_name
ORDER BY
  volunteer_demand / volunteer_supply DESC;

--10
SELECT
  c."name",
  SUM(r.priority_value) AS total_priority_value
FROM
  city c
  JOIN request_location rl
    ON rl.city_id = c.id
  JOIN request r
    ON r.id = rl.request_id
GROUP BY
  c.id
ORDER BY
  total_priority_value DESC;

--11
SELECT
  r.id AS request_id,
  va.id AS application_id
FROM
  request r
  JOIN volunteer_application va
    ON va.request_id = r.id
WHERE
  va.is_valid AND va.modified <= r.register_by_date
ORDER BY
  request_id,
  application_id;

--12
SELECT
  c."name",
  ia.interest_name,
  COUNT(DISTINCT v.id)
FROM
  city c
  JOIN volunteer_range vr
    ON vr.city_id = c.id
  JOIN volunteer v
    ON v.id = vr.volunteer_id
  JOIN interest_assignment ia
    ON ia.volunteer_id = v.id
GROUP BY
  c.id,
  ia.interest_name;