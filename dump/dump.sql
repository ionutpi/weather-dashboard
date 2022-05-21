USE dash;

CREATE TABLE weather (
   created TIMESTAMP,
   observed TIMESTAMP,
   parameterId VARCHAR(100),
   stationId VARCHAR(10),
   value FLOAT
);