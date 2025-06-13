--how to add auto generation for column ID to a table after migration from SQLite to Postgre

--1) Create sequence to generate the IDs
CREATE SEQUENCE portfolio_id_seq;


--2) Alter the portfolio.id column to use this sequence:
ALTER TABLE portfolio 
ALTER COLUMN id SET DEFAULT nextval('portfolio_id_seq');

--3)Ensure sequence is in sync with existing data (to avoid conflicts):
SELECT setval('portfolio_id_seq', COALESCE((SELECT MAX(id) FROM portfolio), 1), true);

--4) Check the data:
select * from portfolio p order by p.id desc

-- Get the current value of the sequence (last assigned value)
SELECT last_value FROM portfolio_id_seq;

-- Get full details of the sequence (including whether nextval() was called)
SELECT * FROM portfolio_id_seq;

-- Get the next value from the sequence (this will increment the sequence)
SELECT nextval('portfolio_id_seq');

-- Get the current value without incrementing (only works after nextval() has been used in the session)
SELECT currval('portfolio_id_seq');
