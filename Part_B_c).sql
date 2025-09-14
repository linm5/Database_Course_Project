--B
--c1
--Create Procedure
CREATE OR REPLACE PROCEDURE fillRequest(req request) AS $$
DECLARE
    going BOOLEAN = 1;
    is_accepted BOOLEAN = 1;
    volunteerNum integer = 0;
	req_skill RECORD;
	vol_app RECORD;
BEGIN
FOR req_skill IN
    SELECT *
    FROM request_skill AS rs
    WHERE rs.request_id = req.id
    ORDER BY rs.value DESC
LOOP
    FOR vol_app IN
        SELECT *
        FROM volunteer_application va
        JOIN skill_assignment sa ON sa.skill_name = req_skill.skill_name
        JOIN volunteer_range vr ON vr.volunteer_id = va.volunteer_id
        JOIN request_location rl ON rl.request_id = va.request_id
        WHERE req.id=va.request_id AND va.is_valid AND sa.volunteer_id = va.volunteer_id AND rl.city_id = vr.city_id
    LOOP
        IF EXISTS (SELECT 1 FROM skill_assignment as sa WHERE sa.volunteer_id = vol_app.volunteer_id
                   AND req_skill.skill_name = sa.skill_name
                   AND NOT EXISTS (SELECT 1 FROM volunteer_assignment WHERE volunteer_id = vol_app.volunteer_id)) THEN
            INSERT INTO volunteer_assignment (request_id, volunteer_id) VALUES (req.id, vol_app.volunteer_id);
            volunteerNum := volunteerNum + 1;
        END IF;
        IF volunteerNum >= req_skill.min_need THEN
            EXIT;
        END IF;
 	END LOOP;
    IF req.register_by_date < CURRENT_DATE AND volunteerNum < req_skill.min_need THEN
        ROLLBACK;
    END IF;
END LOOP;
COMMIT;
END;
$$LANGUAGE plpgsql;

--Reset assignment
DROP TABLE IF EXISTS volunteer_assignment;
CREATE TABLE volunteer_assignment(
  volunteer_id text REFERENCES volunteer,
  request_id INT REFERENCES request
);

--Run the transaction
DO $$
DECLARE
	req request;
BEGIN
	FOR req IN
    	SELECT *
    	FROM request r
	LOOP
		CALL fillrequest(req);
	END LOOP;
	COMMIT;
END;
$$ language plpgsql;

--Sneakpeak
SELECT * FROM volunteer_assignment;

--c2
--Create Procedure
CREATE OR REPLACE PROCEDURE remove_outdated_application(req request) AS $$
DECLARE
    going BOOLEAN = 1;
    is_accepted BOOLEAN = 1;
    volunteerNum integer = 0;
	vol_app RECORD;
BEGIN
    FOR vol_app IN
        SELECT *
        FROM volunteer_application va
        WHERE req.id = va.request_id
    LOOP
        IF req.register_by_date < CURRENT_DATE - INTERVAL '1 years' THEN
            DELETE FROM volunteer_application WHERE id = vol_app.id;
        ELSE
            volunteerNum := volunteerNum + 1;
        END IF;
    END LOOP;

    IF volunteerNum < req.number_of_volunteers THEN
        ROLLBACK;
    END IF;
COMMIT;
END;
$$LANGUAGE plpgsql;

--Run the transaction
DO $$
DECLARE
	req request;
BEGIN
	FOR req IN
    	SELECT *
    	FROM request r
	LOOP
		CALL remove_outdated_application(req);
	END LOOP;
	COMMIT;
END;
$$ language plpgsql;