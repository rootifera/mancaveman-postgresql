INSERT INTO hardware_brand (name)
VALUES ('Atari'),
       ('Commodore'),
       ('Microsoft'),
       ('Neo Geo'),
       ('Nintendo'),
       ('Nvidia'),
       ('Oculus VR'),
       ('Sega'),
       ('Sony'),
       ('Valve')
ON CONFLICT
    DO NOTHING;
