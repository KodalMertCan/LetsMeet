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

-- USER_LIKE  (neu: like_id PK, status statt text, keine conversation_id)
CREATE TABLE USER_LIKE (
    like_id     SERIAL PRIMARY KEY,
    sender_id   INT REFERENCES "USER"(id) ON DELETE SET NULL,
    receiver_id INT REFERENCES "USER"(id) ON DELETE SET NULL,
    timestamp   DATE,
    status      VARCHAR
);

-- HOBBY
CREATE TABLE HOBBY (
    hobby_id   SERIAL PRIMARY KEY,
    hobby_name VARCHAR(200) UNIQUE NOT NULL
);

-- HOBBY_PRIORITY
CREATE TABLE HOBBY_PRIORITY (
    user_id  INT NOT NULL REFERENCES "USER"(id) ON DELETE CASCADE,
    hobby_id INT NOT NULL REFERENCES HOBBY(hobby_id) ON DELETE CASCADE,
    priority VARCHAR(50) NOT NULL,
    PRIMARY KEY (user_id, hobby_id)
);

-- PHOTO  (neu: link TEXT)
CREATE TABLE PHOTO (
    photo_id   SERIAL PRIMARY KEY,
    user_id    INT NOT NULL REFERENCES "USER"(id) ON DELETE CASCADE,
    link       TEXT,
    created_at DATE DEFAULT CURRENT_DATE
);
