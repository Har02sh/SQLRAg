PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE Contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    rank TEXT,
    phone_number TEXT,
    address TEXT
);
INSERT INTO Contacts VALUES(1,'John Doe','Air Chief Marshal','555-123-4567','123 Main St, New York, NY');
INSERT INTO Contacts VALUES(2,'Jane Smith','Admiral','555-987-6543','456 Oak Ave, Los Angeles, CA');
INSERT INTO Contacts VALUES(3,'Michael Johnson','Major','555-234-5678','789 Pine Rd, Chicago, IL');
INSERT INTO Contacts VALUES(4,'Emily Davis','Wing Commander','555-345-6789','321 Birch Ln, Houston, TX');
INSERT INTO Contacts VALUES(5,'David Martinez','Commander','555-456-7890','654 Cedar St, Phoenix, AZ');
INSERT INTO Contacts VALUES(6,'Sarah Brown','Captain','555-567-8901','987 Maple Dr, Philadelphia, PA');
INSERT INTO Contacts VALUES(7,'James Wilson','Squadron Leader','555-678-9012','741 Walnut Blvd, San Antonio, TX');
INSERT INTO Contacts VALUES(8,'Olivia Taylor','Lieutenant Colonel','555-789-0123','852 Spruce Ct, San Diego, CA');
INSERT INTO Contacts VALUES(9,'Daniel White','Flight Lieutenant','555-890-1234','963 Aspen Pl, Dallas, TX');
INSERT INTO Contacts VALUES(10,'Sophia Harris','Sub-Lieutenant','555-901-2345','159 Redwood Cir, San Jose, CA');
INSERT INTO Contacts VALUES(11,'Robert Anderson','Naik','555-012-3456','753 Magnolia Ave, Austin, TX');
INSERT INTO Contacts VALUES(12,'Isabella Thomas','Leading Aircraftman','555-123-4568','357 Elm St, Jacksonville, FL');
INSERT INTO Contacts VALUES(13,'William Garcia','Petty Officer','555-234-5679','258 Cherry Ln, Columbus, OH');
INSERT INTO Contacts VALUES(14,'Mia Martinez','Sepoy','555-345-6780','159 Ash Dr, Indianapolis, IN');
INSERT INTO Contacts VALUES(15,'Benjamin Rodriguez','Aircraftman','555-456-7891','951 Sycamore St, Charlotte, NC');
INSERT INTO Contacts VALUES(16,'Charlotte Lewis','Seaman I','555-567-8902','753 Poplar Blvd, Seattle, WA');
INSERT INTO Contacts VALUES(17,'Alexander Young','General','555-678-9013','357 Willow Pl, Denver, CO');
INSERT INTO Contacts VALUES(18,'Amelia King','Air Chief Marshal','555-789-0124','159 Fir Ave, Washington, DC');
INSERT INTO Contacts VALUES(19,'Lucas Scott','Admiral','555-890-1235','258 Dogwood Ln, Boston, MA');
INSERT INTO Contacts VALUES(20,'Emma Hall','Major','555-901-2346','357 Hickory Ct, Nashville, TN');
INSERT INTO sqlite_sequence VALUES('Contacts',20);
COMMIT;
