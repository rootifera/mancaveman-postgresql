INSERT INTO software_category (name)
VALUES ('Antivirus Software'),
       ('Audio Editing Software'),
       ('Business Software'),
       ('Cloud Computing Software'),
       ('Communication Tools'),
       ('Database Management'),
       ('Development Tools'),
       ('Educational Software'),
       ('Game'),
       ('Graphic Design Tools'),
       ('Medical Software'),
       ('Multimedia Software'),
       ('Network Management Software'),
       ('Operating System'),
       ('Productivity Suite'),
       ('Security Software'),
       ('Simulation Software'),
       ('Utility Software'),
       ('Video Editing Software') ON CONFLICT
    DO NOTHING;
