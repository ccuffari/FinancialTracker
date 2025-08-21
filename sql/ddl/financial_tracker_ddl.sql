-- =====================================
-- FINANCIAL TRACKER DATABASE DDL
-- =====================================
-- Generato automaticamente il 2025-08-21 15:22:56
-- 
-- Questo script crea la struttura completa del database
-- per il Financial Tracker. La transazione è atomica:
-- o vengono create tutte le strutture o nessuna.
-- =====================================


BEGIN;

-- =====================================
-- CREAZIONE SCHEMI
-- =====================================

CREATE SCHEMA IF NOT EXISTS dates;
CREATE SCHEMA IF NOT EXISTS needs;
CREATE SCHEMA IF NOT EXISTS salaries;
CREATE SCHEMA IF NOT EXISTS savings;
CREATE SCHEMA IF NOT EXISTS wishes;

-- =====================================
-- CREAZIONE TABELLE
-- =====================================

-- Tabella: dates.dates
CREATE TABLE dates.dates (
    id DECIMAL(15,2),
    date VARCHAR(7) NOT NULL
,
    CONSTRAINT pk_dates_dates PRIMARY KEY (date)
);

-- Tabella: needs.cdc
CREATE TABLE needs.cdc (
    date VARCHAR(7) NOT NULL,
    installment DECIMAL(15,2),
    cdc_value DECIMAL(15,2)
,
    CONSTRAINT pk_needs_cdc PRIMARY KEY (date)
);

-- Tabella: needs.connections
CREATE TABLE needs.connections (
    date VARCHAR(7) NOT NULL,
    sim DECIMAL(15,2),
    internet DECIMAL(15,2),
    connection_value DECIMAL(15,2)
,
    CONSTRAINT pk_needs_connections PRIMARY KEY (date)
);

-- Tabella: needs.financials
CREATE TABLE needs.financials (
    date VARCHAR(7) NOT NULL,
    car_financial DECIMAL(15,2),
    car_gas DECIMAL(15,2),
    telephone_financial DECIMAL(15,2),
    financial_value DECIMAL(15,2)
,
    CONSTRAINT pk_needs_financials PRIMARY KEY (date)
);

-- Tabella: needs.fines
CREATE TABLE needs.fines (
    date VARCHAR(7) NOT NULL,
    fine DECIMAL(15,2),
    stamp DECIMAL(15,2),
    fines_value DECIMAL(15,2)
,
    CONSTRAINT pk_needs_fines PRIMARY KEY (date)
);

-- Tabella: needs.installments
CREATE TABLE needs.installments (
    date VARCHAR(7) NOT NULL,
    klarna DECIMAL(15,2),
    scalapay DECIMAL(15,2),
    cofidis DECIMAL(15,2),
    installment_value DECIMAL(15,2)
,
    CONSTRAINT pk_needs_installments PRIMARY KEY (date)
);

-- Tabella: needs.insurances
CREATE TABLE needs.insurances (
    date VARCHAR(7) NOT NULL,
    car_insurance DECIMAL(15,2),
    insurance_value DECIMAL(15,2)
,
    CONSTRAINT pk_needs_insurances PRIMARY KEY (date)
);

-- Tabella: needs.loans
CREATE TABLE needs.loans (
    date VARCHAR(7) NOT NULL,
    silvia_loan DECIMAL(15,2),
    mom_loan DECIMAL(15,2),
    dad_loan DECIMAL(15,2),
    andrea_loan DECIMAL(15,2),
    loan_value DECIMAL(15,2)
,
    CONSTRAINT pk_needs_loans PRIMARY KEY (date)
);

-- Tabella: needs.rents
CREATE TABLE needs.rents (
    date VARCHAR(7) NOT NULL,
    rent_value DECIMAL(15,2)
,
    CONSTRAINT pk_needs_rents PRIMARY KEY (date)
);

-- Tabella: salaries.salaries
CREATE TABLE salaries.salaries (
    date VARCHAR(7) NOT NULL,
    ral DECIMAL(15,2),
    gross_salary DECIMAL(15,2),
    net_salary DECIMAL(15,2),
    13th DECIMAL(15,2),
    salary_value DECIMAL(15,2)
,
    CONSTRAINT pk_salaries_salaries PRIMARY KEY (date)
);

-- Tabella: savings.savings
CREATE TABLE savings.savings (
    date VARCHAR(7) NOT NULL,
    ral DECIMAL(15,2),
    gross_salary DECIMAL(15,2),
    net_salary DECIMAL(15,2),
    13th DECIMAL(15,2),
    saving_value DECIMAL(15,2)
,
    CONSTRAINT pk_savings_savings PRIMARY KEY (date)
);

-- Tabella: wishes.beauty
CREATE TABLE wishes.beauty (
    date VARCHAR(7) NOT NULL,
    hair DECIMAL(15,2),
    profume DECIMAL(15,2),
    beauty_value DECIMAL(15,2)
,
    CONSTRAINT pk_wishes_beauty PRIMARY KEY (date)
);

-- Tabella: wishes.holidays
CREATE TABLE wishes.holidays (
    date VARCHAR(7) NOT NULL,
    flight DECIMAL(15,2),
    home DECIMAL(15,2),
    holidays_value DECIMAL(15,2)
,
    CONSTRAINT pk_wishes_holidays PRIMARY KEY (date)
);

-- Tabella: wishes.parties
CREATE TABLE wishes.parties (
    date VARCHAR(7) NOT NULL,
    Monday DECIMAL(15,2),
    Tuesday DECIMAL(15,2),
    Wednesday DECIMAL(15,2),
    Thursday DECIMAL(15,2),
    Friday DECIMAL(15,2),
    Saturday DECIMAL(15,2),
    Sunday DECIMAL(15,2),
    parties_value DECIMAL(15,2)
,
    CONSTRAINT pk_wishes_parties PRIMARY KEY (date)
);

-- Tabella: wishes.subscriptions
CREATE TABLE wishes.subscriptions (
    date VARCHAR(7) NOT NULL,
    cigars DECIMAL(15,2),
    Prime DECIMAL(15,2),
    Netflix DECIMAL(15,2),
    iCloud DECIMAL(15,2),
    ChatGPT DECIMAL(15,2),
    Nintendo DECIMAL(15,2),
    Microsoft DECIMAL(15,2),
    subscriptions_value DECIMAL(15,2)
,
    CONSTRAINT pk_wishes_subscriptions PRIMARY KEY (date)
);

-- =====================================
-- FOREIGN KEY CONSTRAINTS
-- =====================================

-- Foreign Key: salaries.salaries.date -> dates.dates.date
ALTER TABLE salaries.salaries
    ADD CONSTRAINT fk_salaries_salaries_date
    FOREIGN KEY (date)
    REFERENCES dates.dates (date)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;

-- Foreign Key: savings.savings.date -> dates.dates.date
ALTER TABLE savings.savings
    ADD CONSTRAINT fk_savings_savings_date
    FOREIGN KEY (date)
    REFERENCES dates.dates (date)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;

-- Foreign Key: needs.financials.date -> dates.dates.date
ALTER TABLE needs.financials
    ADD CONSTRAINT fk_needs_financials_date
    FOREIGN KEY (date)
    REFERENCES dates.dates (date)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;

-- Foreign Key: needs.insurances.date -> dates.dates.date
ALTER TABLE needs.insurances
    ADD CONSTRAINT fk_needs_insurances_date
    FOREIGN KEY (date)
    REFERENCES dates.dates (date)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;

-- Foreign Key: needs.rents.date -> dates.dates.date
ALTER TABLE needs.rents
    ADD CONSTRAINT fk_needs_rents_date
    FOREIGN KEY (date)
    REFERENCES dates.dates (date)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;

-- Foreign Key: needs.loans.date -> dates.dates.date
ALTER TABLE needs.loans
    ADD CONSTRAINT fk_needs_loans_date
    FOREIGN KEY (date)
    REFERENCES dates.dates (date)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;

-- Foreign Key: needs.fines.date -> dates.dates.date
ALTER TABLE needs.fines
    ADD CONSTRAINT fk_needs_fines_date
    FOREIGN KEY (date)
    REFERENCES dates.dates (date)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;

-- Foreign Key: needs.cdc.date -> dates.dates.date
ALTER TABLE needs.cdc
    ADD CONSTRAINT fk_needs_cdc_date
    FOREIGN KEY (date)
    REFERENCES dates.dates (date)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;

-- Foreign Key: needs.installments.date -> dates.dates.date
ALTER TABLE needs.installments
    ADD CONSTRAINT fk_needs_installments_date
    FOREIGN KEY (date)
    REFERENCES dates.dates (date)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;

-- Foreign Key: wishes.holidays.date -> dates.dates.date
ALTER TABLE wishes.holidays
    ADD CONSTRAINT fk_wishes_holidays_date
    FOREIGN KEY (date)
    REFERENCES dates.dates (date)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;

-- Foreign Key: wishes.subscriptions.date -> dates.dates.date
ALTER TABLE wishes.subscriptions
    ADD CONSTRAINT fk_wishes_subscriptions_date
    FOREIGN KEY (date)
    REFERENCES dates.dates (date)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;

-- Foreign Key: wishes.parties.date -> dates.dates.date
ALTER TABLE wishes.parties
    ADD CONSTRAINT fk_wishes_parties_date
    FOREIGN KEY (date)
    REFERENCES dates.dates (date)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;

-- Foreign Key: wishes.beauty.date -> dates.dates.date
ALTER TABLE wishes.beauty
    ADD CONSTRAINT fk_wishes_beauty_date
    FOREIGN KEY (date)
    REFERENCES dates.dates (date)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;

-- Foreign Key: needs.connections.date -> dates.dates.date
ALTER TABLE needs.connections
    ADD CONSTRAINT fk_needs_connections_date
    FOREIGN KEY (date)
    REFERENCES dates.dates (date)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;

-- =====================================
-- COMMIT TRANSAZIONE
-- =====================================
COMMIT;