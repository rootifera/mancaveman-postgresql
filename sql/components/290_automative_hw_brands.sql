INSERT INTO hardware_brand (name)
VALUES ('Aisin'),
       ('Alpine'),
       ('Bilstein'),
       ('Borla'),
       ('Bosch'),
       ('Brembo'),
       ('Bridgestone'),
       ('Continental'),
       ('Denso'),
       ('Eibach'),
       ('Garrett'),
       ('Hella'),
       ('JL Audio'),
       ('K&N'),
       ('Kenwood'),
       ('Magna'),
       ('Michelin'),
       ('Pioneer'),
       ('Pirelli'),
       ('Recaro'),
       ('Sparco'),
       ('TEIN'),
       ('TurboXS'),
       ('Yokohama'),
       ('ZF Friedrichshafen')
ON CONFLICT
    DO NOTHING;
