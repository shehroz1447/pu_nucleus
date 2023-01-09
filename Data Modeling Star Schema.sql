-- Data Modeling - Star Schema
-- Snowflake

-- CREATE DIM AND FACT
CREATE TABLE DWH_DEMO.SALES_DWH.PRODUCT_DIM (
	PRO_ID VARCHAR(20) NOT NULL,
	PRO_NAME VARCHAR(20),
	EXPIRY_DATE DATE,
	primary key (PRO_ID)
);

CREATE TABLE DWH_DEMO.SALES_DWH.STORE_DIM (
	STO_ID VARCHAR(20) NOT NULL,
	STORE VARCHAR(20),
	ADDRESS VARCHAR(40),
    PHONE NUMBER(38,0),
	primary key (STO_ID)
);

CREATE TABLE DWH_DEMO.SALES_DWH.DATE_DIM (
	DT_ID VARCHAR(20) NOT NULL,
	DT DATE,
	WEATHER VARCHAR(20),
	primary key (DT_ID)
);

CREATE TABLE DWH_DEMO.SALES_DWH.CUSTOMER_DIM (
	CUS_ID VARCHAR(20) NOT NULL,
	NAME VARCHAR(20),
	AGE NUMBER(38,0),
	primary key (CUS_ID)
);

CREATE TABLE DWH_DEMO.SALES_DWH.SALE_FACT (
	SALE_ID VARCHAR(20) NOT NULL,
    SALE_PRICE NUMBER(38,0) NOT NULL, 
    PRO_ID VARCHAR(20) NOT NULL,
    STO_ID VARCHAR(20) NOT NULL,
    DT_ID VARCHAR(20) NOT NULL,
    CUS_ID VARCHAR(20) NOT NULL,
	primary key (SALE_ID, PRO_ID, STO_ID, DT_ID, CUS_ID),
    FOREIGN KEY (PRO_ID) REFERENCES PRODUCT_DIM(PRO_ID),
    FOREIGN KEY (STO_ID) REFERENCES STORE_DIM(STO_ID),
    FOREIGN KEY (DT_ID) REFERENCES DATE_DIM(DT_ID),
    FOREIGN KEY (CUS_ID) REFERENCES CUSTOMER_DIM(CUS_ID)
);

-- DROP TABLE DWH_DEMO.SALES_DWH.SALE_FACT

-- ADD INITIAL DATA
INSERT INTO DWH_DEMO.SALES_DWH.PRODUCT_DIM (PRO_ID, PRO_NAME, EXPIRY_DATE)
VALUES 
('pro001',	'yums',	to_date('23.03.2022', 'DD.MM.YYYY')),
('pro002',	'coke',	to_date('11.05.2022', 'DD.MM.YYYY')),
('pro003',	'sting', to_date('04.07.2022', 'DD.MM.YYYY')),
('pro004',	'lays',	to_date('31.05.2022', 'DD.MM.YYYY'));

INSERT INTO DWH_DEMO.SALES_DWH.STORE_DIM (STO_ID, STORE, ADDRESS, PHONE)
VALUES 
('st001',	'Soan',	'Main Commercial Plaza', 465137189),
('st002',	'Pwd',	'Main Bollevard Plaza', 61513527),
('st003',	'Bahria', 'Civic Centre', 851356817);

INSERT INTO DWH_DEMO.SALES_DWH.CUSTOMER_DIM (CUS_ID, NAME, AGE)
VALUES 
('cus001',	'Shehroz', 23),
('cus002',	'Awais', 18),
('cus003',	'Shams', 27),
('cus004',	'Awais', 17);

INSERT INTO DWH_DEMO.SALES_DWH.DATE_DIM (DT_ID, DT, WEATHER)
VALUES 
('dt001',to_date('01.03.2022', 'DD.MM.YYYY'),'Sunny'),
('dt002',to_date('02.03.2022', 'DD.MM.YYYY'),'Cloudy'),
('dt003',to_date('03.03.2022', 'DD.MM.YYYY'),'Sunny'),
('cus004',to_date('04.03.2022', 'DD.MM.YYYY'),'Rainy');

INSERT INTO DWH_DEMO.SALES_DWH.SALE_FACT (SALE_ID, SALE_PRICE, PRO_ID, STO_ID, DT_ID, CUS_ID)
VALUES 
('sa001',	20,	'pro001',	'st001',	'date001',	'cus002'),
('sa002',	50,	'pro002',	'st001',	'date001',	'cus002'),
('sa003',	60,	'pro003',	'st002',	'date002',	'cus001'),
('sa004',	10,	'pro004',	'st002',	'date002',	'cus001'),
('sa005',	10,	'pro004',	'st003',	'date002',	'cus004'),
('sa006',	50,	'pro002',	'st001',	'date003',	'cus003'),
('sa007',	20,	'pro001',	'st003',	'date003',	'cus004'),
('sa008',	10,	'pro004',	'st002',	'date003',	'cus001'),
('sa009',	10,	'pro004',	'st001',	'date004',	'cus002');

-- Total Money Earned by Coke Sales in Soan Store 
Select sum(sale_price) from sale_fact sf
join product_dim p
ON  p.pro_id = sf.pro_id
join store_dim s
ON s.sto_id = sf.sto_id
WHERE 
p.pro_name = 'coke' 
and
s.store = 'Soan';