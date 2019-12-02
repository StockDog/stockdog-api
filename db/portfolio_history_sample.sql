-- For this to work, it must be ran right after init.sql
USE StockDog;

INSERT INTO User(firstName, lastName, email ,password, token) 
    VALUES("John", "Doe", "jd@email.com", "Password123", "123456789");

INSERT INTO League(name, start, end, startPos, inviteCode, ownerId)
    VALUES("Sample", NOW(), NOW(), 3000, 'abc123', 1);

INSERT INTO Portfolio(buyPower, name, userId, leagueId) 
    VALUES(3000, "JohnD", 1, 1);

INSERT INTO PortfolioItem(shareCount, avgCost, portfolioId, ticker)
    VALUES(100, 35.03, 1, "AMD");

INSERT INTO PortfolioHistory(portfolioId, datetime, value)
    VALUES(1, DATE_SUB(CURDATE(), INTERVAL 2 DAY), 2950);
INSERT INTO PortfolioHistory(portfolioId, datetime, value)
    VALUES(1, DATE_SUB(CURDATE(), INTERVAL 1 DAY), 3000);
INSERT INTO PortfolioHistory(portfolioId, datetime, value)
    VALUES(1, NOW(), 3005);