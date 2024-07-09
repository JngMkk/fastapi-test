DROP DATABASE IF EXISTS testdb;
CREATE DATABASE testdb;

USE testdb;

CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(320) UNIQUE NOT NULL,
    password VARCHAR(60) NOT NULL,
    is_disabled BOOLEAN DEFAULT FALSE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now() ON UPDATE now(),
    CONSTRAINT users_pkey PRIMARY KEY (id),
    CONSTRAINT users_email_ukey UNIQUE (email)
);

CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    title VARCHAR(30) NOT NULL,
    description VARCHAR(100),
    tags JSON,
    image VARCHAR(255),
    location VARCHAR(50),
    is_checked BOOLEAN DEFAULT FALSE,
    user_id VARCHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now() ON UPDATE now(),
    CONSTRAINT events_pkey PRIMARY KEY (id),
    CONSTRAINT users_id_fkey FOREIGN KEY (user_id)
        REFERENCES testdb.users (id)
        ON DELETE CASCADE
);