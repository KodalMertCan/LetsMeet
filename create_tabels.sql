-- create_tables.sql (ERD v2)
-- USER, NACHRICHT, USER_LIKE, FRIEND_LIST, HOBBY, HOBBY_PRIORITY, PHOTO

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Clean rebuild (nur DEV)
DROP TABLE IF EXISTS PHOTO CASCADE;
DROP TABLE IF EXISTS HOBBY_PRIORITY CASCADE;
DROP TABLE IF EXISTS HOBBY CASCADE;
DROP TABLE IF EXISTS USER_LIKE CASCADE;
DROP TABLE IF EXISTS NACHRICHT CASCADE;
DROP TABLE IF EXISTS FRIEND_LIST CASCADE;
DROP TABLE IF EXISTS "USER" CASCADE;


-- USER
CREATE TABLE "USER" (
    id              SERIAL PRIMARY KEY,
    email           VARCHAR(255) NOT NULL UNIQUE,
    surname         VARCHAR(100),
    name            VARCHAR(100),
    gender          VARCHAR(30),
    birthdate       DATE,
    created_at      DATE DEFAULT CURRENT_DATE,
    updated_at      DATE DEFAULT CURRENT_DATE,
    gender_interest VARCHAR(100),
    phone_number    VARCHAR(100),
    street          VARCHAR(200),
    number          VARCHAR(50),
    zip             VARCHAR(20),
    city            VARCHAR(100)
);

-- FRIEND_LIST
CREATE TABLE FRIEND_LIST (
    user_id   INT NOT NULL REFERENCES "USER"(id) ON DELETE CASCADE,
    friend_id INT NOT NULL REFERENCES "USER"(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, friend_id)
);

-- NACHRICHT
CREATE TABLE NACHRICHT (
    message_id      SERIAL PRIMARY KEY,
    user_id         INT NOT NULL REFERENCES "USER"(id) ON DELETE CASCADE, -- Sender
    conversation_id INT,
    receiver_email  VARCHAR(255),
    text            VARCHAR,
    timestamp       DATE
);

-- USER_LIKE
CREATE TABLE USER_LIKE (
    message_id      SERIAL PRIMARY KEY,
    conversation_id INT,
    sender_id       INT REFERENCES "USER"(id) ON DELETE SET NULL,
    receiver_id     INT REFERENCES "USER"(id) ON DELETE SET NULL,
    text            VARCHAR,
    timestamp       DATE
);

-- HOBBY
CREATE TABLE HOBBY (
    hobby_id   SERIAL PRIMARY KEY,
    hobby_name VARCHAR(200) UNIQUE NOT NULL
);

-- HOBBY_PRIORITY (Priority als STRING/VARCHAR gemäß ERD)
CREATE TABLE HOBBY_PRIORITY (
    user_id  INT NOT NULL REFERENCES "USER"(id) ON DELETE CASCADE,
    hobby_id INT NOT NULL REFERENCES HOBBY(hobby_id) ON DELETE CASCADE,
    priority VARCHAR(50) NOT NULL,
    PRIMARY KEY (user_id, hobby_id)
);

-- PHOTO
CREATE TABLE PHOTO (
    photo_id   SERIAL PRIMARY KEY,
    user_id    INT NOT NULL REFERENCES "USER"(id) ON DELETE CASCADE,
    created_at DATE DEFAULT CURRENT_DATE
);

-- Indizes
CREATE INDEX IF NOT EXISTS idx_user_email ON "USER"(email);
CREATE INDEX IF NOT EXISTS idx_msg_sender_time ON NACHRICHT(user_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_like_sender_time ON USER_LIKE(sender_id, timestamp);

-- Trigger: updated_at automatisch setzen
CREATE OR REPLACE FUNCTION set_user_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = CURRENT_DATE;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_user_updated_at ON "USER";
CREATE TRIGGER trg_user_updated_at BEFORE UPDATE ON "USER"
FOR EACH ROW EXECUTE FUNCTION set_user_updated_at();