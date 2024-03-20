INSERT INTO hardware_brand (name)
VALUES
       ('Akai'),
       ('Alesis'),
       ('Behringer'),
       ('Bose'),
       ('Casio'),
       ('Ernie Ball'),
       ('ESP Guitars'),
       ('Fender'),
       ('Gibson'),
       ('Ibanez'),
       ('Korg'),
       ('Marshall'),
       ('Martin Guitars'),
       ('Native Instruments'),
       ('Orange Amplification'),
       ('Pioneer DJ'),
       ('Roland'),
       ('Sennheiser'),
       ('Shure'),
       ('Steinberg'),
       ('Steinway'),
       ('Taylor Guitars'),
       ('Yamaha'),
       ('Zildjian')
ON CONFLICT
    DO NOTHING;
