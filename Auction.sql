CREATE DATABASE  IF NOT EXISTS `Auction`;
USE `Auction`;

DROP TABLE IF EXISTS `Seller`;

CREATE TABLE Seller
(
    SellerID      INT                 NOT NULL AUTO_INCREMENT PRIMARY KEY,
    FirstName     VARCHAR(50)         NOT NULL,
    LastName      VARCHAR(50)         NOT NULL,
    StreetAddress VARCHAR(100)        NOT NULL,
    City          VARCHAR(50)         NOT NULL,
    State         VARCHAR(50)         NOT NULL,
    ZipCode       VARCHAR(20)         NOT NULL,
    PhoneNumber   VARCHAR(20)         NOT NULL,
    EmailID       VARCHAR(100) UNIQUE NOT NULL,
    Password      VARCHAR(50)         NOT NULL
);

DROP TABLE IF EXISTS `Bidder`;

CREATE TABLE Bidder
(
    BidderID      INT                 NOT NULL AUTO_INCREMENT PRIMARY KEY,
    FirstName     VARCHAR(50)         NOT NULL,
    LastName      VARCHAR(50)         NOT NULL,
    StreetAddress VARCHAR(100)        NOT NULL,
    City          VARCHAR(50)         NOT NULL,
    State         VARCHAR(50)         NOT NULL,
    ZipCode       VARCHAR(20)         NOT NULL,
    PhoneNumber   VARCHAR(20)         NOT NULL,
    EmailID       VARCHAR(100) UNIQUE NOT NULL,
    Password      VARCHAR(50)         NOT NULL
);

DROP TABLE IF EXISTS `Users`;

CREATE TABLE Users
(
    EmailID  VARCHAR(100) UNIQUE NOT NULL,
    Password VARCHAR(50)         NOT NULL
);

DROP TABLE IF EXISTS `ItemType`;

CREATE TABLE ItemType
(
    ItemTypeID  INT         NOT NULL AUTO_INCREMENT PRIMARY KEY,
    Name        VARCHAR(50) NOT NULL,
    Description TEXT
);

DROP TABLE IF EXISTS `Item`;

CREATE TABLE Item
(
    ItemID      INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
    Name        VARCHAR(100) NOT NULL,
    Description TEXT,
    ItemTypeID  INT          NOT NULL,
    SellerID    INT          NOT NULL,
    Sold        BOOLEAN      NOT NULL,
    FOREIGN KEY (ItemTypeID) REFERENCES ItemType (ItemTypeID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (SellerID) REFERENCES Seller (SellerID) ON DELETE CASCADE ON UPDATE CASCADE
);

DROP TABLE IF EXISTS `Bid`;

CREATE TABLE Bid
(
    BidID     INT            NOT NULL AUTO_INCREMENT PRIMARY KEY,
    BidAmount DECIMAL(10, 2) NOT NULL,
    ItemID    INT            NOT NULL,
    BidderID  INT            NOT NULL,
    FOREIGN KEY (ItemID) REFERENCES Item (ItemID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (BidderID) REFERENCES Bidder (BidderID) ON DELETE CASCADE ON UPDATE CASCADE
);

DROP TABLE IF EXISTS `WinningBid`;

CREATE TABLE WinningBid
(
    ItemID         INT NOT NULL,
    WinnerBidderID INT NOT NULL,
    HighestBidID   INT NOT NULL,
    FOREIGN KEY (ItemID) REFERENCES Item (ItemID),
    FOREIGN KEY (WinnerBidderID) REFERENCES Bidder (BidderID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (HighestBidID) REFERENCES Bid (BidID) ON DELETE CASCADE ON UPDATE CASCADE
);

DROP TABLE IF EXISTS `CreditCard`;

CREATE TABLE CreditCard
(
    CreditCardNumber VARCHAR(20) PRIMARY KEY,
    ExpiryDate       DATE         NOT NULL,
    NameOnCard       VARCHAR(100) NOT NULL,
    CardType         VARCHAR(50)  NOT NULL,
    BidderID         INT          NOT NULL,
    FOREIGN KEY (BidderID) REFERENCES Bidder (BidderID) ON DELETE CASCADE ON UPDATE CASCADE
);

DROP TABLE IF EXISTS `Transaction`;

CREATE TABLE Transaction
(
    TransactionID    INT PRIMARY KEY AUTO_INCREMENT,
    Amount           DECIMAL(10, 2),
    BidderID         INT,
    SellerID         INT,
    ItemID           INT,
    CreditCardNumber VARCHAR(20),
    FOREIGN KEY (BidderID) REFERENCES Bidder (BidderID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (SellerID) REFERENCES Seller (SellerID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (ItemID) REFERENCES Item (ItemID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (CreditCardNumber) REFERENCES CreditCard (CreditCardNumber)
);

DROP TABLE IF EXISTS `Buys`;

CREATE TABLE Buys
(
    ItemID   INT,
    BidderID INT,
    PRIMARY KEY (ItemID, BidderID),
    FOREIGN KEY (ItemID) REFERENCES Item (ItemID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (BidderID) REFERENCES Bidder (BidderID) ON DELETE CASCADE ON UPDATE CASCADE
);

DROP TABLE IF EXISTS `Sells`;

CREATE TABLE Sells
(
    SellerID INT,
    ItemID   INT,
    PRIMARY KEY (SellerID, ItemID),
    FOREIGN KEY (SellerID) REFERENCES Seller (SellerID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (ItemID) REFERENCES Item (ItemID) ON DELETE CASCADE ON UPDATE CASCADE
);


DELIMITER //
CREATE PROCEDURE get_seller_for_email(IN email_id VARCHAR (100))
BEGIN
SELECT SellerID, FirstName, LastName
FROM Seller
WHERE EmailID = email_id;
END
//

DELIMITER ;

DELIMITER //
CREATE PROCEDURE get_bidder_for_email(IN email_id VARCHAR (100))
BEGIN
SELECT BidderID, FirstName, LastName
FROM Bidder
WHERE EmailID = email_id;
END
//

DELIMITER ;

DELIMITER //
CREATE PROCEDURE get_user(IN email_id VARCHAR (100), IN pass_word VARCHAR (50))
BEGIN
SELECT *
FROM users
WHERE EmailID = email_id
  AND Password = pass_word;
END
//

DELIMITER ;

DELIMITER //
CREATE PROCEDURE check_user_exists(IN email_id VARCHAR (100))
BEGIN
SELECT *
FROM users
WHERE EmailID = email_id;
END
//

DELIMITER ;

DELIMITER //
CREATE PROCEDURE add_seller(IN first_name VARCHAR (50), IN last_name VARCHAR (50),
                            IN street_address VARCHAR (100), IN city VARCHAR (50),
                            IN state VARCHAR (50), IN zip_code INT, IN phone_number INT, IN email_id VARCHAR (100),
                            IN pass_word VARCHAR (50))
BEGIN
INSERT INTO seller (FirstName, LastName, StreetAddress, City, State, ZipCode, PhoneNumber, EmailID, Password)
VALUES (first_name, last_name, street_address, city, state, zip_code, phone_number, email_id, pass_word);
INSERT INTO users (EmailID, Password)
VALUES (email_id, pass_word);

END
//


DELIMITER //
CREATE PROCEDURE add_bidder(IN first_name VARCHAR (50), IN last_name VARCHAR (50),
                            IN street_address VARCHAR (100), IN city VARCHAR (50),
                            IN state VARCHAR (50), IN zip_code INT, IN phone_number INT, IN email_id VARCHAR (100),
                            IN pass_word VARCHAR (50))
BEGIN
INSERT INTO bidder (FirstName, LastName, StreetAddress, City, State, ZipCode, PhoneNumber, EmailID, Password)
VALUES (first_name, last_name, street_address, city, state, zip_code, phone_number, email_id, pass_word);
INSERT INTO users (EmailID, Password)
VALUES (email_id, pass_word);

END
//

DELIMITER ;

DELIMITER //
CREATE PROCEDURE get_items()
BEGIN
SELECT ItemID, Name
FROM Item
WHERE Sold = 0;
END
//

DELIMITER ;

DELIMITER //
CREATE PROCEDURE get_items_all()
BEGIN
SELECT i.ItemID, i.Name, i.Description, it.Name, i.SellerID
FROM Item i
JOIN ItemType it
ON i.ItemTypeID =it.ItemTypeID
WHERE Sold = 0;
END
//

DELIMITER ;

DELIMITER //
CREATE PROCEDURE seller_user_join()
BEGIN
SELECT SellerID
FROM Seller
         JOIN Users ON Users.EmailID = Seller.EmailID;
END
//

DELIMITER ;

DELIMITER //
CREATE PROCEDURE bidder_user_join()
BEGIN
SELECT BidderID
FROM Bidder
         JOIN Users ON Users.EmailID = Bidder.EmailID;
END
//

DELIMITER ;

DELIMITER //
CREATE PROCEDURE item_seller()
BEGIN
SELECT item.ItemID, item.Name
FROM Item
         JOIN seller
         JOIN sells
WHERE sells.SellerID = seller.SellerID
  AND sells.ItemID = item.ItemID
  AND item.sold = 0;

END
//

DELIMITER ;

DELIMITER //
CREATE PROCEDURE get_highest_bid(IN item_id INT)
BEGIN
SELECT get_highest_bid_func(item_id);
END
//

DELIMITER ;

DELIMITER //

CREATE FUNCTION get_highest_bid_func(item_id INT) RETURNS DECIMAL(10, 2) DETERMINISTIC
BEGIN
    DECLARE highest_bid DECIMAL(10, 2);

    SELECT MAX(BidAmount) INTO highest_bid
    FROM Bid
    WHERE ItemID = item_id;

    RETURN highest_bid;
END
//

DELIMITER ;

DELIMITER //
CREATE PROCEDURE set_item_to_sold(IN item_id INT)
BEGIN
UPDATE Item
SET Sold = 1
WHERE ItemID = item_id;

END
//

DELIMITER ;

DELIMITER //
CREATE PROCEDURE get_highest_bid_id(IN item_id INT)
BEGIN
SELECT BidID
FROM Bid
WHERE ItemID = item_id
ORDER BY BidAmount DESC LIMIT 1;
END
//

DELIMITER ;


DELIMITER //
CREATE PROCEDURE get_highest_bidder_id_query(IN bid_id INT)
BEGIN
SELECT BidderID
FROM Bid
WHERE BidID = bid_id;

END
//

DELIMITER ;

DELIMITER //
CREATE PROCEDURE insert_winning_bid(IN item_id INT, IN bid_id INT, IN highest_bid_id INT)
BEGIN
INSERT INTO WinningBid (ItemID, WinnerBidderID, HighestBidID)
VALUES (item_id, bid_id, highest_bid_id);
END
//

DELIMITER ;

DELIMITER //
CREATE PROCEDURE insert_bid(IN bid_amt DECIMAL (10, 2), IN item_id INT, IN bidder_id INT)
BEGIN
INSERT INTO Bid (BidAmount, ItemID, BidderID)
VALUES (bid_amt, item_id, bidder_id);
END
//

DELIMITER ;

DELIMITER //
CREATE PROCEDURE join_bid_bidder(IN seller_id INT)
BEGIN
SELECT item.ItemID, item.Name, bid.BidAmount, concat(bidder.FirstName, ' ', bidder.LastName) AS 'Bidder Name'
FROM item
         JOIN bid ON (item.ItemID = bid.ItemID )
         JOIN bidder ON (bid.BidderID = bidder.BidderID)
         WHERE item.SellerID = seller_id;
END
//

DELIMITER ;

DELIMITER //
CREATE PROCEDURE get_item_types()
BEGIN
SELECT ItemTypeID, Name
FROM ItemType;
END
//

DELIMITER ;

DELIMITER //
CREATE PROCEDURE insert_item_type(IN name VARCHAR (50), IN description TEXT)
BEGIN
INSERT INTO ItemType (Name, Description)
VALUES (name, description);
END
//

DELIMITER ;

DELIMITER //
CREATE PROCEDURE view_bid()
BEGIN
SELECT SellerID
FROM Seller
         JOIN Users ON Users.EmailID = Seller.EmailID;
END
//

DELIMITER ;

DELIMITER //
CREATE PROCEDURE insert_item(IN name VARCHAR (50), IN description TEXT,
                             IN item_type_id INT, IN seller_id INT, IN sold BOOLEAN)
BEGIN
INSERT INTO Item (Name, Description, ItemTypeID, SellerID, Sold)
VALUES (name, description, item_type_id, seller_id, sold);
END
//

DELIMITER ;

DELIMITER //
CREATE PROCEDURE insert_into_sells(IN seller_id INT, IN item_id INT)
BEGIN
INSERT INTO Sells (SellerID, ItemID)
VALUES (seller_id, item_id);
END
//

DELIMITER ;

DELIMITER //
CREATE PROCEDURE get_last_insert_id()
BEGIN
SELECT LAST_INSERT_ID();
END //

DELIMITER ;

DELIMITER //
CREATE PROCEDURE get_seller_details(IN seller_id INT)
BEGIN
SELECT FirstName, LastName, EmailID FROM Seller WHERE SellerID = seller_id;
END //

DELIMITER ;

DELIMITER //
CREATE PROCEDURE get_winning_items(IN bidder_id INT)
BEGIN

SELECT wb.ItemID, i.Name, i.Description, i.SellerID, b.BidAmount 
FROM WinningBid wb 
JOIN Item i ON wb.ItemID = i.ItemID 
JOIN Bid b ON wb.HighestBidID = b.BidID 
WHERE wb.WinnerBidderID = bidder_id 
AND NOT EXISTS (
SELECT 1 FROM Buys 
WHERE Buys.ItemID = wb.ItemID 
AND Buys.BidderID = bidder_id);

END //

DELIMITER ;

DELIMITER //
CREATE PROCEDURE fetch_card_and_bidder(IN bidder_id INT)
BEGIN
SELECT CreditCardNumber, NameOnCard FROM CreditCard WHERE BidderID = bidder_id;
END //

DELIMITER ;

DELIMITER //
CREATE PROCEDURE fetch_details_for_transaction(IN bidder_id INT, IN ItemID INT)
BEGIN
SELECT b.BidAmount, i.ItemID, i.SellerID FROM Bid b JOIN Item i ON b.ItemID = i.ItemID WHERE b.BidderID = bidder_id AND b.ItemID = ItemID;
END //

DELIMITER ;

DELIMITER //
CREATE PROCEDURE insert_into_transaction(IN bid DECIMAL(10, 2),IN bidder_id INT,
IN seller_id INT, IN item_id INT, IN card_no VARCHAR(20))
BEGIN
INSERT INTO Transaction (Amount, BidderID, SellerID, ItemID, CreditCardNumber) VALUES (bid, bidder_id, seller_id, item_id, card_no);
END //

DELIMITER ;

DELIMITER //
CREATE PROCEDURE insert_into_buys(IN item_id INT,IN bidder_id INT)
BEGIN
INSERT INTO Buys (ItemID, BidderID) VALUES (item_id, bidder_id);
END //

DELIMITER ;

DELIMITER //
CREATE PROCEDURE insert_new_credit_card(IN card_no VARCHAR(20),IN expiry_date DATE,
IN name_on_card VARCHAR(100),
IN card_type VARCHAR(50),IN bidder_id INT)
BEGIN
INSERT INTO CreditCard (CreditCardNumber, ExpiryDate, NameOnCard, CardType, BidderID) VALUES (card_no, expiry_date, name_on_card,card_type,bidder_id);
END //

DELIMITER ;

DELIMITER //
CREATE PROCEDURE delete_credit_card(IN card_no VARCHAR(20))
BEGIN
DELETE FROM CreditCard WHERE CreditCardNumber = card_no;
END //

DELIMITER ;

DELIMITER //
CREATE PROCEDURE get_purchase_data(IN bidder_id INT)
BEGIN
SELECT Item.Name, Bid.BidAmount
FROM Buys
INNER JOIN Item ON Buys.ItemID = Item.ItemID
INNER JOIN WinningBid ON Item.ItemID = WinningBid.ItemID
INNER JOIN Bid ON WinningBid.HighestBidID = Bid.BidID
WHERE Buys.BidderID = bidder_id;
END //

DELIMITER ;

DELIMITER //
CREATE TRIGGER check_credit_card_expiry
BEFORE INSERT ON `CreditCard`
FOR EACH ROW
BEGIN
    IF NEW.ExpiryDate < CURDATE() THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid credit card expiry date';
    END IF;
END;
//
DELIMITER ;