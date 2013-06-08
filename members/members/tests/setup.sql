-- insert some needed data that the app does not generate by itself (in tests/base.py)

-- wh_order
BEGIN TRANSACTION;
CREATE TABLE wh_order (
    ord_no INTEGER NOT NULL, 
    ord_label VARCHAR(255),
    who_order_completed DATE, 
    PRIMARY KEY (ord_no, ord_label)
);
INSERT INTO "wh_order" VALUES(1,'May 2012', '2012-05-28 17:35:23');
INSERT INTO "wh_order" VALUES(2,'June 2012', '2012-06-27 17:35:23');
INSERT INTO "wh_order" VALUES(3,'July 2012', '2012-07-29 17:35:23');
INSERT INTO "wh_order" VALUES(4,'August 2012', '2012-08-30 17:35:23');
INSERT INTO "wh_order" VALUES(5,'September 2012', '2012-09-29 17:35:23');

-- order_header (not needed)
--CREATE TABLE order_header (ord_no integer NOT NULL, ord_label character varying NOT NULL);
--INSERT INTO "order_header" VALUES(1,'current_order');

-- shift descriptions
CREATE TABLE shift_days_descriptions (id int NOT NULL, descr varchar(255), PRIMARY KEY (id));
INSERT INTO shift_days_descriptions VALUES (0, 'any day');
INSERT INTO shift_days_descriptions VALUES (1, 'pick-up day');
INSERT INTO shift_days_descriptions VALUES (2, 'day before pick-up day');

CREATE TABLE wholesaler (
	wh_id INTEGER PRIMARY KEY, 
	wh_name VARCHAR(100), 
	wh_addr1 VARCHAR(50), 
	wh_addr2 VARCHAR(50), 
	wh_addr3 VARCHAR(50), 
	wh_city VARCHAR(50), 
	wh_postcode VARCHAR(10), 
	wh_tel VARCHAR(20), 
	wh_fax VARCHAR(20), 
        wh_active boolean DEFAULT true,
	wh_update VARCHAR(20)
);

INSERT INTO "wholesaler" VALUES(1,'DNB', '', '', '', 'Amsterdam', '', '', '', 1, '2012-11-29 17:35:23');
INSERT INTO "wholesaler" VALUES(2,'Zapatista', '', '', '', 'Hamburg', '', '', '', 1, '2012-11-29 17:35:23');
INSERT INTO "wholesaler" VALUES(3,'De Werkbij', '', '', '', 'Amsterdam', '', '', '', 1, '2012-11-29 17:35:23');

-- I don't know why this is not created automatically with 
-- models.base.Base.metadata.create_all(self.engine)
CREATE TABLE vers_suppliers (
	id INTEGER PRIMARY KEY, 
	name VARCHAR(100), 
	website VARCHAR(50), 
	email VARCHAR(50), 
	telnr VARCHAR(20), 
	faxnr VARCHAR(20),
        active boolean DEFAULT true, 
	comment VARCHAR(500) 
);

INSERT INTO "vers_suppliers" VALUES(1,'Geijtenboerderij', '', '', '', '', 1, '');
INSERT INTO "vers_suppliers" VALUES(2,'Boerderij B', '', '', '', '', 1, '');

COMMIT;
