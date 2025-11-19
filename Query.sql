######## MAIN QUERY ########
-- CURRENT DATE (THIS VARIABLE WILL BE PROVIDED AS A VARIABLE BY THE PIPELINE) OR WE CAN DEFINE IT HERE
SET @ds = '2025-04-06';
# SET @ds = CURRENT_DATE();

-- LOADING THE RESULTS IN THE TABLE AA_tables.`results_atd_mexico`
#TRUNCATE TABLE aa_tables.`results_atd_mexico`; -- TO DELETE THE TABLE BEFORE LOADING THE NEW DATA (OVERWRITING THE DATA)
INSERT INTO aa_tables.`results_atd_mexico` (
	region, territory, country_name, workflow_uuid, driver_uuid, delivery_trip_uuid, 
    courier_flow, restaurant_offered_timestamp_utc, order_final_state_timestamp_local, 
    eater_request_timestamp_local, geo_archetype, merchant_surface, pickup_distance, 
    dropoff_distance, ATD
)

-- DAYS OF THE PREVIOUS WEEK (MONDAY - SUNDAY)
WITH week_days AS(
SELECT 
	@ds AS specified_date,
	DATE_SUB(@ds, INTERVAL WEEKDAY(@ds) DAY) AS actual_week_monday,
    DATE_SUB(DATE_SUB(@ds, INTERVAL WEEKDAY(@ds) DAY), INTERVAL 7 DAY) AS previous_week_monday, -- PREVIOUS WEEK STARTING ON MONDAY
    DATE_SUB(DATE_SUB(@ds, INTERVAL WEEKDAY(@ds) DAY), INTERVAL 1 DAY) AS previous_week_sunday), -- PREVIOUS WEEK STARTING ON SUNDAY

-- DIM_CITY, CITIES_STRATEGY & EATS_DISPATCH JOIN WITH KM CALCULATION FOR THE DISTANCES
eats_dispatch_with_geo AS (
SELECT eats_dispatch.jobuuid,
       CAST(eats_dispatch.traveldistance AS DOUBLE) / 1000 AS traveldistance, -- DIVIDE BY 1000 TO GET KM
       CAST(eats_dispatch.pickupdistance AS DOUBLE) / 1000 AS pickupdistance, -- DIVIDE BY 1000 TO GET KM
       cities_stra.region,
       cities_stra.territory,
       dim_city.country_name
FROM uber_case.`delivery_matching.eats_dispatch_metrics_job_message` AS eats_dispatch
LEFT JOIN 
uber_case.`kirby_external_data.cities_strategy_region` AS cities_stra
ON eats_dispatch.cityid = cities_stra.city_id
LEFT JOIN 
uber_case.`dwh.dim_city` AS dim_city
ON cities_stra.city_id = dim_city.city_id)

-- ORDER_FINAL_STATE JOIN WITH THE REST OF THE TABLES & ATD CALCULATION
SELECT eats_dispatch_w_g.region,
	   eats_dispatch_w_g.territory,
       eats_dispatch_w_g.country_name,
	   lea_trips.workflow_uuid,
	   lea_trips.driver_uuid,
       lea_trips.delivery_trip_uuid,
       lea_trips.courier_flow,
       STR_TO_DATE(lea_trips.restaurant_offered_timestamp_utc, '%d/%m/%Y %H:%i:%s') AS restaurant_offered_timestamp_utc,
       STR_TO_DATE(lea_trips.order_final_state_timestamp_local, '%d/%m/%Y %H:%i:%s') AS order_final_state_timestamp_local,
       STR_TO_DATE(lea_trips.eater_request_timestamp_local, '%d/%m/%Y %H:%i:%s') AS eater_request_timestamp_local,
       #STR_TO_DATE(w_d.previous_week_monday, '%Y-%m-%d') AS previous_week_monday, -- LIMIT OF THE PREVIOUS WEEK
       #STR_TO_DATE(w_d.previous_week_sunday, '%Y-%m-%d') AS previous_week_sunday, -- LIMIT OF THE PREVIOUS WEEK
       lea_trips.geo_archetype,
       lea_trips.merchant_surface,
       eats_dispatch_w_g.pickupdistance AS pickup_distance,
       eats_dispatch_w_g.traveldistance AS dropoff_distance,
       #TIMESTAMPDIFF(HOUR, STR_TO_DATE(lea_trips.eater_request_timestamp_local, '%d/%m/%Y %H:%i:%s'),STR_TO_DATE(lea_trips.restaurant_offered_timestamp_utc, '%d/%m/%Y %H:%i:%s')) AS hour_converter, -- INFERENCE OF TIME ZONE CONVERSION
       ROUND(CAST(TIMESTAMPDIFF(SECOND, DATE_SUB(STR_TO_DATE(lea_trips.restaurant_offered_timestamp_utc, '%d/%m/%Y %H:%i:%s'), -- ORDER START TIME (IN UTC TIME ZONE)
       INTERVAL TIMESTAMPDIFF(HOUR, STR_TO_DATE(lea_trips.eater_request_timestamp_local, '%d/%m/%Y %H:%i:%s'),STR_TO_DATE(lea_trips.restaurant_offered_timestamp_utc, '%d/%m/%Y %H:%i:%s')) HOUR), -- TIME ZONE CONVERSION (HOURS REQUIRED TO CONVERT UTC TO LOCAL TIME ZONE)
       STR_TO_DATE(lea_trips.order_final_state_timestamp_local, '%d/%m/%Y %H:%i:%s')) AS DOUBLE)/60,2) AS ATD -- ORDER END TIME (IN LOCAL TIME ZONE)
FROM uber_case.`tmp.lea_trips_scope_atd_consolidation_v2` AS lea_trips
INNER JOIN 
eats_dispatch_with_geo AS eats_dispatch_w_g
ON lea_trips.delivery_trip_uuid = eats_dispatch_w_g.jobuuid
INNER JOIN
week_days AS w_d
ON 1=1
WHERE eats_dispatch_w_g.country_name IN ('Mexico')
AND STR_TO_DATE(lea_trips.eater_request_timestamp_local, '%d/%m/%Y %H:%i:%s')>=STR_TO_DATE(w_d.previous_week_monday, '%Y-%m-%d')
AND STR_TO_DATE(lea_trips.eater_request_timestamp_local, '%d/%m/%Y %H:%i:%s')<=STR_TO_DATE(w_d.previous_week_sunday, '%Y-%m-%d');


######## EXTRA QUERIES ########
# DESCRIBE uber_case.`tmp.lea_trips_scope_atd_consolidation_v2`;

# ALTER TABLE uber_case.`delivery_matching.eats_dispatch_metrics_job_message` MODIFY COLUMN estimated_delivery_time VARCHAR(45);

# TRUNCATE uber_case.`tmp.lea_trips_scope_atd_consolidation_v2`;

# TRUNCATE uber_case.`delivery_matching.eats_dispatch_metrics_job_message`;

# CREATE SCHEMA `aa_tables`;

# DROP TABLE IF EXISTS aa_tables.results_atd_mexico;

# TRUNCATE aa_tables.results_atd_mexico;

/*
CREATE TABLE aa_tables.results_atd_mexico (
    region VARCHAR(45),
    territory VARCHAR(45),
    country_name VARCHAR(45),
    workflow_uuid VARCHAR(45),
    driver_uuid VARCHAR(45),
    delivery_trip_uuid VARCHAR(45),
    courier_flow VARCHAR(45),
    geo_archetype VARCHAR(45),
    merchant_surface VARCHAR(45),
    restaurant_offered_timestamp_utc DATETIME,
    order_final_state_timestamp_local DATETIME,
    eater_request_timestamp_local DATETIME,
    pickup_distance DOUBLE,
    dropoff_distance DOUBLE,
    ATD DOUBLE
);*/
