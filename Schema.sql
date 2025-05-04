-- Database
CREATE DATABASE IF NOT EXISTS social_media_analysis;
USE social_media_analysis;

-- SocialMedia
CREATE TABLE Social_Media (
    name VARCHAR(100) PRIMARY KEY
);

-- User
CREATE TABLE User (
    username VARCHAR(40),
    social_media VARCHAR(100),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    country_of_birth VARCHAR(100),
    country_of_residence VARCHAR(100),
    age INT,
    gender VARCHAR(20),
    is_verified BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (username, social_media),
    FOREIGN KEY (social_media) REFERENCES Social_Media(name)
);

-- Post
CREATE TABLE Post (
    post_username VARCHAR(40),
    post_social_media VARCHAR(100),
    post_time TIME,
    text TEXT,
    likes INT DEFAULT 0 CHECK(likes >= 0),
    dislikes INT DEFAULT 0 CHECK(dislikes >= 0),
    location_city VARCHAR(100),
    location_state VARCHAR(100),
    location_country VARCHAR(100),
    has_multimedia BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (post_username, post_social_media, post_time),
    FOREIGN KEY (post_username, post_social_media) REFERENCES User(username, social_media)
);

-- Repost
CREATE TABLE Repost (
    original_post_username VARCHAR(40),
    original_social_media VARCHAR(100),
    original_post_time TIME,
    repost_username VARCHAR(40),
    repost_social_media VARCHAR(100),
    repost_time TIME,
    repost_location_city VARCHAR(100),
    repost_location_state VARCHAR(100),
    repost_location_country VARCHAR(100),
    repost_likes INT DEFAULT 0,
    repost_dislikes INT DEFAULT 0,
    repost_has_multimedia BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (repost_username, repost_social_media, repost_time),
    FOREIGN KEY (original_post_username, original_social_media, original_post_time) 
        REFERENCES Post(post_username, post_social_media, post_time),
    FOREIGN KEY (repost_username, repost_social_media) 
        REFERENCES User(username, social_media)
);

-- Institute
CREATE TABLE Institute (
    name VARCHAR(200) PRIMARY KEY
);

-- Project
CREATE TABLE Project (
    name VARCHAR(200) PRIMARY KEY,
    manager_firstname VARCHAR(100),
    manager_lastname VARCHAR(100),
    institute_name VARCHAR(200),
    start_date DATE,
    end_date DATE,
    FOREIGN KEY (institute_name) REFERENCES Institute(name)
);

-- Field
CREATE TABLE Field (
    field_name VARCHAR(100),
    project_name VARCHAR(200),
    PRIMARY KEY (project_name, field_name),
    FOREIGN KEY (project_name) REFERENCES Project(name)
);

-- Project_Post
CREATE TABLE Project_Post (
    project_name VARCHAR(200),
    post_username VARCHAR(40),
    post_social_media VARCHAR(100),
    post_time TIME,
    PRIMARY KEY (project_name, post_username, post_social_media, post_time),
    FOREIGN KEY (project_name) REFERENCES Project(name),
    FOREIGN KEY (post_username, post_social_media, post_time) 
        REFERENCES Post(post_username, post_social_media, post_time)
);

-- Analysis_Result
CREATE TABLE Analysis_Result (
    project_name VARCHAR(200),
    post_username VARCHAR(40),
    post_social_media VARCHAR(100),
    post_time TIME,
    field_name VARCHAR(100),
    analysis TEXT,
    PRIMARY KEY (project_name, post_username, post_social_media, post_time, field_name),
    FOREIGN KEY (project_name, post_username, post_social_media, post_time) 
        REFERENCES Project_Post(project_name, post_username, post_social_media, post_time),
    FOREIGN KEY (project_name, field_name) 
        REFERENCES Field(project_name, field_name)
);