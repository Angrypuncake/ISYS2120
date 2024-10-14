SELECT * FROM Aircraft;

SELECT * FROM Aircraft
WHERE AircraftID = :aircraftID;

INSERT INTO Aircraft (AircraftID, ICAOCode, AircraftRegistration, Name, Manufacturer, Model)
VALUES (:aircraftID, :ICAOCode, :aircraftRegistration, :name, :manufacturer, :model);

UPDATE Aircraft
SET ICAOCode = :ICAOCode,
    AircraftRegistration = :aircraftRegistration,
    Name = :name,
    Manufacturer = :manufacturer,
    Model = :model
WHERE AircraftID = :aircraftID;


DELETE FROM Aircraft
WHERE AircraftID = :aircraftID;

