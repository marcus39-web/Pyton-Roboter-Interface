CREATE DATABASE IF NOT EXISTS brainbot_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE brainbot_ai;

CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(64) NOT NULL UNIQUE,
    name VARCHAR(128) NOT NULL,
    description TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS samples (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    source VARCHAR(128) NOT NULL,
    distance_cm INT NOT NULL,
    safe_distance_cm INT NOT NULL,
    raw_payload JSON NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS predictions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    sample_id BIGINT NOT NULL,
    category_id INT NOT NULL,
    decision_text VARCHAR(128) NOT NULL,
    command_text VARCHAR(128) NOT NULL,
    confidence DECIMAL(5,4) NOT NULL DEFAULT 1.0,
    model_version VARCHAR(64) NOT NULL DEFAULT 'rule-v1',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_predictions_sample FOREIGN KEY (sample_id) REFERENCES samples(id) ON DELETE CASCADE,
    CONSTRAINT fk_predictions_category FOREIGN KEY (category_id) REFERENCES categories(id)
);

CREATE TABLE IF NOT EXISTS feedback (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    prediction_id BIGINT NOT NULL,
    is_correct BOOLEAN NOT NULL,
    corrected_category_id INT NULL,
    note TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_feedback_prediction FOREIGN KEY (prediction_id) REFERENCES predictions(id) ON DELETE CASCADE,
    CONSTRAINT fk_feedback_category FOREIGN KEY (corrected_category_id) REFERENCES categories(id)
);

INSERT INTO categories (code, name, description)
VALUES ('OBSTACLE', 'Hindernis', 'Abstand unter Sicherheitsgrenze')
ON DUPLICATE KEY UPDATE name = VALUES(name), description = VALUES(description);

INSERT INTO categories (code, name, description)
VALUES ('CLEAR', 'Freie Strecke', 'Abstand über Sicherheitsgrenze')
ON DUPLICATE KEY UPDATE name = VALUES(name), description = VALUES(description);
