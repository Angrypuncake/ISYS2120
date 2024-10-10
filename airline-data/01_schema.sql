-- SCHEMA FILE for AIRLINE DATA

DROP SCHEMA IF EXISTS airline cascade;

CREATE SCHEMA airline;

SET SCHEMA 'airline';

DROP TABLE IF EXISTS Airports;
DROP TABLE IF EXISTS Aircraft;
DROP TABLE IF EXISTS Flights;
DROP TABLE IF EXISTS Passengers;
DROP TABLE IF EXISTS Tickets;

DROP TABLE IF EXISTS Users;
DROP TABLE IF EXISTS UserRoles;


CREATE TABLE UserRoles (
    UserRoleID SERIAL PRIMARY KEY,
    RoleName TEXT,
    IsAdmin BOOLEAN NOT NULL,
    privilegeFlags INT
);

CREATE TABLE Users (
    UserID VARCHAR(10) PRIMARY KEY,  
    FirstName TEXT, 
    LastName TEXT, 
    UserRoleID INT REFERENCES UserRoles(UserRoleID) NOT NULL, 
    Password TEXT NOT NULL
);

CREATE TABLE Airports (
    AirportID INT PRIMARY KEY,
    Name VARCHAR(100),
    IATACode CHAR(3),
    City VARCHAR(100),
    Country VARCHAR(100)
);

CREATE TABLE Aircraft (
    AircraftID INT PRIMARY KEY,
    ICAOCode CHAR(4),
    AircraftRegistration VARCHAR(6),
    Name VARCHAR(100),
    Manufacturer VARCHAR(100),
    Model VARCHAR(100)
);

CREATE TABLE Flights (
    FlightID INT PRIMARY KEY,
    FlightNumber VARCHAR(10),
    DepartureAirportID INT,
    ArrivalAirportID INT,
    DepartureTime TIMESTAMP,
    ArrivalTime TIMESTAMP,
    AircraftID INT,
    FOREIGN KEY (DepartureAirportID) REFERENCES Airports(AirportID),
    FOREIGN KEY (ArrivalAirportID) REFERENCES Airports(AirportID),
    FOREIGN KEY (AircraftID) REFERENCES Aircraft(AircraftID)
);

CREATE TABLE Passengers (
    PassengerID INT PRIMARY KEY,
    FirstName VARCHAR(100),
    LastName VARCHAR(100),
    DateOfBirth DATE,
    Gender CHAR(1),
    Nationality VARCHAR(100),
    PassportNumber CHAR(8)
);

CREATE TABLE Tickets (
    TicketID INT PRIMARY KEY,
    FlightID INT,
    PassengerID INT,
    TicketNumber VARCHAR(15),
    BookingDate TIMESTAMP,
    SeatNumber VARCHAR(5),
    Class VARCHAR(10),
    Price DECIMAL(10, 2),
    FOREIGN KEY (FlightID) REFERENCES Flights(FlightID),
    FOREIGN KEY (PassengerID) REFERENCES Passengers(PassengerID)
);


INSERT INTO UserRoles(UserRoleID, RoleName, IsAdmin) VALUES (1, 'Employee', FALSE), (2, 'Database Admin', TRUE);

INSERT INTO Users(UserID, FirstName, LastName, UserRoleID, Password) VALUES ('user', 'John', 'Doe', 1, 'password'), ('admin', 'Jane', 'Doe', 2, 'admin');