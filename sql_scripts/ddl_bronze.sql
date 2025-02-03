/*
===============================================================================
DDL Script: Create Bronze Tables
===============================================================================
Script Purpose:
    This script creates tables in the 'bronze' schema, dropping existing tables 
    if they already exist.
	  Run this script to re-define the DDL structure of 'bronze' Tables
===============================================================================
*/

CREATE TABLE IF NOT EXISTS bronze.rawdata_handelsbanken_transactions (
    transaction_id SERIAL PRIMARY KEY,
    posting_date DATE,
    transaction_date DATE NOT NULL,
    transaction_description TEXT,
    amount NUMERIC(10, 2) NOT NULL
);
