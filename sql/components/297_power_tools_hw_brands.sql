INSERT INTO hardware_brand (name)
VALUES ('Black & Decker'),
       ('Bosch'),
       ('Craftsman'),
       ('DeWalt'),
       ('Festool'),
       ('Hitachi'),
       ('Makita'),
       ('Milwaukee'),
       ('Ryobi'),
       ('Stanley')
ON CONFLICT
    DO NOTHING;
