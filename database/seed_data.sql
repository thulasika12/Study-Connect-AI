USE study_connect_ai;

INSERT INTO users (name, email, password_hash, role) VALUES
('Admin User', 'admin@studyconnect.ai', '$2b$12$KIXQoQOZ1o8f0G0h2q0aZOeYQm1z0Y5f5m5m5m5m5m5m5m5m5m5mO', 'admin'),

('Priya Sharma', 'priya.teacher@studyconnect.ai', '$2b$12$KIXQoQOZ1o8f0G0h2q0aZOeYQm1z0Y5f5m5m5m5m5m5m5m5m5m5mO', 'student'),

('Rahul Verma', 'rahul.student@studyconnect.ai', '$2b$12$KIXQoQOZ1o8f0G0h2q0aZOeYQm1z0Y5f5m5m5m5m5m5m5m5m5m5mO', 'student');


INSERT INTO study_groups (name, description, creator_id) VALUES
('Physics Warriors', 'Group for physics preparation and doubt discussion', 2),

('Data Structures Study Circle', 'Weekly DSA problem solving sessions', 3);


INSERT INTO group_members (group_id, user_id) VALUES
(1,2),
(1,3),
(2,3);