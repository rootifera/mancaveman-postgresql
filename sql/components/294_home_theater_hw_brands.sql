INSERT INTO hardware_brand (name)
VALUES ('Bang & Olufsen'),
       ('Bose'),
       ('Bowers & Wilkins'),
       ('Denon'),
       ('Harman Kardon'),
       ('JBL'),
       ('Klipsch'),
       ('LG Electronics'),
       ('Onkyo'),
       ('Panasonic'),
       ('Philips'),
       ('Pioneer'),
       ('Polk Audio'),
       ('Samsung'),
       ('Sennheiser'),
       ('Sharp'),
       ('Sony'),
       ('TCL'),
       ('Vizio'),
       ('Yamaha')
ON CONFLICT
    DO NOTHING;
