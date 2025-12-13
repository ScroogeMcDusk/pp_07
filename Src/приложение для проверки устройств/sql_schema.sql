/* Example schema for the four tables */
CREATE TABLE Девайсы (
    DeviceID INT IDENTITY(1,1) PRIMARY KEY,
    Name NVARCHAR(200) NOT NULL,
    SerialNumber NVARCHAR(200),
    Model NVARCHAR(200),
    CreatedAt DATETIME DEFAULT GETDATE()
);

CREATE TABLE Проверка (
    InspectionID INT IDENTITY(1,1) PRIMARY KEY,
    DeviceID INT NOT NULL FOREIGN KEY REFERENCES Devices(DeviceID),
    Inspector NVARCHAR(200),
    InspectionDate DATETIME DEFAULT GETDATE(),
    Result NVARCHAR(50)
);

CREATE TABLE Дефекты (
    DefectID INT IDENTITY(1,1) PRIMARY KEY,
    InspectionID INT NOT NULL FOREIGN KEY REFERENCES Inspections(InspectionID),
    DefectType NVARCHAR(200),
    Description NVARCHAR(MAX)
);

CREATE TABLE Пользователи (
    UserID INT IDENTITY(1,1) PRIMARY KEY,
    Username NVARCHAR(200) NOT NULL,
    FullName NVARCHAR(200),
    Role NVARCHAR(100)
);
